from src.cluster.common import Common

from unittest.mock import Mock, patch
import pytest

from src.cluster.common import Common, net
from src.util.defn import ScriptTemplate, JobSettings

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

class TestCommon:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """
        Set up the test case.
        """
        self.config = Mock()
        self.config.cast = Mock()
        self.config.cast.dict.return_value = {
            'command': 'some_command',
            'command_script_stdin': 'some_command_script_stdin',
            'script': 'some_script',
            'script_executable': 'some_script_executable'
        }
        self.config.cast.filter = 'some_filter'
        self.config.cast.cast_on_tag = True
        self.config.cast.cast_gear_whitelist = []
        self.config.paths.cast_path = '/path/to/cast'
        self.config.paths.engine_run_path = '/path/to/engine_run'
        self.config.sdk = Mock()
        self.log = Mock()
        self.common = Common(self.config, self.log)
        self.common.uid_whitelist = None
        self.common.config.cast.group_whitelist = True

    def test_confirm_config_defaults_loaded(self):
        self.common.confirm_config_defaults_loaded()

        assert self.config.cast.dict.call_count == 4
        self.log.fatal.assert_not_called()

    def test_get_jobs(self):

        self.jobs = [Mock(), Mock()]
        self.config.sdk.jobs.iter_find.return_value = iter(self.jobs)

        result = self.common.get_jobs()

        assert result == self.jobs
        self.config.sdk.jobs.iter_find.assert_called_once_with(filter='state=running,tags=hpc')
        self.log.debug.assert_not_called()

    def test_determine_singularity_settings(self):
        job = Mock()
        job.config = {
            'singularity-debug': True,
            'singularity-writable': False
        }

        result = self.common.determine_singularity_settings(job)

        assert result == (True, False)
        self.log.warn.assert_not_called()

    def test_determine_singularity_settings_invalid_types(self):
        job = Mock()
        job.config = {
            'singularity-debug': 'true',
            'singularity-writable': 123
        }

        result = self.common.determine_singularity_settings(job)

        assert result == (False, False)
        self.log.warn.assert_called_with('Invalid singularity-writable type on job. Ignoring.')
   
    @patch("src.cluster.common.net.load_user_id_whitelist")
    def test_load_whitelist(self, mock_load_user_id_whitelist):
        mock_load_user_id_whitelist.return_value = ['user1', 'user2']

        self.common.load_whitelist()

        net.load_user_id_whitelist.assert_called_once_with(self.common.fw)
        assert self.common.uid_whitelist == ['user1', 'user2']
        self.common.log.warn.assert_not_called()

    @patch("src.cluster.common.net.load_user_id_whitelist")
    def test_load_whitelist_empty(self, mock_load_user_id_whitelist):
        mock_load_user_id_whitelist.return_value = []

        self.common.load_whitelist()

        net.load_user_id_whitelist.assert_called_once_with(self.common.fw)
        assert self.common.uid_whitelist == []
        self.common.log.warn.assert_called_once_with('HPC whitelist is active, but empty! No jobs will run.')


    @patch("src.cluster.common.net.add_system_log")
    @patch("src.cluster.common.net.cancel_job")
    def test_reject_whitelist(self, mock_cancel_job, mock_add_system_log):
        job = Mock()
        job.id = 'job123'
        job_user = 'user1'

        mock_add_system_log.return_value = None

        self.config.cast.admin_contact_email = 'admin@example.com'

        self.common.reject_whitelist(job, job_user)

        self.log.warn.assert_called_once_with('User user1 is not on the HPC whitelist. Dropping job.')

        expected_msg = (
            'User user1 is not on the HPC whitelist.\nOnly white-listed users are '
            'allowed to run Gears on the HPC at this time.\nFor more information '
            f'please contact {self.config.cast.admin_contact_email}')
        mock_add_system_log.assert_called_once_with(self.config.sdk, job.id, expected_msg)
        mock_cancel_job.assert_called_once_with(self.config.sdk, job.id)
        self.log.debug.assert_called_once()    
    
    @patch("src.cluster.common.net.load_user_id_whitelist")
    def test_check_whitelist(self, mock_load_user_id_whitelist):
        job = Mock()
        job.origin = Mock()
        job.origin.type = 'user'
        job.origin.id = 'user1'
        self.common.reject_whitelist = Mock()

        mock_load_user_id_whitelist.return_value = ['user1', 'user2']

        self.common.load_whitelist()

        result = self.common.check_whitelist(job)

        assert result is True
        self.common.reject_whitelist.assert_not_called()

    @patch("src.cluster.common.net.load_user_id_whitelist")
    def test_check_whitelist_reject(self, mock_load_user_id_whitelist):
        job = Mock()
        job.origin = Mock()
        job.origin.type = 'user'
        job.origin.id = 'user3'

        mock_load_user_id_whitelist.return_value = ['user1', 'user2']
        self.common.reject_whitelist = Mock()
        self.common.load_whitelist()

        result = self.common.check_whitelist(job)

        assert result is False
        self.common.reject_whitelist.assert_called_once_with(job, 'user3')


    @patch("builtins.open")
    def test_run_templating(self, mock_open):
        job = Mock()
        job.id = 'job123'
        job_settings    = JobSettings(
            fw_id=str(job.id),
            singularity_debug=False,
            singularity_writable=False,
            ram="4G",
            cpu="4",
        )
        values = ScriptTemplate(
                job             = job_settings,
                script_path     = "/path/to/script.sh",
                script_log_path = "/path/to/script.log",
                cast_path       = self.config.paths.cast_path,
                engine_run_path = self.config.paths.engine_run_path,
            )

        self.config.cast.show_script_template_values = True
        self.config.cast.script = SCRIPT_TEMPLATE
        self.config.cast.show_script_template_result = True
        self.config.cast.script_executable = False
        self.config.cast.command = ['command1', 'command2']
        self.config.cast.dry_run = True
        self.config.cast.show_commnd_template_result = True

        expected_script_text = (
            "\n#!/bin/bash\n"
            "#SBATCH --job-name=fw-job123\n"
            "#SBATCH --ntasks=1\n"
            "#SBATCH --cpus-per-task=4\n"
            "#SBATCH --mem-per-cpu=4G\n"
            "#SBATCH --output /path/to/script.log\n\n"
            "set -euo pipefail\n\n"
            "source \"/path/to/cast/settings/credentials.sh\"\n"
            "cd \"/path/to/engine_run\"\n\n"
            "set -x\n"
            "srun ./engine run --single-job job123\n"
        )
        expected_command = ['echo', 'command1', 'command2']

        mock_handle = mock_open.return_value
        self.common.log.debug.reset_mock()

        result_script_text, result_command = self.common.run_templating(job, values)

        assert result_script_text == expected_script_text
        assert result_command == expected_command
        mock_open.assert_called_once_with('/path/to/script.sh', 'w')
        mock_handle.write.assert_called_once_with(expected_script_text)
        mock_handle.close.assert_called_once()


    def test_report_results(self):
        start = 0
        jobs_launched = 5
        jobs_skipped = 2
        jobs_rejected = 1

        with patch('src.cluster.common.frame.elapsed_ms') as mock_elapsed_ms:
            mock_elapsed_ms.return_value = 100

            self.common.report_results(start, jobs_launched, jobs_skipped, jobs_rejected)

            mock_elapsed_ms.assert_called_once_with(start)
            self.log.info.assert_called_once_with(
                "Launched 5, rejected 1, skipped 2 jobs. Runtime: 100 ms."
            )

    def test_report_results_no_jobs(self):
        start = 0
        jobs_launched = 0
        jobs_skipped = 0
        jobs_rejected = 0

        with patch('src.cluster.common.frame.elapsed_ms') as mock_elapsed_ms:
            mock_elapsed_ms.return_value = 100

            self.common.report_results(start, jobs_launched, jobs_skipped, jobs_rejected)

            mock_elapsed_ms.assert_called_once_with(start)
            self.log.info.assert_called_once_with("No jobs to handle. Runtime: 100 ms.")
