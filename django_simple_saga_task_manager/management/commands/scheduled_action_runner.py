from django.conf import settings
from django.core.management.base import BaseCommand
from django_simple_saga_task_manager.models import Task
from django_simple_saga_task_manager.saga_interface import SAGATaskInterface
import logging
import kronos

LOG = logging.getLogger(__name__)

@kronos.register(settings.SAGA_REMOTE_CRON_SCHEDULE, args={'--remote': ''})
@kronos.register(settings.SAGA_LOCAL_CRON_SCHEDULE, args={'--local': ''})
class Command(BaseCommand):
    help = 'Process outstanding SAGA actions'

    def add_arguments(self, parser):
        remote_parser = parser.add_mutually_exclusive_group(required=False)
        remote_parser.add_argument('--remote', dest='remote', action='store_true')
        remote_parser.add_argument('--local', dest='remote', action='store_false')
        parser.set_defaults(remote=False)

    def handle(self, *args, **options):
        remote = options['remote']
        LOG.debug('Handling tasks with remote set to %s', remote)
        self.process_actions(remote)

    def process_actions(self, remote=False):
        '''
        Process tasks in the queue.

        remote: boolean
            process remote tasks if true, else process local tasks.
        '''
        if (remote):
            task_type = Task.REMOTE
        else:
            task_type = Task.LOCAL

        # Only create SAGA interface if any tasks in queue
        queued = Task.objects.exclude(status=Task.COMPLETE).exclude(status=Task.FAILED).filter(type=task_type).count()
        if (queued > 0):
            LOG.debug('Processing tasks')
            # Create saga interface using context manager
            with SAGATaskInterface(remote) as si:

                # First process QUEUED tasks. This gives the opportunity
                # for short running tasks to have run and be processed
                # in this cycle.

                for task in Task.objects.filter(status=Task.QUEUED).filter(type=task_type):
                    running = Task.objects.filter(status=Task.RUNNING).filter(type=task_type).count()
                    if (remote):
                        if (running < settings.SAGA_MAX_REMOTE_JOBS):
                            si.submit_saga_task(task)
                    else:
                        if (running < settings.SAGA_MAX_LOCAL_JOBS):
                            si.submit_saga_task(task)

                # Next process running tasks
                for task in Task.objects.filter(status=Task.RUNNING).filter(type=task_type):
                    si.update_running_saga_task_status(task)

                # Tasks failed while running
                for task in Task.objects.filter(status=Task.FAILED_RUNNING).filter(type=task_type):
                    si.process_finished_saga_task(task)

                # Finally finished tasks
                for task in Task.objects.filter(status=Task.FINISHED_RUNNING).filter(type=task_type):
                    si.process_finished_saga_task(task)
