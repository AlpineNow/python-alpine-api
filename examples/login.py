#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Alpine Data All Rights reserved.
# TODO

"""Simple Command-Line Sample For Alpine Login.
Command-line application to login and logout with Alpine API
Usage:
  $ python login.py
To get detailed log output run:
  $ python user.py --logging_level=DEBUG
"""

__author__ = 'ggao@alpinenow.com (Guohui Gao)'

import sys
from api.chorus.chorus import Chorus
from api.exception import *

def main(argv):
    chorus_host = "10.10.0.204"
    chorus_port = "8080"
    admin_username = "chorusadmin"
    admin_password = "secret"

    # Create a chorus session
    chorus_session = Chorus(chorus_host, chorus_port)
    # Login with the admin user credential
    chorus_session.login(admin_username, admin_password)

if __name__ == '__main__':
  main(sys.argv)