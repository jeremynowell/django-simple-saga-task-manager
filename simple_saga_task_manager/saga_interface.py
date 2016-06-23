import logging
import os
import saga
import shutil

from django.conf import settings
from simple_saga_task_manager.models import Task
from simple_saga_task_manager.exceptions import SimpleTaskManagerException

#Configure logging
logger = logging.getLogger(__name__)

class SAGATaskInterface():
    '''
    Class which provides SAGA related tasks.

    An instance of this may be instantiated to take care
    of either local tasks or remote tasks. A SAGA session is created
    on instantiation and shared so that SSH connections are reused.

    Settings are obtained from the DJANGO settings file.

    To ensure session is destroyed use as a context manager using "with"
    '''


    def closeService(self):
        # close any SAGA objects and associated resources

        logger.debug('Entering closeService')
        try:
            self.js.close()
            if (self.remote) :
                self.dir.close()
        except saga.SagaException, ex:
            logger.error('Exception in closeService: ' + ex.type)
            logger.error(ex.traceback)
            raise ex
        logger.debug('Exiting closeService')


    def initialiseService(self):
        # Setup appropriate session and job service
        logger.debug('Entering initialiseService')
        if (self.remote):

            try:
                ctx = saga.Context("SSH")
                ctx.user_id = settings.SAGA_REMOTE_USER
                ctx.user_cert = settings.SAGA_REMOTE_SSH_CERT
                ctx.user_key = settings.SAGA_REMOTE_SSH_KEY
                ctx.user_pass = settings.SAGA_REMOTE_SSH_KEY_PASS

                session = saga.Session()
                session.add_context(ctx)

                # initialise the SAGA job service and remote directory instances
                # we cache these to try and avoid the rate limit on opening new ssh connections to the remote host
                self.js = saga.job.Service(remote_job_service_url(), session=session)
                self.dir = saga.filesystem.Directory(remote_file_server_url(), saga.filesystem.READ_WRITE, session=session)
                logger.info('Initialised remote SAGA objects OK')
            except saga.SagaException, ex:
                logger.error('Exception in initialiseService: ' + ex.type)
                logger.error(ex.traceback)
                raise

        else:
            try:
                self.js = saga.job.Service(local_job_service_url())
                logger.info('Initialised local SAGA objects OK')

            except saga.SagaException, ex:
                logger.error('Exception in initialiseService: ' + ex.type)
                logger.error(ex.traceback)
                raise

        logger.debug('Exiting initialiseService')


    def __init__(self, remote=False):
        '''
        Instantiate class.

        remote: boolean
            whether to use this as a remote or local task
            interface
        '''
        self.remote = remote
        logger.debug('saga_interface initialised')


    def __enter__(self):
        # For use with context manager
        logger.debug('Entering __enter__')
        self.initialiseService()
        logger.debug('Exiting __enter__')
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug('Entering __exit__')
        try:
            self.closeService()
        except Exception, ex:
            logger.error('Exception in __exit__: ' + ex.type)
            logger.error(ex.traceback)
            raise ex

        if (exc_type == None):
            logger.debug('Exiting __enter__ OK')
            return True
        else:
            logger.debug('Exiting __enter__ after error')
            return False


    def submit_saga_task(self, task):
        '''
        Submit a task using SAGA.

        This checks the task is queued, and then submits it
        for running. The task status and SAGA ID are updated.
        '''
        logger.debug('Entering submit_saga_task')
        # Check task is queued
        if (task.status != Task.QUEUED):
            logger.error('Attempt to submit non-queued task')
            raise SimpleTaskManagerException("Task has already been submitted")

        # Construct SAGA job description

        try:
            jd = saga.job.Description()
            # executable must be full path to executable script
            jd.executable = task.name

            if self.remote:
                working_directory = remote_working_dir(task.id)
            else:
                working_directory = local_working_dir(task.id)

            jd.working_directory = working_directory
            logger.info('Set working directory to: ' + working_directory)

            # Set list of arguments
            jd.arguments = task.arguments
            logger.debug('Got task arguments: ' + str(jd.arguments))
            # Set environment variables
            jd.environment = task.environment
            logger.debug('Got task environment: ' + str(jd.environment))
            jd.output = settings.SAGA_STD_OUT
            jd.error = settings.SAGA_STD_ERR


            if(task.wallclock_limit > 0):
                jd.wall_time_limit = task.wallclock_limit

            if(task.nprocs > 1):
                jd.total_cpu_count = task.nprocs

            if(len(task.project) > 0):
                jd.project = task.project


            # handle any input files
            if self.remote:
                # create the remote working directory
                try:
                    # note - dir.exists is not currently implemented in SAGA library
                    self.dir.make_dir(str(task.id))
                    logger.info('Created remote task directory')
                except saga.SagaException, ex:
                    # directory creation failed -
                    # check if this is because it already exists - TODO
                    logger.error('remote directory creation failed, assume it already exists')

                for f in task.inputfile_set.all() :
                    self.dir.copy('file://' + f.input_file.path, str(task.id))

                logger.info('Copied input files to remote directory')

            else :
                # Create the local working directory
                try:
                    os.makedirs(working_directory)
                    logger.info('Created local working directory')
                except OSError, ex:
                    if not os.path.isdir(working_directory):
                        logger.error('Failed to create local working directory: ' + ex.type)
                        logger.error(ex.traceback)
                        raise

                for f in task.inputfile_set.all() :
                    shutil.copy(f.input_file.path, working_directory)

                logger.info('Copied input files to remote directory')

            # Create the job, but don't run it yet
            saga_job = self.js.create_job(jd)

            # submit the job
            saga_job.run()

            # Get job ID and place in DB
            jobId = saga_job.id
            task.sagaId = jobId

            # Change status of task
            task.status = Task.RUNNING

            logger.info('SAGA Job submitted with id: ' + jobId)

        except saga.SagaException, ex:
            logger.error('Failed to submit saga job: ' + ex.type)
            logger.error(ex.traceback)
            task.status = Task.FAILED_RUNNING

        # Update task
        task.save()
        logger.debug('Exiting submit_saga_task')




    # state must be one of the defined SAGA job states,
    # ie saga.job.PENDING, saga.job.RUNNING, etc
    # note that this function can be extremely slow if there are a large number of jobs to be listed
    def enumerate_running_jobs(self):

        ids = self.js.list()
        count = 0
        for job_id in ids :
            j = self.js.get_job(job_id)
            if j.get_state() == saga.job.RUNNING:
                count += 1
        return count


    def update_running_saga_task_status(self, task):
        '''
        Updates the task status using SAGA for currently
        running tasks.
        '''
        logger.debug('Entering update_running_saga_task_status for taskId: ' + str(task.id))
        # Check task is running
        if (task.status != Task.RUNNING):
            logger.error('Attempt to update non-running task: ' + str(task.id))
            raise SimpleTaskManagerException("Task is not running")


        try:
            # Get task status using saga
            jobId = task.sagaId
            job = self.js.get_job(jobId)

            state = job.state

            logger.info('Got state of task ' + jobId + ' : ' + state)

            if state == saga.job.NEW:
                task.status = Task.RUNNING
                task.save()
            elif state == saga.job.PENDING:
                task.status = Task.RUNNING
                task.save()
            elif state == saga.job.FAILED:
                task.status = Task.FAILED_RUNNING
                task.save()
            elif state == saga.job.DONE:
                task.status = Task.FINISHED_RUNNING
                task.save()
            elif state == saga.job.CANCELED:
                task.status = Task.FAILED_RUNNING
                task.save()
            elif state == saga.job.RUNNING:
                # job is running, nothing to do
                pass
            else:
                logger.error('Unexpected job state: ' + state)
                task.status = Task.FAILED_RUNNING
                task.save()

        except saga.EXCEPTION, ex:
            logger.error('Failed to get status of saga job: ' + ex.type)
            logger.error(ex.traceback)
            task.status = Task.FAILED_RUNNING
            task.save()

        logger.debug('Exiting update_running_saga_task_status for taskId: ' + str(task.id))


    def process_finished_saga_task(self, task):
        '''
        Updates the status of tasks which have finished running and
        makes the results available in the database.
        '''
        logger.debug('Entering process_finished_saga_task for taskId: ' + str(task.id))
        # Check task has finished running
        if (task.status != Task.FINISHED_RUNNING and task.status != Task.FAILED_RUNNING):
            logger.error('Attempt to process non-finished task: ' + str(task.id))
            raise SimpleTaskManagerException("Task has not finished running")

        try:
            if self.remote :
                # try to create the local working directory in case it wasn't created earlier
                path = local_working_dir(task.id)
                try:
                    os.makedirs(path)
                    logger.info('Created local working directory')
                except OSError, ex:
                    logger.error('Problem creating directory: ' + ex.type)
                    logger.error(ex.traceback)
                    if not os.path.isdir(path):
                        raise

                # retrieve any files from the remote directory
                # note: this will not work with nested directories,
                # only files within the top level task directory will be copied
                # if no output files are specifed then copy the whole lot,
                # otherwise only copy the specified ones plus the stdout and stderr


                # TODO - decend into subdirs and copy them as well

                output_files = task.expected_output_files
                if len(output_files) == 0:
                    logger.info("No output files specified, so copying all top-level files")
                    files = self.dir.list(str(task.id) + '/*')
                    for f in files :
                        if self.dir.is_file(f):
                            logger.info('Copying file: ' + str(f))
                            self.dir.copy(f, local_file_server_task_url(task.id))
                else:
                    logger.info("Copying specified output files plus stdout and stderr")
                    self.dir.copy(str(task.id) + "/" + settings.SAGA_STD_OUT, local_file_server_task_url_with_filename(task.id, settings.SAGA_STD_OUT))
                    self.dir.copy(str(task.id) + "/" + settings.SAGA_STD_ERR, local_file_server_task_url_with_filename(task.id, settings.SAGA_STD_ERR))
                    for f in task.expected_output_files:
                        logger.info('Copying specified output file: ' + str(f))
                        self.dir.copy(str(task.id) + "/" + f, local_file_server_task_url_with_filename(task.id, f))

                # note - we should delete the remote directory,
                # but dir.remove is not currently implemented in the SAGA library for directories
                # self.dir.remove(f)
                # as a workaround, delete the files in the directory
                # TODO - decend into any subdirs
                logger.info("Deleting top-level remote directory files")
                files = self.dir.list(str(task.id) + '/*')
                for f in files :
                    if self.dir.is_file:
                        logger.info('Deleting file: ' + str(f))
                        self.dir.remove(f)


        except saga.EXCEPTION, ex:
            logger.error('Failed to process finished saga job: ' + ex.type)
            logger.error(ex.traceback)
            task.status = Task.FAILED
            raise

        # output files from our task should now be in their own local directory,
        # regardless of whether they were executed locally or remotely

        # iterate over the files in the directory
        try:
            path = local_working_dir(task.id)
            for f in os.listdir(path):
                # Put results into django model
                with open(path + os.path.sep + f , 'r') as python_file:

                    if (f == settings.SAGA_STD_OUT):
                        task.addStdOutFile(python_file)
                        logger.info('Saved standard out file: ' + str(f))
                    elif (f == settings.SAGA_STD_ERR):
                        task.addStdErrFile(python_file)
                        logger.info('Saved standard error file: ' + str(f))
                    elif (f in task.expected_output_files):
                        task.addOutputFile(python_file)
                        logger.info('Saved file: ' + str(f))

            # finally remove the temporary local directory for this task
            shutil.rmtree(path)
            logger.info('Removed local working directory: ' + path)


            # could also delete the SAGA job directory here, to avoid the queue clogging up?
            # path = SAGA_BASE_DIR + "/" + some munging of the job id?


        except:
            logger.error('Failed to process finished saga job output files: ' + ex.type)
            logger.error(ex.traceback)
            task.status = Task.FAILED
            raise

        # Interpret run result - TBD elsewhere

        # Update status
        if (task.status == Task.FAILED_RUNNING):
            task.status = task.FAILED
        elif (task.status == Task.FINISHED_RUNNING):
            task.status = Task.COMPLETE
        task.save()
        logger.info('Processed complete saga job: ' + str(task.id))
        logger.debug('Entering process_finished_saga_task for taskId: ' + str(task.id))


