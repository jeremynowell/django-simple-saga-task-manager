import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-simple-saga-task-manager',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='Apache 2.0 License',
    description='A simple Django app to conduct Web-based polls.',
    long_description=README,
    url='http://www.epcc.ed.ac.uk/',
    author='Jeremy Nowell and Malcolm Illingworth, EPCC, The University of Edinburgh',
    author_email='jeremy@epcc.ed.ac.uk',
    install_requires=[
                      'saga_python',
                      'django',
                      'django-picklefield',
                      'django-widget-tweaks',
                      'django-kronos',
                      ],
    classifiers=[
                 'Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Framework :: Django :: 1.8',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: Apache Software License',
                 'Operatins System :: POSIX :: Linux',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Communication',
                 'Topic :: Internet',
                 'Topic :: Internet :: WWW/HTTP',
                 'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Utilities',
    ],
)
