Installation
============

It is recommended to use a python [virtualenv](https://virtualenv.pypa.io/en/stable/)
to separate different python development and production environments.


Install Prerequisites
---------------------
The Django SAGA simple task manager uses the following Python
packages:

* [Django](https://www.djangoproject.com/) (>1.8 required, 1.8.13 tested)
* [django-kronos](https://github.com/jgorset/django-kronos) (0.9 tested)
* [django-picklefield](https://github.com/gintas/django-picklefield) (0.3.2 tested)
* [django-widget-tweaks](https://github.com/kmike/django-widget-tweaks/) (1.4.1 tested)
* [RADICAL-SAGA](http://radical-cybertools.github.io/saga-python/) (>0.40.1 required, 0.41.1 tested)

To install the exact versions of the packages as above then run

    pip install -r requirements.txt

Alternatively, to install the latest version of the packages simply run the
installation script as described in the next section.


Install Task Manager
--------------------

### As a standalone web-app

To use as a standalone web-app, perhaps for demonstration purposes, then no
installation is required, simply download, configure and run as a standard
Django app:

    python manage.py runserver

### As a library

To use as a third-party library in a Django web-app then the recommendation
is to install as for any other Python package.

    python setup.py install

This will install into the standard python site-packages directory. To install
into the user directory run:

    python setup.py install --user

For more details on the standard installation locations see the
[python documentation](https://docs.python.org/2/install/).


Configuration
-------------

The task manager uses Django options to configure working directories and
user information for both remote and local task execution. These have
default settings, but in general the defaults will need to be changed.
These should be set in the Django settings file for the application,
either `settings/dev.py` for the standalone task manager app or
your own Django settings file.

*   `SAGA_STD_OUT`

    Name of file to redirect task standard output to.

    Default: `task.stdout`

*   `SAGA_STD_ERR`

    Name of file to redirect task standard error to.

    Default: `task.stderr`

*   `SAGA_REMOTE_USER`

    Username under which to run jobs on remote server. Note that SSH
    keypair authentication must be configured for this user, using the
    following configuration options.

    Default: `ubuntu`

*   `SAGA_REMOTE_SSH_CERT`

    Public SSH key to access remote server. This should be added to the
    `.ssh/authorized_keys` file on the remote server.

    Default: '/home/cdes/.ssh/id_rsa.pub'

*   `SAGA_REMOTE_SSH_KEY`

    Private SSH key to acces the remote server.

    Default: '/home/cdes/.ssh/id_rsa'

*   `SAGA_REMOTE_SSH_KEY_PASS`

    Password protecting the SSH private key. Clearly if used
    then the configuration file must be protected from unwanted
    access. This is especially important if stored in a code
    repository for example.

    Default: '' (the empty string)

*   `SAGA_REMOTE_HOST`

    The name of the host on which to run remote jobs.

    Default: `indy0.epcc.ed.ac.uk`

*   `SAGA_REMOTE_JOB_ADAPTER`

    The SAGA job adaptor for accessing the remote host.

    Default: `lsf+ssh`

    See the [RADICAL-SAGA documentation](http://saga-python.readthedocs.io/en/latest/)

*   `SAGA_LOCAL_WORKING_DIR`

    The local working directory in which to execute tasks.
    This directory must be writeable by the user under which the
    application is executed. Subdirectories will be created in
    this directory as required by the task manager.

    Default: `/home/cdes/tasks`

*   `SAGA_REMOTE_WORKING_DIR`

    The remote working directory in which to execute tasks.
    This directory must be writeable by the user defined under
    `SAGA_REMOTE_USER`. Subdirectories will be created in
    this directory as required by the task manager.

    Default: `/home/w42/cdes/tasks`

*   `SAGA_MAX_LOCAL_JOBS`

    The maximum number of local tasks to allow at the same time.
    This should be set so that the server which runs the task
    manager is not overloaded.

    Default: 4

*   `SAGA_MAX_REMOTE_JOBS`

    The maximum number of remote tasks to allow at the same time.
    Generally this can be quite high as the remote machine will
    be running a batch scheduler, however administrative policies
    may place a limit on the number of tasks allowed in the queue.

    Default: 100

*   `SAGA_LOCAL_CRON_SCHEDULE`

    The CRON schedule on which to run the task manager for local
    jobs.

    Default: `'*/1 * * * *'` (every minute)

*   `SAGA_REMOTE_CRON_SCHEDULE`

    The CRON schedule on which to run the task manager for remote
    jobs.  This should be set so as not to create too many SSH
    connections for the remote system, nor to overload the system
    with batch system queries.

    Default: `'*/5 * * * *'` (every 5 minutes)


Register tasks with cron
------------------------
The management task which is responsible for processing tasks should be
installed into the system crontab. This can be done by running:

    python manage.py installtasks

You can review the crontab with the command:

    crontab -l

The tasks can be processed on demand by running the task manually:

    python manage.py scheduled_action_runner --local

or

    python manage.py scheduled_action_runner --remote

as appropriate.
