import os
import shutil

from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings
from simple_saga_task_manager.models import StdError, StdOut, Task

TEST_DIR = os.path.join(os.path.dirname(__file__), 'temp')
WORKING_DIR = os.path.join(os.path.dirname(__file__), 'working')

@override_settings(MEDIA_ROOT = TEST_DIR,
                   SAGA_LOCAL_WORKING_DIR = WORKING_DIR)
class SagaTestCase(TestCase):
    def setUp(self):
        self.setup_dir(TEST_DIR)
        self.setup_dir(WORKING_DIR)

    def tearDown(self):
        self.cleanup_dir(TEST_DIR)
        self.cleanup_dir(WORKING_DIR)

    def check_file_exists(self, relative_path):
        abs_path = os.path.join(TEST_DIR, relative_path)
        self.assertTrue(os.path.exists(abs_path))

    def check_output_files_exist(self, task):
        # Check that output files exist
        stdoutfile = StdOut.objects.get(task=task)
        self.assertIsInstance(stdoutfile, StdOut)
        self.assertTrue(os.path.exists(stdoutfile.stdout_file.path))
        expected_path = os.path.join(TEST_DIR, 'tasks', str(task.id), 'outputs', settings.SAGA_STD_OUT)
        self.assertTrue(os.path.exists(expected_path))

        stderrfile = StdError.objects.get(task=task)
        self.assertIsInstance(stderrfile, StdError)
        self.assertTrue(os.path.exists(stderrfile.stderr_file.path))
        expected_path = os.path.join(TEST_DIR, 'tasks', str(task.id), 'outputs', settings.SAGA_STD_ERR)
        self.assertTrue(os.path.exists(expected_path))

    def cleanup_dir(self, directory):
        shutil.rmtree(directory, ignore_errors=True)

    def setup_dir(self, directory):
        # Cleanup existing directory
        shutil.rmtree(directory, ignore_errors=True)
        # Create directory to store files
        os.mkdir(directory)

    def create_local_queued_task(self, task_name="test_task"):
        task_args = []
        task_environment = {}
        output_files = []
        task = Task.objects.create(name=task_name, arguments=task_args, status=Task.QUEUED, type=Task.LOCAL,
                                   environment=task_environment, expected_output_files=output_files)
        return task

    def create_remote_queued_task(self, task_name="test_task"):
        task_args = []
        task_environment = {}
        output_files = []
        task = Task.objects.create(name=task_name, arguments=task_args, status=Task.QUEUED, type=Task.REMOTE,
                                   environment=task_environment, expected_output_files=output_files)
        return task

    def create_local_running_task(self, task_name="test_task"):
        task_args = []
        task_environment = {}
        output_files = []
        task = Task.objects.create(name=task_name, arguments=task_args, status=Task.RUNNING, type=Task.LOCAL,
                                   environment=task_environment, expected_output_files=output_files)
        return task

    def create_remote_running_task(self, task_name="test_task"):
        task_args = []
        task_environment = {}
        output_files = []
        task = Task.objects.create(name=task_name, arguments=task_args, status=Task.RUNNING, type=Task.REMOTE,
                                   environment=task_environment, expected_output_files=output_files)
        return task

    def create_remote_complete_task(self, task_name="test_task"):
        task_args = []
        task_environment = {}
        output_files = []
        task = Task.objects.create(name=task_name, arguments=task_args, status=Task.COMPLETE, type=Task.REMOTE,
                                   environment=task_environment, expected_output_files=output_files)
        return task

    def add_input_file(self, filename, task):
        # Create input file
        with open(filename, 'r') as f:
            df = File(f)
            task.inputfile_set.create(input_file=df)

    def add_output_file(self, filename, task):
        with open(filename, 'r') as f:
            df = File(f)
            task.outputfile_set.create(output_file=df)

    def add_stdout_file(self, filename, task):
        with open(filename, 'r') as f:
            df = File(f)
            StdOut.objects.create(task=task, stdout_file=df)

    def add_stderr_file(self, filename, task):
        with open(filename, 'r') as f:
            df = File(f)
            StdError.objects.create(task=task, stderr_file=df)
