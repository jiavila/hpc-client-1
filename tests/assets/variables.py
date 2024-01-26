"""

"""

import os
from copy import deepcopy
import flywheel
from pathlib import Path
import argparse

from src.util.frame import cmd_parser, prepare_config, load_yaml_settings
from src.util.defn import FlywheelJob

# -----------------------------------------------------------------------------
# Setup the default job for testing
# -----------------------------------------------------------------------------
jobs = []
job_dict = {
     'config': {'config': {'include_rating_widget': False,
                           'measurement': 'T1',
                           'save_derivatives': False,
                           'save_outputs': False,
                           'verbose_reports': True},
                'destination': {'id': '64a732ef0ffb0ba95c5c679f',
                                'type': 'acquisition'},
                'inputs': {'nifti': {'base': 'file',
                                     'hierarchy': {'id': '64a732ef0ffb0ba95c5c679f',
                                                   'type': 'acquisition'},
                                     'location': {'name': 'sub-13_T1w.nii.gz',
                                                  'path': '/flywheel/v0/input/nifti/sub-13_T1w.nii.gz'},
                                     'object': {'classification': {'Features': [],
                                                                   'Intent': [],
                                                                   'Measurement': ['T1']},
                                                'file_id': '64a732fba36314d6133805eb',
                                                'mimetype': 'application/octet-stream',
                                                'modality': 'MR',
                                                'origin': {'id': 'jesusavila@flywheel.io',
                                                           'type': 'user'},
                                                'size': 4888210,
                                                'tags': [],
                                                'type': 'nifti',
                                                'version': 1,
                                                'zip_member_count': None}}}},
     'destination': {'id': '64a732ef0ffb0ba95c5c679f', 'type': 'acquisition'},
     'gear_id': '64a734a17a38c4247c11ce7a',
     'gear_info': {'category': 'qa',
                   'id': '64a734a17a38c4247c11ce7a',
                   'name': 'mriqc',
                   'version': '0.7.0_0.15.1'},
     'id': '64b5bce63a2637356859bf8c',
     'inputs': [{'base': None,
                 'found': None,
                 'id': '64a732ef0ffb0ba95c5c679f',
                 'input': 'nifti',
                 'name': 'sub-13_T1w.nii.gz',
                 'type': 'acquisition'}],
     'origin': {'id': 'jesusavila@flywheel.io', 'type': 'user'},
     'previous_job_id': None,

     'state': 'running',
     'tags': ['hpc', 'mriqc']
}

job = FlywheelJob(**job_dict)
jobs.append(job)

# -----------------------------------------------------------------------------
# Create other jobs for testing other cases and schedulers
# -----------------------------------------------------------------------------
# Create a Flywheel job that has `scheduler_ram` and `scheduler_cpu` variables
# undefined as ''
job_ram_cpu_defined_empty = deepcopy(job_dict)
job_ram_cpu_defined_empty['config']['config']['scheduler_ram'] = ''
job_ram_cpu_defined_empty['config']['config']['scheduler_cpu'] = ''
job_ram_cpu_defined_empty = FlywheelJob(**job_ram_cpu_defined_empty)
jobs.append(job_ram_cpu_defined_empty)

# Create a Flywheel job that has `scheduler_ram` and `scheduler_cpu` variables
# defined for Slurm
job_ram_cpu_defined_slurm = deepcopy(job_dict)
job_ram_cpu_defined_slurm['config']['config']['scheduler_ram'] = '16G'
job_ram_cpu_defined_slurm['config']['config']['scheduler_cpu'] = '4'
job_ram_cpu_defined_slurm = FlywheelJob(**job_ram_cpu_defined_slurm)
jobs.append(job_ram_cpu_defined_slurm)

