import pytest

from src_code import cluster
from src_code.util.frame import log
from tests.assets.job_sample import job, config


@pytest.mark.parametrize(
    "test_job, scheduler_type, expected_values",
    [
        (  # Check slurm default ram and cpu settings
            job,  # This job doesn't have any values
            "slurm",
            {"ram": '4G',
             "cpu": '1'}
        )
    ]

)
def test_determine_cpu_and_ram_settings(test_job, scheduler_type, expected_values):
    """

    """
    scheduler = cluster.from_scheduler(
        config=config,
        log=log,
        scheduler_type=scheduler_type)

    ram, cpu = scheduler.determine_cpu_and_ram_settings(test_job)

    assert ram == expected_values.get('ram')
