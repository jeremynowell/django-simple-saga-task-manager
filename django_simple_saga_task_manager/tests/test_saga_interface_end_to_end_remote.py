import os
import time

from django_saga_simple_task_manager.tests.saga_test_case import SagaTestCase
from django_saga_simple_task_manager.models import Task
from django_saga_simple_task_manager.saga_interface import SAGATaskInterface

class SagaInterfaceEndToEndRemoteTests(SagaTestCase):

    def test_end_to_end_remote(self):
        # Create task in DB
        # Construct task name
        task_name = '/bin/date'
        task = self.create_remote_queued_task(task_name)

        si = SAGATaskInterface(True)
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


    def test_end_to_end_remote_context_manager(self):
        # Create task in DB
        # Construct task name
        task_name = '/bin/date'
        task = self.create_remote_queued_task(task_name)

        with (SAGATaskInterface(True)) as si:
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


    def test_end_to_end_remote_args(self):
        output_file = 'test.out'
        task_args = ['Hello World', '> ' + output_file]
        task_name = '/bin/echo'
        task_environment = {}
        output_files = [output_file]
        task = Task.objects.create(name=task_name, arguments=task_args, status=Task.QUEUED, type=Task.REMOTE,
                                   environment=task_environment, expected_output_files=output_files)

        with (SAGATaskInterface(True)) as si:
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
