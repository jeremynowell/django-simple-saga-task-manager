import os
import time

from django.conf import settings
from simple_saga_task_manager.tests.saga_test_case import SagaTestCase
from simple_saga_task_manager.models import Task
from simple_saga_task_manager.saga_interface import SAGATaskInterface

class SagaInterfaceEndToEndLocalPythonScriptTests(SagaTestCase):

    def test_end_to_end_local_python(self):
        task_name = 'python'
        task_args = [os.path.join(settings.SAGA_TEST_LOCAL_PYTHON_PATH, settings.SAGA_TEST_PYTHON_SCRIPT)]
        task_args = task_args + settings.SAGA_TEST_PYTHON_ARGS
        task_environment = {'PYTHONPATH': settings.SAGA_TEST_LOCAL_PYTHON_PATH}
        output_files = [settings.SAGA_TEST_OUTPUT_FILE]

        task = Task.objects.create(name=task_name, arguments=task_args, status=Task.QUEUED, type=Task.LOCAL,
                                   environment=task_environment, expected_output_files=output_files)
        # Create task input file
        with open(settings.SAGA_TEST_INPUT_FILE, 'r') as f:
            task.addInputFile(f)

        with (SAGATaskInterface(False)) as si:
            si.submit_saga_task(task)

            # Task should now be running
            status = task.status
            self.assertEqual(Task.RUNNING, status)

            # Process running task
            while (status == Task.RUNNING):
                si.update_running_saga_task_status(task)
                status = task.status
                time.sleep(5)

            # Task should now be finished running
            self.assertEqual(Task.FINISHED_RUNNING, status)

            si.process_finished_saga_task(task)

        # Task should now be complete
        self.assertEqual(Task.COMPLETE, task.status)
        for f in output_files:
            self.check_file_exists(os.path.join('tasks', str(task.id), 'outputs', f))


    def test_end_to_end_local_python_many(self):
        task_name = 'python'
        task_args = [os.path.join(settings.SAGA_TEST_LOCAL_PYTHON_PATH, settings.SAGA_TEST_PYTHON_SCRIPT)]
        task_args = task_args + settings.SAGA_TEST_PYTHON_ARGS
        task_environment = {'PYTHONPATH': settings.SAGA_TEST_LOCAL_PYTHON_PATH}
        output_files = [settings.SAGA_TEST_OUTPUT_FILE]

        number_of_jobs = 5

        with (SAGATaskInterface(False)) as si:

            for i in range(number_of_jobs):

                task = Task.objects.create(name=task_name, arguments=task_args, status=Task.QUEUED, type=Task.LOCAL,
                                   environment=task_environment, expected_output_files=output_files)
                # Create task input file
                with open(settings.SAGA_TEST_INPUT_FILE, 'r') as f:
                    task.addInputFile(f)
                si.submit_saga_task(task)

                # Task should now be running
                status = task.status
                self.assertEqual(Task.RUNNING, status)



        running_jobs = True
        while running_jobs:

            with (SAGATaskInterface(False)) as si:

                tasks = Task.objects.filter(status=Task.RUNNING)
                if len(tasks) == 0:
                    running_jobs = False
                else:
                    for task in tasks:
                        si.update_running_saga_task_status(task)


        with (SAGATaskInterface(False)) as si:

            tasks = Task.objects.filter(status=Task.FAILED)
            self.assertEqual(len(tasks), 0)

            tasks = Task.objects.filter(status=Task.FINISHED_RUNNING)
            self.assertEqual(len(tasks), number_of_jobs)

            for task in tasks:
                si.process_finished_saga_task(task)
                for f in output_files:
                    self.check_file_exists(os.path.join('tasks', str(task.id), 'outputs', f))
