import os

from django.test import override_settings
from simple_saga_task_manager.tests.saga_test_case import SagaTestCase
from simple_saga_task_manager.saga_interface import local_working_dir,\
            remote_working_dir, \
            local_job_service_url, remote_job_service_url,\
            local_file_server_url, remote_file_server_url,\
            local_file_server_task_url

class SagaInterfaceUnitTests(SagaTestCase):

    @override_settings(SAGA_LOCAL_WORKING_DIR = '/test/directory')
    def test_local_working_dir(self):
        actual_directory = local_working_dir('taskId')
        expected_directory = os.path.normpath('/test/directory/taskId')
        self.assertEqual(actual_directory, expected_directory)

    @override_settings(SAGA_REMOTE_WORKING_DIR = '/test/directory')
    def test_remote_working_dir(self):
        actual_directory = remote_working_dir('taskId')
        expected_directory = '/test/directory/taskId'
        self.assertEqual(actual_directory, expected_directory)

    def test_local_job_service_url(self):
        actual_url = str(local_job_service_url())
        expected_url = "fork://localhost"
        self.assertEqual(actual_url, expected_url)

    @override_settings(SAGA_REMOTE_HOST = 'test.machine.address',
                       SAGA_REMOTE_JOB_ADAPTER = 'lsf+ssh')
    def test_remote_job_service_url(self):
        actual_url = str(remote_job_service_url())
        expected_url = "lsf+ssh://test.machine.address"
        self.assertEqual(actual_url, expected_url)

    @override_settings(SAGA_LOCAL_WORKING_DIR = '/test/directory')
    def test_local_file_server_url(self):
        actual_url = str(local_file_server_url())
        expected_url = 'file://localhost/test/directory'
        self.assertEqual(actual_url, expected_url)

    @override_settings(SAGA_REMOTE_HOST = 'test.machine.address',
                       SAGA_REMOTE_WORKING_DIR = '/test/directory')
    def test_remote_file_server_url(self):
        actual_url = str(remote_file_server_url())
        expected_url = "sftp://test.machine.address/test/directory"
        self.assertEqual(actual_url, expected_url)

    @override_settings(SAGA_LOCAL_WORKING_DIR = '/test/directory')
    def test_local_file_server_task_url(self):
        actual_url = str(local_file_server_task_url('taskId'))
        expected_url = 'file://localhost/test/directory/taskId/'
        self.assertEqual(actual_url, expected_url)
