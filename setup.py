#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
from idoit_api.__about__ import __version__

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'requests>=2.23.0']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', 'pytest-mock>=3.1.1', 'requests-mock>=1.8.0']

setup(
    author="Andre Machon",
    author_email='ajbmachon2@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="idoit json api client library",
    entry_points={
        'console_scripts': [
            'idoit_api=idoit_api.cli:main',
            'cmdb=idoit_api.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='idoit_api',
    name='idoit_api',
    packages=find_packages(include=['idoit_api', 'idoit_api.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ajbmachon/idoit_api',
    version=__version__,
    zip_safe=False,
)
