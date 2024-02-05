import inspect, os, subprocess, sys
import flywheel

from util import defn, frame
from .common import Common
from abc import abstractmethod


class Base(Common):
    """
    BaseCluster defines methods that you may need to override.
    """

    def set_config_defaults(self):
        """
        Use this function to set cluster defaults.
        These will be used when the corresponding YAML value is not present.
        """

        c = self.config.cast

        if c.command is None:
            c.command = ["echo", "{{script_path}}"]

        if c.command_script_stdin is None:
            c.command_script_stdin = False

        if c.script is None:
            c.script = SCRIPT_TEMPLATE

        if c.script_executable is None:
            c.script_executable = False

    def determine_job_settings(self, job):
        """
        Parse job settings out of a FW job object.

        You will need to override this for cluster-specific config naming. This
        is also your opportunity to apply defaults for users who forget to
        specify the relevant options in their gear's manifest.

        Important: Security-sensitive.
        These values will be passed to command and script templating.
        """

        # These value names are not cluster-specific.
        # Use this function call when overriding.
        s_debug, s_write = self.determine_singularity_settings(job)

        # For this Base impl, no extra settings are defined.
        # Your cluster type might support these; override this function and add them.

        return defn.JobSettings(
            fw_id=str(job.id),
            singularity_debug=s_debug,
            singularity_writable=s_write,
            ram=None,
            cpu=None,
        )

    def determine_script_patch(self, job):
        """
        Determine where the HPC script file will be placed.

        You probably do not need to change this.
        """

        return os.path.join(self.config.paths.scripts_path, "job-" + job.id + ".sh")

    def determine_log_patch(self, job):
        """
        Determine where the HPC log file will be placed.

        You probably do not need to change this.
        """

        return os.path.join(self.config.paths.hpc_logs_path, "job-" + job.id + ".txt")

    def execute(self, command, script_path):
        # Prevent out-of-order log entries
        sys.stdout.flush()
        sys.stderr.flush()

        # Execute
        if not self.config.cast.command_script_stdin:
            subprocess.run(command, check=True)
        else:
            # Some commands, such as bsub, prefer to be fed via stdin
            handle = open(script_path)
            subprocess.run(command, stdin=handle, check=True)
            handle.close()

    def handle_each(self, job, values):
        """
        Handle a single job.

        Override if the general pattern of "generate script, run command" does not work for your cluster type.
        """

        script_text, command = self.run_templating(job, values)

        self.log.info("Casting job to HPC...")
        t = frame.timer()

        try:
            self.execute(command, values.script_path)

        except (FileNotFoundError, subprocess.SubprocessError) as e:
            self.log.critical("Error executing command. Exec error follows:")
            frame.fatal(e)

        ms = str(frame.elapsed_ms(t))
        self.log.debug("Casted job in " + ms + " ms.")

    def handle_all(self, start):
        """
        Main handler loop.
        """

        # Note: some functions are defined in BaseCluster:
        #
        #   determine_job_settings
        #   determine_script_patch
        #   handle_each
        #   set_config_defaults
        #
        # As such, using a Common class directly is invalid.

        # Load any cluster-specific settings
        self.set_config_defaults()
        self.confirm_config_defaults_loaded()

        # Load candidate jobs into memory
        self.log.debug('Looking for jobs to cast...')
        t = frame.timer()
        jobs = self.get_jobs()
        ms = str(frame.elapsed_ms(t))
        count = str(len(jobs))
        self.log.debug('Found ' + count + ' jobs in ' + ms + ' ms.')

        # Track results
        jobs_launched = 0
        jobs_skipped  = 0
        jobs_rejected = 0

        # Invoke cluster-specific logic
        for job in jobs:

            # Cast uses the existence of a script file
            # to determine if a job should be cast.
            script_path = self.determine_script_patch(job)

            if os.path.exists(script_path):
                jobs_skipped += 1
                continue

            if not self.check_whitelist(job):
                jobs_rejected += 1
                continue

            # Collect information
            script_log_path = self.determine_log_patch(job)
            job_settings    = self.determine_job_settings(job)

            # Prepare templating values
            values = defn.ScriptTemplate(
                job             = job_settings,
                script_path     = script_path,
                script_log_path = script_log_path,
                cast_path       = self.config.paths.cast_path,
                engine_run_path = self.config.paths.engine_run_path,
            )

            # Job is fit to cast
            self.handle_each(job, values)
            jobs_launched += 1

        # Finish
        self.report_results(start, jobs_launched, jobs_skipped, jobs_rejected)

    def determine_ram_and_cpu_settings(self, job: flywheel.JobListEntry) -> (str, str):
        """
        Returns the scheduler ram and cpu settings based on the type of
        cluster/HPC scheduler.

        Returns
        -------
        ram: str
        cpu: str
        """
        # Update job config vars to support legacy ram and cpu settings
        job = self._check_legacy_ram_and_cpu_settings(job=job)

        # Set the dict variables we're checking
        settings = {"scheduler_ram": "", "scheduler_cpu": ""}
        self._determine_scheduler_settings(job=job, settings=settings)
        return self.format_scheduler_ram_and_cpu_settings(**settings)

    def _check_legacy_ram_and_cpu_settings(self, job: flywheel.JobListEntry):
        """
        Supports legacy ram and cpu settings for `slurm-ram` and `slurm-cpu`
        by setting the value of these to `scheduler_ram` and `scheduler_cpu`.

        These should be deprecated in next major release (3.0.0). Warn user
        to update their gears to `scheduler_ram` and `scheduler_cpu`.

        Returns
        -------
        job: flywheel.JobListEntry
        """
        # Check if these variables exist in the Flywheel job config. These
        # appear as strings, even if unset ('')
        if isinstance((job.config["config"]).get("slurm-ram"), str) or isinstance(
            (job.config["config"]).get("slurm-cpu"), str
        ):
            # ensure that supported ones aren't also defined.
            if isinstance(
                (job.config["config"]).get("scheduler_ram"), str
            ) or isinstance((job.config["config"]).get("scheduler_cpu"), str):
                raise ValueError(
                    "Legacy variables `slurm-ram` and `slurm-cpu` cannot exist"
                    "with `scheduler_ram` and `scheduler_cpu`. Please remove "
                    "legacy settings."
                )

            # transform legacy vars to supported ones
            (job.config["config"])["scheduler_ram"] = (job.config["config"]).get(
                "slurm-ram"
            )
            (job.config["config"])["scheduler_cpu"] = (job.config["config"]).get(
                "slurm-cpu"
            )

            self.log.warning(
                "Support for variables `slurm-ram` and `slurm-cpu` will be "
                "deprecated in future releases. Please update these to"
                "`scheduler_ram` and `scheduler_cpu`. You cannot have both "
                "legacy and current names defined within the same gear job "
                "config."
            )
            return job
        else:
            return job

    def _determine_scheduler_settings(self, job: flywheel.JobListEntry, settings: dict):
        """
        A template method for checking a scheduler setting(s). This should be
        used in other methods that follow this logic:

        1. Check if the setting is in the Flywheel gear config.
        2. If not, check if the setting is in the `settings/cast.yml` file.
        3. If not, then set it to default values, typically set by a concrete
                cluster/scheduler object's formatting method.

        As an example, see `Base.determine_ram_and_cpu_settings().

        Args
        ----
        job: flywheel.JobListEntry
        settings: dict
                Each key represents a scheduler/cluster setting that should be
                checked in the processed described above. The default key should
                be something that represents an empty object (e.g., '', or None).

        Returns
        -------
        settings: dict
        """
        for setting in settings:
            # check if the Flywheel gear job has any scheduler settings
            self.log.info("Checking gear job for `%s` setting.")
            settings[setting] = (job.config["config"]).get(setting)
            self.log.info(
                "Flywheel gear job `%s` = '%s'" % (setting, settings[setting])
            )

            # If it doesn't, get these from the fw-cast/settings/cast.yml file.
            cast = self.config.cast
            if not settings[
                setting
            ]:  # assume it can be None or '' to handle cases where the gear doesn't and does have these properties
                self.log.info(
                    "No `%s` setting found in Flywheel gear job. Checking "
                    "`settings/cast.yml` file" % setting
                )
                settings[setting] = getattr(cast, setting)
                self.log.info("cast.yml %s = '%s'" % (setting, settings[setting]))

            # If these are still 'None' or '', the default level will be set by
            # the scheduler formatter.
            if not settings[setting]:
                self.log.info(
                    "No `%s` setting found in Flywheel cast.yml. Setting "
                    "to scheduler default." % setting
                )

            self.log.debug(
                "%s = '%s' before formatting." % (setting, settings[setting])
            )
        return settings

    @abstractmethod
    def format_scheduler_ram_and_cpu_settings(
        self, scheduler_ram: str, scheduler_cpu: str
    ) -> (str, str):
        raise NotImplementedError


SCRIPT_TEMPLATE = (
    inspect.cleandoc(
        """#!/bin/bash

echo "This is an example script. Hello world!!"
echo
echo "The FW job ID is {{job.fw_id}}"
echo
{%- if job.cpu -%}echo "Job CPU is set to {{job.cpu}}"{%- endif %}
{%- if job.ram -%}echo "Job RAM is set to {{job.ram}}"{%- endif %}

echo
echo "This file will be written to"
echo "{{script_path}}"

echo "The log will be written to"
echo "{{script_log_path}}"

"""
    )
    + "\n\n"
)
