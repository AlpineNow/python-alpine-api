#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed to Alpine Data, Inc.
# Copyright 2017 Alpine Data All Rights reserved.

from __future__ import print_function
import os

version_major = 0
version_minor = 0
version_build = 1

# For jenkins packaging to pass version number.
# Adding the following step in jenkins for the build number
#   echo $BUILD_NUMBER > build.info
def __path(filename):
    return os.path.join(os.path.dirname(__file__),
                        filename)
if os.path.exists(__path('build.info')):
    build = open(__path('build.info')).read().strip()

if os.path.exists(__path('build.info')):
    version_build = open(__path('build.info')).read().strip()
# -----

try:
    from setuptools import setup, find_packages
    extra = {}
except ImportError:
    from distutils.core import setup
    extra = {}

import sys
if sys.version_info <= (2, 6):
    error = "ERROR: alpine requires Python Version 2.7 or above...exiting."
    print(error, file=sys.stderr)
    sys.exit(1)
    # TBD

install_requires = [
    'requests >= 2.13.0',
    'pytz',
    ]

def readme():
    with open("README.rst") as f:
        return f.read()

setup(
    name="alpine",
    version='{0}.{1}.{2}'.format(version_major, version_minor, version_build),
    description="Alpine Web API Client",
    long_description=readme(),
    author="Alpine Data, Inc.",
    author_email="ggao@alpinenow.com",
    keywords='alpine api sdk chorus',
    url="https://github.com/AlpineNow/python-alpine-api",
    packages=find_packages(exclude=['future', 'doc', "examples", 'tests*']),

    package_data={
        "alpine": ["logging.json"],
    },
    package_dir = {
        'alpine': 'alpine',
    },

    install_requires=install_requires,

    license="MIT License",
    platforms="Linux; MacOS X; Windows",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",

    ],
    include_package_data=True,
    zip_safe=False,

    test_suite='tests.api',
    tests_require=['nose'],
    **extra
)
