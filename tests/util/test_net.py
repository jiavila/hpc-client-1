from src.util.net import prepare_search, add_system_log, cancel_job, load_user_id_whitelist
from src.util.defn import ConfigFileCast
import pytest

from flywheel import Client, Job

from unittest import mock

def test_load_user_id_whitelist():
    # Create a mock Flywheel client instance
    fw_mock = mock.Mock(spec=Client)

    # Create a mock group permissions
    group_perms = [
        mock.Mock(id='user1'),
        mock.Mock(id='user2'),
        mock.Mock(id='user3')
    ]
    fw_mock.get_group = mock.Mock()
    # Mock the get_group method to return the mock group permissions
    fw_mock.get_group.return_value = {'permissions': group_perms}

    # Call the function under test
    result = load_user_id_whitelist(fw_mock)

    # Assert the result is the list of user IDs
    assert result == ['user1', 'user2', 'user3']
    

def test_cancel_job():
    # Create a mock Flywheel client instance
    fw_mock = mock.Mock(spec=Client)
    fw_mock.modify_job = mock.Mock()

    # Create a mock job ID
    job_id = 'job123'

    # Call the function under test
    cancel_job(fw_mock, job_id)

    # Assert that the modify_job method was called with the correct arguments
    fw_mock.modify_job.assert_called_once_with(job_id, Job(state='cancelled'))


def test_add_system_log():
    # Create a mock Flywheel client instance
    fw_mock = mock.Mock(spec=Client)
    fw_mock.add_job_logs = mock.Mock()

    # Create a mock job ID and message
    job_id = 'job123'
    msg = 'System log message'

    # Call the function under test
    add_system_log(fw_mock, job_id, msg)

    # Assert that the add_job_logs method was called with the correct arguments
    fw_mock.add_job_logs.assert_called_once_with(job_id, [{'fd': -1, 'msg': msg + '\n\n'}])


def test_prepare_search_with_hold_engine():
    # Create a mock cast_config object
    cast_config = mock.Mock(spec=ConfigFileCast)
    cast_config.cast_on_tag = False
    cast_config.cast_gear_whitelist = ['some_gear']

    # Set use_hold_engine to True
    cast_config.use_hold_engine = True

    # Call the function under test
    result = prepare_search(cast_config)

    # Assert that the search syntax is correct
    assert result == 'state=running,gear_info.name=~some_gear'


def test_prepare_search_with_hpc_tag():
    # Create a mock cast_config object
    cast_config = mock.Mock()
    cast_config.cast_on_tag = True
    cast_config.cast_gear_whitelist = []

    # Set use_hold_engine to False
    cast_config.use_hold_engine = False

    # Call the function under test
    result = prepare_search(cast_config)

    # Assert that the search syntax is correct
    assert result == 'state=pending,tags=hpc'


def test_prepare_search_with_gear_whitelist():
    # Create a mock cast_config object
    cast_config = mock.Mock()
    cast_config.cast_on_tag = False
    cast_config.cast_gear_whitelist = ['gear1', 'gear2']

    # Set use_hold_engine to False
    cast_config.use_hold_engine = False

    # Call the function under test
    result = prepare_search(cast_config)

    # Assert that the search syntax is correct
    assert result == 'state=pending,gear_info.name=~gear1|gear2'


def test_prepare_search_with_invalid_config():
    # Create a mock cast_config object
    cast_config = mock.Mock()

    # Case 1: cast_on_tag and cast_gear_whitelist are both True
    cast_config.cast_on_tag = True
    cast_config.cast_gear_whitelist = ['gear1', 'gear2']

    # Set use_hold_engine to False
    cast_config.use_hold_engine = False

    # Call the function under test and expect a fatal error
    with pytest.raises(SystemExit):
        prepare_search(cast_config)

    # Case 2: cast_on_tag and cast_gear_whitelist are both False
    cast_config.cast_on_tag = False
    cast_config.cast_gear_whitelist = []

    # Set use_hold_engine to False
    cast_config.use_hold_engine = False

    # Call the function under test and expect a fatal error
    with pytest.raises(SystemExit):
        prepare_search(cast_config)
