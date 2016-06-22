from django.db import transaction
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django_simple_saga_task_manager.models import Task

def submit_task(task_name,
                remote=False,
                arguments=[],
                input_files=[],
                environment={},
                expected_output_files=[],
                wallclock_limit=0,
                project="",
                nprocs=1):
    '''
    Submit a task to be queued to be run, either locally or remotely.

    task_name: string
        name of task
    remote: boolean (optional)
        whether to run files locally or remotely
        default = run locally
    arguments: string list (optional)
        optional array of arguments for task, eg ["--help", "-o output_file"]
    input_files: file object list (optional)
        input files to task
    environment: string dict (optional)
        environment variables in form {'VARIABLE': 'VALUE'}
    expected_output_files: string list (optional)
        list of output files to save at end of task
    wallclock_limit: integer (optional)
        limit on wall clock for remote jobs (seconds)
    project: string (optional)
        project to charge job against on remote resource
    nprocs: interger (optional)
        number of cores to assign to task on remote resource (default = 1)

    returns: int
        task_id
    '''
    if remote:
        task_type = Task.REMOTE
    else:
        task_type = Task.LOCAL

    taskId = 0

    try:
        with transaction.atomic():
            task = Task(name=task_name,
                        arguments=arguments,
                        environment=environment,
                        expected_output_files=expected_output_files,
                        status=Task.QUEUED,
                        type=task_type,
                        wallclock_limit = wallclock_limit,
                        project = project,
                        nprocs = nprocs)
            task.save()
            for f in input_files:
                task.addInputFile(f)
            taskId = task.pk
    except IntegrityError as e:
        print "IE: " + str(e)
        # TODO: throw error here

    return taskId

def get_task_status(task_id):
    '''
    Gets the status of the task.

    task_id: int
        ID of task as stored in DB
    returns: string
        task status
    '''
    task = Task.objects.get(id=task_id)
    return task.status

def get_task_statuses(task_name):
    '''
    Gets the status of the set of tasks with given name.

    task_name: string
        name of task to run query against in DB
    returns: array of dicts {'id': N, 'status': task status}
    '''
    tasks = Task.objects.filter(name=task_name)
    statuses = []
    for t in tasks:
        info = {
                'id': t.pk,
                'status': t.status
                }
        statuses.append(info)
    return statuses

def get_task_results(task_id):
    '''
    Gets the results of a task.

    task_id: int
        ID of task as stored in DB
    returns: array of dicts
        describing output [{filename: file}, {}, ...]
        stdout and stderr where available
    '''
    task = Task.objects.get(id=task_id)

    outputs = {}

    try:
        stdout = task.stdout
        #file_info = {'stdout': stdout.stdout_file.file}
        outputs['stdout'] = stdout.stdout_file.file
        #outputs.append(file_info)
    except ObjectDoesNotExist:
        pass

    try:
        stderr = task.stderror
        outputs['stderr'] = stderr.stderr_file.file
        #outputs.append(file_info)
    except ObjectDoesNotExist:
        pass

    output_files = []
    for f in task.outputfile_set.all():
        file_name = f.output_file.name
        file_object = f.output_file.file
        #file_object = file()
        #shutil.copyfileobj(f.output_file.file, file_object)
        file_info = {file_name: file_object}
        output_files.append(file_object)

    outputs['output_files'] = output_files

    return outputs

def get_task_cost(task_id):
    '''
    Gets the costs of the task.

    task_id: int
        ID of task as stored in DB
    returns: float
        task cost
    '''
    task = Task.objects.get(id=task_id)
    return task.cost
