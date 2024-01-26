import re

from .base import Base
from util import defn


class Slurm(Base):
    def set_config_defaults(self):
        c = self.config.cast

        if c.command is None:
            c.command = ["sbatch", "{{script_path}}"]

        if c.command_script_stdin is None:
            c.command_script_stdin = False

        if c.script is None:
            c.script = SCRIPT_TEMPLATE

        if c.script_executable is None:
            c.script_executable = True

    def determine_job_settings(self, job):
        s_debug, s_write = self.determine_singularity_settings(job)

        ram, cpu = self.determine_ram_and_cpu_settings(job=job)

        # This setting can be modified to account for multiple GPUs per node
        # For now, we will assume that a job will only request one GPU
        if "gpu" in job.tags:
            gpu = "1"
        else:
            gpu = None

        return defn.JobSettings(
            fw_id=str(job.id),
            singularity_debug=s_debug,
            singularity_writable=s_write,
            ram=ram,
            cpu=cpu,
            gpu=gpu,
        )

    def format_scheduler_ram_and_cpu_settings(
        self, scheduler_ram: str, scheduler_cpu: str
    ) -> (str, str):
        if not scheduler_ram:
            scheduler_ram = "4G"
        if not scheduler_cpu:
            scheduler_cpu = "1"
        # Force string and alphanum
        ram = re.sub(r"\W+", "", str(scheduler_ram))
        cpu = re.sub(r"\W+", "", str(scheduler_cpu))
        return ram, cpu


SCRIPT_TEMPLATE = """#!/bin/bash
#SBATCH --job-name=fw-{{job.fw_id}}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={{job.cpu}}
#SBATCH --mem-per-cpu={{job.ram}}
#SBATCH --output {{script_log_path}}

set -euo pipefail

source "{{cast_path}}/settings/credentials.sh"
cd "{{engine_run_path}}"

set -x
srun ./engine run --single-job {{job.fw_id}}

"""
