#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Alpine Data All Rights reserved.
# TODO

"""Simple Command-Line Sample For Alpine API.
Command-line application to login and logout with Alpine API
Usage:
  $ python user.py
To get detailed log output run:
  $ python user.py --logging_level=DEBUG
"""

__author__ = 'ggao@alpinenow.com (Guohui Gao)'

import sys
from api.chorus.chorus import Chorus
from api.chorus.user import User
from api.exception import *

def main(argv):
    chorus_host = "10.10.0.204"
    chorus_port = "8080"
    admin_username = "chorusadmin"
    admin_password = "secret"
    sample_username = "test_user"
    sample_password = "secret"
    sample_firstname = "First"
    sample_lastname = "Last"
    sample_firstname_update = "First Name Updated"
    sample_email = "test_user@alpinenow.com"
    sample_title = "Title"
    sample_deparment = "Department"
    sample_admin_type = "admin"
    sample_user_type = "analytics_developer"

    # Create a chorus session
    chorus_session = Chorus(chorus_host, chorus_port)
    # Login with the admin user credential
    chorus_session.login(admin_username, admin_password)

    # Create a user session for user management
    user_session = User(chorus_session)
    # Create a new sample user with admin roles
    user_info = user_session.create_user(sample_username, sample_password, sample_firstname, sample_lastname, sample_email,
                                 sample_title, sample_deparment, admin=sample_admin_type, user_type=sample_user_type)
    print "Created User Info: {0}".format(user_info)

    # Update user info
    user_info_updated = user_session.update_user_info(sample_username, first_name=sample_firstname_update)
    print "Updated User Info: {0}".format(user_info_updated)

    # Get the user info
    user_info = user_session.get_user_info(sample_username)
    print "User Info: {0}".format(user_info)

    # Delete the user.
    response = user_session.delete_user(sample_username)
    print "Received response code {0} with reason {1}...".format(response.status_code, response.reason)


if __name__ == '__main__':
  main(sys.argv)