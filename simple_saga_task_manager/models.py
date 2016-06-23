import os

from django.core.files import File
from django.db import models
from django.utils import timezone
from picklefield.fields import PickledObjectField

def task_to_path(task_id, filepath, subdir):
    '''
    Returns a path based on the tasks ID.

    task_id: int
        ID of task
    filepath: string
        full path to file
    subdir: string
        subdirectory to add on to task directory
    return: string
    '''
    # Get just the filename
    filename = os.path.basename(filepath)
    # Concatenate parts of directory
    return os.path.join('tasks', str(task_id), subdir, filename)

def task_input_path(instance, filename):
    '''
    Construct location to store input file, based on task ID.

    instance:
        object model instance
    filename: string
        full path of input file
    returns: path relative to MEDIA_ROOT
    '''
    return task_to_path(instance.task.pk, filename, 'inputs')

def task_output_path(instance, filename):
    '''
    Construct location to store output file, based on task ID.

    instance:
        object model instance
    filename: string
        full path of output file
    returns: path relative to MEDIA_ROOT
    '''
    return task_to_path(instance.task.pk, filename, 'outputs')

class Task(models.Model):
    '''
    Represents tasks which may be executed locally or remotely.
    '''
    # Enum of possible status values
    QUEUED = 'QU'
    RUNNING = 'RU'
    FINISHED_RUNNING = 'FR'
    FAILED_RUNNING = 'FL'
    FAILED = 'FA'
    COMPLETE = 'CO'
    STATUS_CHOICES = (
                      (QUEUED, 'Queued'),
                      (RUNNING, 'Running'),
                      (FINISHED_RUNNING, 'Completed running'),
                      (FAILED_RUNNING, 'Failed while running'),
                      (FAILED, 'Failed'),
                      (COMPLETE, 'Successful completion'),
                      )

    # Enum of possible types
    REMOTE = 'R'
    LOCAL = 'L'
    TYPE_CHOICES = (
                    (REMOTE, 'Remote'),
                    (LOCAL, 'Local'),
                    )

    name = models.CharField(max_length=100)
    arguments = PickledObjectField()
    environment = PickledObjectField()
    expected_output_files = PickledObjectField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    sagaId = models.CharField(max_length=100, default="", blank=True)
    wallclock_limit = models.IntegerField(default=0, blank=True)
    project = models.CharField(max_length=100, default="", blank=True)
    nprocs = models.IntegerField(default=1)
    cost = models.FloatField(default=0)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    #TODO: overwrite save() to set created date

    def addInputFile(self, inputFile):
        '''
        Add an input file to this task.

        inputFile - python file object to add.
        '''
        # Convert file to django file
        df = File(inputFile)
        # Associate with task
        self.inputfile_set.create(input_file=df)

    def addOutputFile(self, outputFile):
        '''
        Add an output file to this task.

        outputFile - python file object to add.
        '''
        # Convert file to django file
        df = File(outputFile)
        # Associate with task
        self.outputfile_set.create(output_file=df)

    def addStdOutFile(self, stdOutFile):
        '''
        Add a stdout file to this task.

        stdOutFile - python file object to add.
        '''
        # Convert file to django file
        df = File(stdOutFile)
        StdOut.objects.create(task=self, stdout_file=df)

    def addStdErrFile(self, stdErrFile):
        '''
        Add a stderr file to this task.

        stdErrFile - python file object to add.
        '''
        # Convert file to django file
        df = File(stdErrFile)
        StdError.objects.create(task=self, stderr_file=df)

class InputFile(models.Model):
    '''
    Stores input files for tasks
    '''
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    input_file = models.FileField(upload_to=task_input_path)

class StdOut(models.Model):
    '''
    Stores standard out in a file
    '''
    task = models.OneToOneField(Task, on_delete=models.CASCADE, primary_key=True)
    stdout_file = models.FileField(upload_to=task_output_path)

class StdError(models.Model):
    '''
    Stores standard error in a file
    '''
    task = models.OneToOneField(Task, on_delete=models.CASCADE, primary_key=True)
    stderr_file = models.FileField(upload_to=task_output_path)

class OutputFile(models.Model):
    '''
    Stores output files for tasks
    '''
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    output_file = models.FileField(upload_to=task_output_path)
