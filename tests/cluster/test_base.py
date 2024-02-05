import pytest

from src import cluster
from src.util.frame import log
from tests.assets.variables import jobs, config, config_no_ram_no_cpu


@pytest.mark.parametrize(
    "test_job, scheduler_type, config_setting, expected_values",
    [
        (
            # Check slurm default ram and cpu settings from the formatting
            # method.  This means that these are not set in the job and the
            # cast.yml file
            jobs[0],  # This job doesn't have any values
            "slurm",
            config_no_ram_no_cpu,
            {
                "ram": '4G',
                "cpu": '1'
            }
        ),
        (
            # Check lsf default ram and cpu settings from the formatting
            # method.
            jobs[0],  # This job doesn't have any values
            "lsf",
            config_no_ram_no_cpu,
            {
                "ram": 'rusage[mem=4000]',
                "cpu": '1'
            }
        ),
        (
            # Check sge default ram and cpu settings from the formatting
            # method.
            jobs[0],  # This job doesn't have any values
            "sge",
            config_no_ram_no_cpu,
            {
                "ram": '4G',
                "cpu": '4-8'
            }
        ),
        (  # Check slurm settings from the test cast.yml file.
            jobs[0],
            "slurm",
            config,
            {
                "ram": '8G',
                "cpu": '8'
            }
        ),
        (
            # Check slurm settings from the Flywheel job. These will be empty
            # strings, so we should get the default values from the cast.yml
            # file again.
            jobs[1],
            "slurm",
            config,
            {
                "ram": '8G',
                "cpu": '8'
            }
        ),
        (
            # Check slurm settings from the Flywheel job. These settings should
            # be successfully gotten from the job, since they're defined there.
            jobs[2],
            "slurm",
            config,
            {
                "ram": '16G',
                "cpu": '4'
            }
        ),
        (
            # Check lsf settings from the Flywheel job. These settings should
            # be successfully gotten from the job, since they're defined there.
            jobs[3],
            "lsf",
            config,
            {
                "ram": 'rusage[mem=5000]',
                "cpu": '2'
            }
        ),
        (
            # Check sge settings from the Flywheel job. These settings should
            # be successfully gotten from the job, since they're defined there.
            jobs[4],
            "sge",
            config,
            {
                "ram": '10G',
                "cpu": '2-4'
            }
        ),
        (
            # Check empty ('') legacy slurm-ram and slurm-cpu settings from the
            # Flywheel job. These should default to the slurm setting.
            jobs[5],
            "slurm",
            config_no_ram_no_cpu,
            {
                "ram": '4G',
                "cpu": '1'
            }
        ),
        (
            # Check defined legacy slurm-ram and slurm-cpu settings from the
            # Flywheel job. These should be set to what the job configs.
            jobs[6],
            "slurm",
            config_no_ram_no_cpu,
            {
                "ram": '12G',
                "cpu": '6'
            }
        )
    ]

)
def test_determine_ram_and_cpu_settings(
    test_job,
    scheduler_type,
    config_setting,
    expected_values
):
    scheduler = cluster.from_scheduler(
        config=config_setting,
        log=log,
        scheduler_type=scheduler_type)

    ram, cpu = scheduler.determine_ram_and_cpu_settings(test_job)

    assert ram == expected_values['ram']
    assert cpu == expected_values['cpu']


@pytest.mark.parametrize(
    "scheduler_type, scheduler_ram, scheduler_cpu, expected_values",
    [
        (
            # Check slurm default ram and cpu settings from the formatting
            # method.
            "slurm",
            '',
            '',
            {
                "ram": '4G',
                "cpu": '1'
            }
        ),
        (  # Check slurm settings from the cast.yml file. the `settings` folder
            # has to exists (i.e., `./process/setup.sh` must be run)
            "slurm",
            '8G',
            '8',
            {
                "ram": '8G',
                "cpu": '8'
            }
        ),
        (
            # Check slurm settings for default None values.
            "slurm",
            None,
            None,
            {
                "ram": '4G',
                "cpu": '1'
            }
        ),
        (
            # Check lsf default settings.
            "lsf",
            None,
            None,
            {
                "ram": 'rusage[mem=4000]',
                "cpu": '1'
            }
        ),
        (
            # Check sge default settings.
            "sge",
            None,
            None,
            {
                "ram": '4G',
                "cpu": '4-8'
            }
        )
    ]

)
def test_format_scheduler_ram_and_cpu_settings(
    scheduler_type: str,
    scheduler_ram: str,
    scheduler_cpu: str,
    expected_values: dict,
):
    scheduler = cluster.from_scheduler(
        config=config,
        log=log,
        scheduler_type=scheduler_type)

    ram, cpu = scheduler.format_scheduler_ram_and_cpu_settings(
        scheduler_ram=scheduler_ram,
        scheduler_cpu=scheduler_cpu
    )

    assert ram == expected_values['ram']
    assert cpu == expected_values['cpu']