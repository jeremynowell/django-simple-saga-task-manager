import os

DEBUG = True

SAGA_BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k_*i8rk62-_3g$)05_-g&ea&)*6_e5%77!v6+^oxwm@)tpgwb9'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_simple_saga_task_manager',
    'widget_tweaks',
    'kronos',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings1/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(SAGA_BASE_DIR, 'db.sqlite3'),
    }
}

# Default settings. Will be included if not
# present in app settings file.
# Standard out file name
SAGA_STD_OUT = 'task.stdout'

# Standard error file name
SAGA_STD_ERR = 'task.stderr'

# user name for keystore
SAGA_REMOTE_USER = 'cdes'

# public part of ssh key
SAGA_REMOTE_SSH_KEY = '/home/cdes/.ssh/id_rsa.pub'

# private part of ssh key
SAGA_REMOTE_SSH_CERT = '/home/cdes/.ssh/id_rsa'

# private key password
SAGA_REMOTE_SSH_KEY_PASS = 'ppabewSEDC'

# saga url of execution host, ie adapter plus ssh host
SAGA_REMOTE_HOST = 'indy0.epcc.ed.ac.uk'

# saga job adapter for remote machine
SAGA_REMOTE_JOB_ADAPTER = 'lsf+ssh'

# working dir for locally executed tasks
SAGA_LOCAL_WORKING_DIR = '/home/cdes/tasks'

# working dir for remotely executed tasks
SAGA_REMOTE_WORKING_DIR = '/home/w42/cdes/tasks'

# Maximum number of local jobs to allow at once
SAGA_MAX_LOCAL_JOBS = 4

# Maximum number of remote jobs to allow at once
SAGA_MAX_REMOTE_JOBS = 100

# Schedule for local jobs
SAGA_LOCAL_CRON_SCHEDULE = '*/1 * * * *'

# Schedule for remote jobs
SAGA_REMOTE_CRON_SCHEDULE = '*/5 * * * *'

# Test Settings
# Input file relative to tests/resources directory
SAGA_TEST_LOCAL_PYTHON_PATH = '/home/cdes/CDES_Fortissimo_Unix'
SAGA_TEST_REMOTE_PYTHON_PATH = '/home/w42/cdes/CDES_Fortissimo_Unix'
SAGA_TEST_REMOTE_ENVIRONMENT = {
                                'PYTHONPATH': SAGA_TEST_REMOTE_PYTHON_PATH,
                                'PATH': '/home/w42/cdes/anaconda2/bin:$PATH',
                                'LD_LIBRARY_PATH': '/home/w42/cdes/anaconda2/lib:$LD_LIBRARY_PATH'
                                }
SAGA_TEST_PYTHON_SCRIPT = 'cmsd2simulation/tasks/simulation_task.py'
SAGA_TEST_PYTHON_ARGS = [
                         '--cmsdxml 140103_VSM_Ceramic_ProcessR33.xlsm.xml',
                         '--numrep 2',
                         '--simtime 1000',
                         '--incp 50',
                         '--warmup 950',
                         '--ci 0.95'
                         ]
SAGA_TEST_INPUT_FILE = '/home/cdes/CDES_Fortissimo_Unix/resources/140103_VSM_Ceramic_ProcessR33.xlsm.xml'
SAGA_TEST_OUTPUT_FILE = 'updatedProduceSales.xlsx'
