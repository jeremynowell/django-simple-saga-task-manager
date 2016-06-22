Django simple SAGA task manager
===============================

The Django Simple SAGA task manager is a Django app for managing execution
of tasks outside of the standard Django request-response cycle.

Tasks may be executed locally or remotely, using the RADICAL-SAGA interface
to interface with remote batch submission systems.

Once placed in the execution queue, tasks are submitted to the appropriate
resource for execution.

A Django management command runs according a configured schedule in order to
start and monitor tasks and to retrieve their results.

Detailed documentation, including the installation guide is in the "docs"
directory.

Quick start
-----------

1. Add "simple\_saga\_task\_manager" to your INSTALLED_APPS setting like this:

        INSTALLED_APPS = [
            ...
            'simple_saga_task_manager',
        ]

2. Include the URLconf in your project urls.py like this:

        url(r'^simple_saga_task_manager/', include('simple_saga_task_manager.urls')),

3. Run `python manage.py migrate` to create the task manager models.

4.  Start the development server and visit <http://127.0.0.1:8000/simple_saga_task_manager/>
    to start submitting tasks.

Tests
-----

Tests are found in the tests directory. Before running the settings described in the docs
directory need to be configured correctly.
