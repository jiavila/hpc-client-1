import inspect, os, subprocess, sys

from ..util import defn, frame
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
			c.command = ['echo', '{{script_path}}']

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
			fw_id = str(job.id),

			singularity_debug    = s_debug,
			singularity_writable = s_write,

			ram = None,
			cpu = None,
		)

	def determine_script_patch(self, job):
		"""
		Determine where the HPC script file will be placed.

		You probably do not need to change this.
		"""

		return os.path.join(self.config.paths.scripts_path, 'job-' + job.id + '.sh')

	def determine_log_patch(self, job):
		"""
		Determine where the HPC log file will be placed.

		You probably do not need to change this.
		"""

		return os.path.join(self.config.paths.hpc_logs_path, 'job-' + job.id + '.txt')

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

		self.log.info('Casting job to HPC...')
		t = frame.timer()

		try:
			self.execute(command, values.script_path)

		except (FileNotFoundError, subprocess.SubprocessError) as e:
			self.log.critical('Error executing command. Exec error follows:')
			frame.fatal(e)

		ms = str(frame.elapsed_ms(t))
		self.log.debug('Casted job in ' + ms + ' ms.')

	def determine_cpu_and_ram_settings(self, job) -> (str, str):
		# check if the Flywheel gear job has any scheduler settings
		self.log.info(
			"Checking gear job for `scheduler_ram` and `scheduler_cpu` settings."
		)
		scheduler_ram = (job.config['config']).get('scheduler_ram')
		scheduler_cpu = (job.config['config']).get('scheduler_cpu')
		self.log.debug(
			"Flywheel gear job scheduler_ram = '%s', scheduler_cpu = '%s'"
		)

		# If it doesn't, get these from the fw-cast/settings/cast.yml file.
		cast = self.config.cast
		if not scheduler_ram:  # assume it can be None or '' to handle cases where the gear doesn't and does have these properties
			self.log.info(
				"No `scheduler_ram` setting found in Flywheel gear job. Checking"
				"`settings/cast.yml` file."
			)
			scheduler_ram = cast.scheduler_ram
			self.log.debug(
				"cast.yml scheduler_ram = '%s'" % scheduler_ram
			)
		if not scheduler_cpu:
			self.log.info(
				"No `scheduler_cpu` setting found in Flywheel gear job. Checking"
				"`settings/cast.yml` file."
			)
			scheduler_cpu = cast.scheduler_cpu
			self.log.debug(
				"cast.yml scheduler_cpu = '%s'" % scheduler_cpu
			)

		# Format the ram and cpu settings per scheduler type. If these are still
		# 'None' or '', the default level will be set by in the scheduler formatter.
		if not scheduler_ram:
			self.log.info(
				"No `scheduler_ram` setting found in Flywheel gear job. Setting "
				"to scheduler default."
			)
		if not scheduler_cpu:
			self.log.info(
				"No `scheduler_cpu` setting found in Flywheel gear job. Setting "
				"to scheduler default."
			)
		self.log.debug(
			"scheduler_ram = '%s', scheduler_cpu = '%s' before formatting." %
			(scheduler_ram, scheduler_cpu)
		)
		return self.format_scheduler_ram_and_cpu_settings(
			scheduler_ram=scheduler_ram, scheduler_cpu=scheduler_cpu
		)

	@abstractmethod
	def format_scheduler_ram_and_cpu_settings(
		self, scheduler_ram: str, scheduler_cpu: str
	) -> (str, str):
		raise NotImplementedError


SCRIPT_TEMPLATE = inspect.cleandoc("""#!/bin/bash

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

""") + '\n\n'
