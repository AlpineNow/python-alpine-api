#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Alpine Data All Rights reserved.
# Sample

"""Simple Command-Line Sample For Alpine API.
Command-line application to login and logout with Alpine API
Usage:
  $ python users.py
To get debug log output run:
  $ python users.py --logging_level=DEBUG
"""

from api.exception import *
from api.alpine import *


if __name__ == '__main__':
    self = sys.modules['__main__']
    #host = raw_input(">>> Host: ")
    #port = raw_input(">>> Port: ")
    #username = raw_input(">>> Login User: ")
    #password = raw_input(">>> Password: ")
    host = "10.10.0.204"
    port = "8080"
    username = "demoadmin"
    password = "password"
    alpine = Alpine(host, port)
    alpine.login(username, password)
    # alpine = Alpine(host, port, username, password)
    while True:
        # input_option = raw_input("Press Enter to Continue...")
        print "----------------------------------------------------------------"
        input_option = raw_input("Please select the number of functions you want to use: \n"
                                 "1. view the list of users.\n"
                                 "2. view info of a user.\n"
                                 "3. delete users.\n"
                                 "q. exit.\n")
        if input_option == 'q':
            break
        if input_option == '1':
            user_list = alpine.user.get_list()
            print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format("User_ID", "User Name", "Email","First Name",
                                                                  "Last Name", "App Role", "Department", "Title"))
            for user in sorted(user_list, key=lambda x: x['id'], reverse=True):
                print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(user['id'], user['username'], user['email'],
                                                                      user['first_name'], user['last_name'],
                                                                      user['user_type'],user['dept'],user['title']))
        elif input_option == '2':
            user_name = raw_input(">>> username: ")
            try:
                user_id = alpine.user.get_id(user_name)
                user = alpine.user.get(user_id)
                print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format("User_ID", "User Name", "Email","First Name",
                                                                      "Last Name", "App Role", "Department", "Title"))
                print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(user['id'], user['username'], user['email'],
                                                                      user['first_name'], user['last_name'],
                                                                      user['user_type'], user['dept'],user['title']))
            except UserNotFoundException:
                print("User '{0}' Not Found".format(user_name))

        elif input_option == '3':
            user_names = raw_input(">>> Please enter user names to be deleted, split by ',' : ")
            for user_name in user_names.split(','):
                if not user_name:
                    continue
                try:
                    delete_safe_flag = True
                    user_id = alpine.user.get_id(user_name)
                    # Check whether there are any workspace owned by the user
                    workspace_list = alpine.workspace.get_list(user_id)
                    if workspace_list:
                        for workspace in workspace_list:
                            workspace['owner']['username']
                            if workspace['owner']['username'] == user_name:
                                delete_safe_flag = False
                                print "User '{0}' is owner of workspace '{1}', Please transfer ownership of " \
                                      "active workspaces to another person.".format(user_name, workspace['name'])
                    # Check whether there are any Datasource owned by the user
                    db_database_list = alpine.datasource.get_db_data_source_list()
                    if db_database_list:
                        for db_datasource in db_database_list:
                            if db_datasource['owner']['username'] == user_name:
                                delete_safe_flag = False
                                print "User '{0}' is owner of data source '{1}', Please transfer ownership of " \
                                      "the data source to another person.".format(user_name, db_datasource['name'])
                    # Delete the user when it is safe to do so.
                    if delete_safe_flag:
                        alpine.user.delete(user_id)
                        print "User '{0}' successfully deleted".format(user_name)
                except UserNotFoundException:
                    print "User '{0}' not found, please double check the username exists".format(user_name)
                    continue
        else:
            print "Invalid Input"
