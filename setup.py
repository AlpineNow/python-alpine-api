#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed to Alpine Data, Inc.
# TODO
# Copyright 2017 Alpine Data All Rights reserved.

from __future__ import print_function

try:
    from setuptools import setup, find_packages
    extra = {}
except ImportError:
    from distutils.core import setup
    extra = {}

import sys
if sys.version_info <= (2, 5):
    error = "ERROR: boto requires Python Version 2.6 or above...exiting."  # TODO
    print(error, file=sys.stderr)
    sys.exit(1)
    # TBD

install_requires = [
    'requests >= 2.13.0',
    ]

def readme():
    with open("README.md") as f:
        return f.read()

setup(
    name="alpineapi",
    version='0.0.1',
    description="Alpine Web API Client",
    long_description=readme(),
    author="Alpine Data, Inc.",
    author_email="ggao@alpinenow.com",
    keywords='alpine api sdk chorus',
    url="https://github.com/alpinedatalabs/python-alpine-api",
    package_data={
        "alpineapi": ["logging.json"],
    },
    install_requires=install_requires,

    license="TODO",       #TODO
    platforms="Linux; MacOS X; Windows",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",                 # TODO
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Programming Language :: Python :: 2.6",           # TODO
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4"            # TODO
    ],
    include_package_data=True,
    zip_safe=False,

    test_suite='tests.api',
    tests_require=['nose'],
    **extra
)