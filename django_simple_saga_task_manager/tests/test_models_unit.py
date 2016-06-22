import os

from django.conf import settings
from django.test import TestCase, override_settings
from django_simple_saga_task_manager.models import Task, InputFile, task_to_path,\
    task_input_path, task_output_path, OutputFile, StdOut, StdError
from django_simple_saga_task_manager.tests.saga_test_case import SagaTestCase

INPUT_FILE = os.path.join(os.path.dirname(__file__), 'resources', 'input_test.txt')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'resources', 'output_test.txt')
STDOUT_FILE = os.path.join(os.path.dirname(__file__), 'resources', 'stdout_test.txt')
STDERR_FILE = os.path.join(os.path.dirname(__file__), 'resources', 'stderr_test.txt')

@override_settings(MEDIA_ROOT = TEST_DIR)
class FileTests(SagaTestCase):
    def setUp(self):
        # Create directory to store files
        self.setup_dir(TEST_DIR)

        # Create test Task
        global task
        task = self.create_local_queued_task()

        # Add input file
        self.add_input_file(INPUT_FILE, task)

        # Add output file
        self.add_output_file(OUTPUT_FILE, task)

    def test_task_to_path(self):
        actualPath = task_to_path(100,
                                  "input_test.txt",
                                  "test_path")
        expectedPath = os.path.join('tasks', '100', 'test_path', 'input_test.txt')
        self.assertEqual(actualPath, expectedPath)

    def test_task_input_path(self):
        infile = InputFile.objects.get(id=1)
        actualPath = task_input_path(infile,
                                     "input_test.txt")
        expectedPath = os.path.join('tasks', '1', 'inputs', 'input_test.txt')
        self.assertEqual(actualPath, expectedPath)

    def test_task_output_path(self):
        outfile = OutputFile.objects.get(id=1)
        actualPath = task_output_path(outfile,
                                     "output_test.txt")
        expectedPath = os.path.join('tasks', '1', 'outputs', 'output_test.txt')
        self.assertEqual(actualPath, expectedPath)

    def test_Task_addInputFile(self):
        inputFile = os.path.join(os.path.dirname(__file__), 'resources', 'input_test2.txt')
        with open(inputFile, 'r') as f:
            task.addInputFile(f)

        expected_path = os.path.join(TEST_DIR, 'tasks', str(task.pk), 'inputs', 'input_test2.txt')
        self.assertTrue(os.path.exists(expected_path))

    def test_Task_addOutputFile(self):
        outputFile = os.path.join(os.path.dirname(__file__), 'resources', 'output_test2.txt')
        with open(outputFile, 'r') as f:
            task.addOutputFile(f)

        expected_path = os.path.join(TEST_DIR, 'tasks', str(task.pk), 'outputs', 'output_test2.txt')
        self.assertTrue(os.path.exists(expected_path))

    def test_Task_addStdOutFile(self):
        outputFile = os.path.join(os.path.dirname(__file__), 'resources', 'stdout_test2.txt')
        with open(outputFile, 'r') as f:
            task.addStdOutFile(f)

        expected_path = os.path.join(TEST_DIR, 'tasks', str(task.pk), 'outputs', 'stdout_test2.txt')
        self.assertTrue(os.path.exists(expected_path))

    def test_Task_addStdErrFile(self):
        outputFile = os.path.join(os.path.dirname(__file__), 'resources', 'stderr_test2.txt')
        with open(outputFile, 'r') as f:
            task.addStdErrFile(f)

        expected_path = os.path.join(TEST_DIR, 'tasks', str(task.pk), 'outputs', 'stderr_test2.txt')
        self.assertTrue(os.path.exists(expected_path))

    def test_InputFile(self):
        infile = InputFile.objects.get(id=1)
        self.assertTrue(os.path.exists(infile.input_file.path))
        expected_path = os.path.join(TEST_DIR, 'tasks', str(task.pk), 'inputs', 'input_test.txt')
        self.assertTrue(os.path.exists(expected_path))

    def test_OutputFile(self):
        outfile = OutputFile.objects.get(id=1)
        self.assertTrue(os.path.exists(outfile.output_file.path))
        expected_path = os.path.join(TEST_DIR, 'tasks', str(task.pk), 'outputs', 'output_test.txt')
        self.assertTrue(os.path.exists(expected_path))

    def test_StdOut(self):
                # Add stdout file
        self.add_stdout_file(STDOUT_FILE, task)
        stdoutfile = StdOut.objects.get(task_id=1)
        self.assertTrue(os.path.exists(stdoutfile.stdout_file.path))
        expected_path = os.path.join(TEST_DIR, 'tasks', str(task.pk), 'outputs', 'stdout_test.txt')
        self.assertTrue(os.path.exists(expected_path))

    def test_StdError(self):
                # Add stderr file
        self.add_stderr_file(STDERR_FILE, task)
        stderrfile = StdError.objects.get(task_id=1)
        self.assertTrue(os.path.exists(stderrfile.stderr_file.path))
        expected_path = os.path.join(TEST_DIR, 'tasks', str(task.pk), 'outputs', 'stderr_test.txt')
        self.assertTrue(os.path.exists(expected_path))
