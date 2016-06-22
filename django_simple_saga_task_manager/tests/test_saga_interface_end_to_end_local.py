import os
import time

from django_simple_saga_task_manager.tests.saga_test_case import SagaTestCase
from django_simple_saga_task_manager.models import Task
from django_simple_saga_task_manager.saga_interface import SAGATaskInterface

class SagaInterfaceEndToEndLocalTests(SagaTestCase):

    def test_end_to_end_local(self):
        # Create task in DB
        # Construct task name
        task_name = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'test-tasks', 'hello-world.sh'))
        task = self.create_local_queued_task(task_name)

        si = SAGATaskInterface(False)
        si.initialiseService()
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

        si.closeService()

        self.check_output_files_exist(task)


    def test_end_to_end_local_context_manager(self):
        # Create task in DB
        # Construct task name
        task_name = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'test-tasks', 'hello-world.sh'))
        task = self.create_local_queued_task(task_name)

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

        self.check_output_files_exist(task)


    def test_end_to_end_local_args(self):
        output_file = 'test.out'
        task_args = ['Hello World', '> ' + output_file]
        task_name = '/bin/echo'
        task_environment = {}
        output_files = [output_file]
        task = Task.objects.create(name=task_name, arguments=task_args, status=Task.QUEUED, type=Task.LOCAL,
                                   environment=task_environment, expected_output_files=output_files)

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

        self.check_output_files_exist(task)
        self.check_file_exists(os.path.join('tasks', str(task.id), 'outputs', output_file))
