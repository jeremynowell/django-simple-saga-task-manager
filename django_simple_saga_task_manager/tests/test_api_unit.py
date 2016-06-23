import os

from django.conf import settings
from django.test import TestCase, override_settings
import django_simple_saga_task_manager.api as api
from django_simple_saga_task_manager.models import Task, InputFile
from django_simple_saga_task_manager.tests.saga_test_case import SagaTestCase, TEST_DIR

INPUT_FILE = os.path.join(os.path.dirname(__file__), 'resources', 'input_test.txt')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'resources', 'output_test.txt')
STDOUT_FILE = os.path.join(os.path.dirname(__file__), 'resources', 'stdout_test.txt')
STDERR_FILE = os.path.join(os.path.dirname(__file__), 'resources', 'stderr_test.txt')

@override_settings(MEDIA_ROOT = TEST_DIR)
class SubmitTaskTests(SagaTestCase):

    def test_submit_task_local(self):
        with open(INPUT_FILE, 'r') as f:
            task_id = api.submit_task('test_task', input_files=[f])

        self.assertEqual(task_id, 1)

        task = Task.objects.get(id=1)
        self.assertEqual(task.name, 'test_task')
        self.assertEqual(task.status, Task.QUEUED)
        self.assertEqual(task.type, Task.LOCAL)

        inputfile = InputFile.objects.get(id=1)
        self.assertEqual(os.path.basename(inputfile.input_file.name), 'input_test.txt')
        expected_path = os.path.join('tasks', str(1), 'inputs', 'input_test.txt')
        self.check_file_exists(expected_path)

    def test_submit_task_remote(self):
        with open(INPUT_FILE, 'r') as f:
            task_id = api.submit_task('test_task', input_files=[f], remote=True)

        self.assertEqual(task_id, 1)

        task = Task.objects.get(id=1)
        self.assertEqual(task.name, 'test_task')
        self.assertEqual(task.status, Task.QUEUED)
        self.assertEqual(task.type, Task.REMOTE)

        inputfile = InputFile.objects.get(id=1)
        self.assertEqual(os.path.basename(inputfile.input_file.name), 'input_test.txt')
        expected_path = os.path.join('tasks', str(1), 'inputs', 'input_test.txt')
        self.check_file_exists(expected_path)

    def test_get_task_status_queued(self):
        self.create_local_queued_task()

        actualStatus = api.get_task_status(1)
        expectedStatus = Task.QUEUED
        self.assertEqual(actualStatus, expectedStatus)

        self.create_remote_queued_task()

        actualStatus = api.get_task_status(2)
        self.assertEqual(actualStatus, expectedStatus)

    def test_get_task_status_running(self):
        self.create_local_running_task()

        actualStatus = api.get_task_status(1)
        expectedStatus = Task.RUNNING
        self.assertEqual(actualStatus, expectedStatus)

        self.create_remote_running_task()

        actualStatus = api.get_task_status(2)
        self.assertEqual(actualStatus, expectedStatus)

    def test_get_task_statuses(self):
        self.create_local_queued_task()
        self.create_remote_queued_task()
        self.create_local_running_task()
        self.create_remote_running_task()

        statuses = api.get_task_statuses("test_task")
        self.assertEqual(len(statuses), 4)
        self.assertEqual(statuses[0]['id'], 1)
        self.assertEqual(statuses[0]['status'], Task.QUEUED)
        self.assertEqual(statuses[1]['id'], 2)
        self.assertEqual(statuses[1]['status'], Task.QUEUED)
        self.assertEqual(statuses[2]['id'], 3)
        self.assertEqual(statuses[2]['status'], Task.RUNNING)
        self.assertEqual(statuses[3]['id'], 4)
        self.assertEqual(statuses[3]['status'], Task.RUNNING)

    def test_get_task_results(self):
        task = self.create_remote_complete_task()
        self.add_input_file(INPUT_FILE, task)
        self.add_stdout_file(STDOUT_FILE, task)
        self.add_stderr_file(STDERR_FILE, task)
        self.add_output_file(OUTPUT_FILE, task)

        outputs = api.get_task_results(task.pk)
        stdout_file = outputs['stdout']
        self.assertEqual(os.path.basename(STDOUT_FILE), os.path.basename(stdout_file.name))
        stdout_file.close()

        stderr_file = outputs['stderr']
        self.assertEqual(os.path.basename(STDERR_FILE), os.path.basename(stderr_file.name))
        stderr_file.close()

        output_files = outputs['output_files']
        self.assertEqual(os.path.basename(OUTPUT_FILE), os.path.basename(output_files[0].name))
        output_files[0].close()