def local_working_dir(taskId):
    return os.path.join(os.path.normpath(settings.SAGA_LOCAL_WORKING_DIR), str(taskId))


def remote_working_dir(taskId):
    # Assume remote computer is Linux/unix
    return settings.SAGA_REMOTE_WORKING_DIR + '/' + str(taskId)


def local_job_service_url():
    url = saga.Url()
    url.set_scheme('fork')
    url.set_host('localhost')
    logger.debug('Got local job service URL: ' + str(url))
    return url


def remote_job_service_url():
    url = saga.Url()
    url.set_scheme(settings.SAGA_REMOTE_JOB_ADAPTER)
    url.set_host(settings.SAGA_REMOTE_HOST)
    logger.debug('Got remote job service URL: ' + str(url))
    return url


def local_file_server_url():
    #'file://localhost/home/jeremy/tasks'
    url = saga.Url()
    url.set_scheme('file')
    url.set_host('localhost')
    url.set_path(settings.SAGA_LOCAL_WORKING_DIR)
    logger.debug('Got local file server URL: ' + str(url))
    return url


def remote_file_server_url():
    #'sftp://indy0.epcc.ed.ac.uk/home/w02/jnowell/518_example/tasks'
    url = saga.Url()
    url.set_scheme('sftp')
    url.set_host(settings.SAGA_REMOTE_HOST)
    url.set_path(settings.SAGA_REMOTE_WORKING_DIR)
    logger.debug('Got remote file server URL: ' + str(url))
    return url


def local_file_server_task_url(taskId):
    url = local_file_server_url()
    path = url.get_path()
    new_path = path + '/' + str(taskId) + '/'
    url.set_path(new_path)
    logger.debug('Got local file server URL for task: ' + str(url))
    return url

def local_file_server_task_url_with_filename(taskId, filename):
    url = local_file_server_url()
    path = url.get_path()
    new_path = path + '/' + str(taskId) + '/' + filename
    url.set_path(new_path)
    logger.debug('Got local file server URL for task: ' + str(url))
    return url