# Create a Flywheel job that has `scheduler_ram` and `scheduler_cpu` variables
# defined for lsf
job_ram_cpu_defined_lsf = deepcopy(job_dict)
job_ram_cpu_defined_lsf['config']['config']['scheduler_ram'] = 'rusage[mem=5000]'
job_ram_cpu_defined_lsf['config']['config']['scheduler_cpu'] = '2'
job_ram_cpu_defined_lsf = FlywheelJob(**job_ram_cpu_defined_lsf)
jobs.append(job_ram_cpu_defined_lsf)

# Create a Flywheel job that has `scheduler_ram` and `scheduler_cpu` variables
# defined for sge
job_ram_cpu_defined_sge = deepcopy(job_dict)
job_ram_cpu_defined_sge['config']['config']['scheduler_ram'] = '10G'
job_ram_cpu_defined_sge['config']['config']['scheduler_cpu'] = '2-4'
job_ram_cpu_defined_sge = FlywheelJob(**job_ram_cpu_defined_sge)
jobs.append(job_ram_cpu_defined_sge)

# Create a Flywheel job that has `slurm-ram` and `slurm` variables
# undefined as ''
job_slurm_ram_cpu_defined_empty = deepcopy(job_dict)
job_slurm_ram_cpu_defined_empty['config']['config']['slurm-ram'] = ''
job_slurm_ram_cpu_defined_empty['config']['config']['slurm-cpu'] = ''
job_slurm_ram_cpu_defined_empty = FlywheelJob(**job_slurm_ram_cpu_defined_empty)
jobs.append(job_slurm_ram_cpu_defined_empty)

# Create a Flywheel job that has `slurm-ram` and `slurm-cpu` variables defined
# for slurm
job_slurm_ram_cpu_defined_slurm = deepcopy(job_dict)
job_slurm_ram_cpu_defined_slurm['config']['config']['slurm-ram'] = '12G'
job_slurm_ram_cpu_defined_slurm['config']['config']['slurm-cpu'] = '6'
job_slurm_ram_cpu_defined_slurm = FlywheelJob(**job_slurm_ram_cpu_defined_slurm)
jobs.append(job_slurm_ram_cpu_defined_slurm)

# -----------------------------------------------------------------------------
# Set up the config and log for the scheduler objects. All these are necessary
# to instantiate a scheduler object (children of Base in
# `src/cluster/base.py`
# -----------------------------------------------------------------------------
# set some env variables
os.environ['SCITRAN_RUNTIME_HOST'] = 'latest.sse.flywheel.io'
os.environ['SCITRAN_RUNTIME_PORT'] = '443'
os.environ['SCITRAN_CORE_DRONE_SECRET'] = ''

# TODO: Create a temporary folder with settings and logs... symlink in here
arg_dict = {
    "folder": Path(__file__).parent,
    "show_match": False,
    "show_config": False,
}
args = argparse.Namespace(**arg_dict)
# args = cmd_parser().parse_args()
# Handle running the pytest from Pycharm's debugger or from the command line
script_directory = Path(__file__).parent
# print(script_directory)
if os.path.split(script_directory)[-1] == "assets":
    args.folder = os.path.split(os.path.split(script_directory)[0])[0]  # manually set the base folder to the project, 2 folders up
elif os.path.exists(os.path.join(script_directory, "tests")):  # we're already in the project directory
    args.folder = script_directory
else:
    raise ValueError(
        "Cannot determine correct absolute path to main project folder."
    )
# print("args.folder: %s" % args.folder)

# Create config fucntions to make varieties b/c deepcopy not working
def create_config(args):

    config = prepare_config(args)
    # change cast so that it loads from tests/assets/cast.yml
    config.cast = load_yaml_settings(os.path.join(args.folder, 'tests/assets/cast.yml')).cast
    config.sdk = flywheel.Client()
    return config


config = create_config(args=args)

# Create config where ram and cpu are empty
config_no_ram_no_cpu = create_config(args=args)
config_no_ram_no_cpu.cast.scheduler_cpu = ''
config_no_ram_no_cpu.cast.scheduler_ram = ''
