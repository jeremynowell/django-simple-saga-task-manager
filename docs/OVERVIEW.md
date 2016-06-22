Django Simple SAGA Task Manager
===============================

Overview
--------
The Django Simple SAGA Task Manager is a Django app for managing the
execution of tasks outside of the standard Django request-response cycle.

Tasks may be executed locally, for short tasks, or remotely for longer
running or more computationally intensive tasks. The management of tasks
uses the
[RADICAL-SAGA interface](http://radical-cybertools.github.io/saga-python/),
which is able to interface with remote batch submission systems over
SSH connections.

Once placed in the execution queue, the task manager is responsible for
executing tasks, updating their status, and retrieving the results of
their execution once complete.

An API is provided for queueing jobs for execution, getting their status
and retrieving their results. Alternatively, the Django Task model may
be used directly by those familiar with Django.

Design Overview
---------------

A Django model holds all task information, see the usual Django `models.py`
for the description of this model.

A Django management command (`management\commands\scheduled_action_runner`)
runs according a configured schedule (making use of the
[django-kronos package](https://github.com/jgorset/django-kronos)) which
in turn operates on the tasks according to their status, using a
`SagaTaskInterface` object as described in `saga_interface.py`.
All task operations use RADICAL-SAGA, be they local or remote operations.

A high-level API is defined in `api.py`.

Tests
-----
Tests are provided in the `tests` directory, and may be executed using
the standard Django test runner through `manage.py`, once the appropriate
settings have been configured. E.g.

    python manage.py test django_simple_saga_task_manager.tests.test_api_unit

Note that some of these tests are end-to-end tests and will likely require
some settings to be changed - see the `SAGA_TEST_*` settings in `defaults.py`.

Examples
--------
Along with the tests, examples of usage may be seen in the `views.py`,
`forms.py` and the accompanying HTML files in the `templates`
directory.
