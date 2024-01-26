import pytest
from src.util.defn import JobSettings
from pydantic import ValidationError

def test_job_settings_creation():
    job_settings_data = {
        'fw_id': '123',
        'singularity_debug': True,
        'singularity_writable': False,
        'ram': '8GB',
        'cpu': '4',
        'gpu': '1'
    }
    job_settings = JobSettings(**job_settings_data)
    
    assert job_settings.fw_id == '123'
    assert job_settings.singularity_debug == True
    assert job_settings.singularity_writable == False
    assert job_settings.ram == '8GB'
    assert job_settings.cpu == '4'
    assert job_settings.gpu == '1'

def test_job_settings_optional_values():
    job_settings_data = {
        'fw_id': '456',
        'singularity_debug': False,
        'singularity_writable': True,
        'gpu': None
    }
    job_settings = JobSettings(**job_settings_data)
    
    assert job_settings.fw_id == '456'
    assert job_settings.singularity_debug == False
    assert job_settings.singularity_writable == True
    assert job_settings.ram is None
    assert job_settings.cpu is None
    assert job_settings.gpu is None

def test_job_settings_invalid_data():
    with pytest.raises(ValueError, match='fw_id'):
        JobSettings()

    # JobSettings(fw_id='789', singularity_debug=False, singularity_writable=True, ram='invalid_value')