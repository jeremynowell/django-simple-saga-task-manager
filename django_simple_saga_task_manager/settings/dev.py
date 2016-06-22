import os

from django_simple_saga_task_manager.settings.base import *

MEDIA_ROOT = os.path.join(BASE_DIR, 'dev')

LOGGING = {
           'version': 1,
           'disable_existing_loggers': False,
           'formatters': {
                          'verbose': {
                                      'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                                      'datefmt': "%d/%b/%Y %H:%M:%S",
                                      },
                          'simple': {
                                     'format': '%(levelname)s %(message)s',
                                     },
                          },
           'handlers': {
                        'file': {
                                 'level': 'DEBUG',
                                 'class': 'logging.FileHandler',
                                 'filename': 'simple_task_manager.log',
                                 'formatter': 'verbose',
                                 },
                        'console': {
                                    'level': 'DEBUG',
                                    'class': 'logging.StreamHandler',
                                    'formatter': 'simple',
                                    },
                        },
           'loggers': {
                       'django': {
                                  'handlers': ['file'],
                                  'propagate': True,
                                  'level': 'ERROR',
                                  },
                       'django_simple_saga_task_manager': {
                                               'handlers': ['file', 'console'],
                                               'level': 'DEBUG',
                                               },
                       },

           }
