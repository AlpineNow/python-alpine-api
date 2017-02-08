#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Alpine Data All Rights reserved.
# TODO

"""Simple Command-Line Sample For Alpine API.
Command-line application to login and logout with Alpine API
Usage:
  $ python delete_multiple_users.py
To get debug log output run:
  $ python delete_multiple_users.py --logging_level=DEBUG
"""

import logging
import sys
import time

from api.exception import *
from api.alpine import *


if __name__ == '__main__':
    self = sys.modules['__main__']
    if len(sys.argv) >= 2:
        help()
    else:
        # host = raw_input(">>> Host: ")
        # port = raw_input(">>> Host: ")
        # username = raw_input("Login User: ")
        # password = raw_input("Password: ")
        host = "10.10.0.204"
        port = "8080"
        username = "chorusadmin"
        password = "secret"
        alpine = Alpine(host, port)
        alpine.login(username, password)
        # alpine = Alpine(host, port, username, password)
        while True:
            input_option = raw_input("Please select the following option number or 'q' to exit: \n"
                        "1. view a list of users.\n"
                        "2. view info of a user.\n"
                        "3. delete users.\n");
            if input_option == 'q':
                break
            if input_option == '1':
                user_list = alpine.user.get_all()
                for user in reversed(user_list):
                    alpine.logger.debug("{0}\t{1}\t{2}\t{3}".format(user['id'], user['username'], user['email'], user['admin'], user['user_type']))
                print 1
            elif input_option == '2':
                print 2
            elif input_option == '3':
                print 3
            else:
                print "Invalid Input"
            print "Received input is : ", input_option
