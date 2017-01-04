#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Alpine Data All Rights reserved.
# TODO

"""Simple Command-Line Sample For Alpine API.
Command-line application to login and logout with Alpine API
Usage:
  $ python workspace.py
To get detailed log output run:
  $ python workspace.py --logging_level=DEBUG
"""

__author__ = 'ggao@alpinenow.com (Guohui Gao)'

import sys
from api.chorus.chorus import Chorus
from api.chorus.user import User
from api.chorus.workspace import Workspace
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
    sample_member_role = "Business Analyst"
    sample_email = "test_user@alpinenow.com"
    sample_title = "Title"
    sample_deparment = "Department"
    sample_admin_type = "admin"
    sample_user_type = "analytics_developer"
    sample_workspace_name = "API Sample Workspace"
    sample_workspace_public_state_false = False
    sample_workspace_public_state_true = True
    sample_workspace_stage = 2



    # Create a chorus session
    chorus_session = Chorus(chorus_host, chorus_port)
    # Login with the admin user credential
    chorus_session.login(admin_username, admin_password)

    # Create a workspace session for workspace management
    workspace_session = Workspace(chorus_session)
    # Delete sample workspaces if exists
    workspace_session.delete_workspace_if_exists(workspace_name=sample_workspace_name)
    # Create a new sample workspace
    workspace_info = workspace_session.create_new_workspace(workspace_name=sample_workspace_name, public=sample_workspace_public_state_true,
                                           summary="")
    print "Created Workspace Info: {0}".format(workspace_info)

    # Update workspace info.
    workspace_info_updated = workspace_session.update_workspace_details(sample_workspace_name, sample_workspace_public_state_false,
                                                                is_active=True, summary="New Summary",
                                                                stage_id=sample_workspace_stage)
    print "Updated Workspace Info: {0}".format(workspace_info_updated)

    workspace_info = workspace_session.get_workspace_info(sample_workspace_name)
    print "Getting Workspace Info: {0}".format(workspace_info)

    # Create a new sample user with admin roles
    user_session = User(chorus_session)
    user_session.delete_user_if_exists(sample_username)
    user_session.create_user(sample_username, sample_password, sample_firstname, sample_lastname, sample_email,
                                 sample_title, sample_deparment, admin=sample_admin_type, user_type=sample_user_type)

    member_list = workspace_session.update_workspace_membership(sample_workspace_name, sample_username, sample_member_role)


    # Delete the workspace
    #response = workspace_session.delete_workspace(sample_workspace_name)
    #print "Received response code {0} with reason {1}...".format(response.status_code, response.reason)

    # Delete the user.
    #response = user_session.delete_user(sample_username)
    #print "Received response code {0} with reason {1}...".format(response.status_code, response.reason)


if __name__ == '__main__':
  main(sys.argv)