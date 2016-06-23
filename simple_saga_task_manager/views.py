import logging
from django.forms import formset_factory
from django.shortcuts import render, render_to_response
from django.template.context import RequestContext
from django.views import generic
from simple_saga_task_manager import api as api
from simple_saga_task_manager.forms import TaskForm, ArgumentForm, EnvironmentForm
from simple_saga_task_manager.models import Task
from django.http.response import HttpResponseRedirect

LOG = logging.getLogger(__name__)

class IndexView(generic.ListView):
    model = Task
    template_name = 'tasks.html'


def tasks(request):
    LOG.debug("Tasks view requested")
    return render_to_response('tasks.html', context_instance=RequestContext(request))

def task_status(request, taskId):
    LOG.debug("Task status view requested for task " + str(taskId))
    task = Task.objects.get(pk=taskId)
    return render_to_response('task_status.html',
                              {'taskId' : taskId,
                               'task' : task},
                              context_instance=RequestContext(request))

def submit_task(request):
    LOG.debug("Task submit view requested")

    ArgumentFormSet = formset_factory(ArgumentForm)
    EnvironmentFormSet = formset_factory(EnvironmentForm)

    # Process data if POST
    if request.method == 'POST':
        task_form = TaskForm(request.POST)

        if task_form.is_valid():
            task_name = task_form.cleaned_data['task_name']
            task_remote = task_form.cleaned_data['remote']

            task_id = api.submit_task(task_name, {}, [], task_remote)

            return HttpResponseRedirect('/tasks/' + str(task_id))

    else:
        task_form = TaskForm()
        argument_formset = ArgumentFormSet(prefix='fs1')
        environment_formset = EnvironmentFormSet(prefix='fs2')

    context = {
               'form': task_form,
               'arg_formset': argument_formset,
               'env_formset': environment_formset,
               }

    return render(request, 'submit.html', context)
