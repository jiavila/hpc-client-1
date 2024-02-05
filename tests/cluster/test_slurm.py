import re

from src.cluster.slurm import Slurm
from src.util import defn
import logging

log = logging
# TODO: Make this more graceful!
# cast = {}
# paths = {}
# creds = {}

# config= defn.Config(
# 		cast  = cast,
# 		paths = paths,
# 		creds = creds,
# 	)

SCRIPT_TEMPLATE = """
#!/bin/bash
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



from tests.assets.variables import  job, config

class TestSlurm:
    def test_set_config_defaults(self):
        slurm = Slurm(config, log)
        slurm.set_config_defaults()
        c = slurm.config.cast

        assert c.command == ["sbatch", "{{script_path}}"]
        assert c.command_script_stdin == False
        assert c.script == SCRIPT_TEMPLATE[1:]
        assert c.script_executable == True

    def test_determine_job_settings(self):
        slurm = Slurm(config, log)
        
        job_settings = slurm.determine_job_settings(job)

        assert job_settings.fw_id == str(job.id)
        assert job_settings.singularity_debug == False
        assert job_settings.singularity_writable == False
        assert job_settings.ram == "8G"
        assert job_settings.cpu == "8"
        assert job_settings.gpu is None

    def test_format_scheduler_ram_and_cpu_settings(self):
        slurm = Slurm(config, log)
        scheduler_ram = "8G"
        scheduler_cpu = "4"

        ram, cpu = slurm.format_scheduler_ram_and_cpu_settings(
            scheduler_ram, scheduler_cpu
        )

        assert ram == "8G"
        assert cpu == "4"
