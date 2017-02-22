#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Alpine Data All Rights reserved.
# TODO

"""Simple Command-Line Sample For Alpine API.
Command-line application to login and logout with Alpine API
Usage:
  $ python workfile.py
To get detailed log output run:
  $ python workfile.py --logging_level=DEBUG
"""

import logging
import sys
import time

from api.exception import *
from api.alpine import *


def help():
    print "Usage: host=[host] port=[port] user=[username] password=[password]"


def setUp(alpine_host, alpine_port, username, password):
    global db_data_source_id
    global hadoop_data_source_id
    # Demo Database Info (Greenplum)
    sample_datasource_db_name = "Demo_GP"
    sample_datasource_db_description = "Test Greenplum"
    sample_datasource_db_host = "10.10.0.151"
    sample_datasource_db_port = 5432
    sample_datasource_db_database_name = "miner_demo"
    sample_datasource_db_database_username = "miner_demo"
    sample_datasource_db_database_password = "miner_demo"

    # Demo Hadoop Info (Cloudera CDH5.7)
    sample_datasource_hadoop_name = "Demo_Hadoop"
    sample_datasource_hadoop_version_string = "Cloudera CDH5.4-5.7"
    sample_datasource_hadoop_description = "Test Cloudera"
    sample_datasource_hadoop_namenode_host = "awscdh57singlenode.alpinenow.local"
    sample_datasource_hadoop_namenode_port = 8020
    sample_datasource_hadoop_resource_manager_host = "awscdh57singlenode.alpinenow.local"
    sample_datasource_hadoop_resource_manager_port = 8032
    sample_datasource_hadoop_username = "yarn"
    sample_datasource_hadoop_group_list = "hadoop"
    sample_datasource_hadoop_additional_parameters = [
        {"key": "mapreduce.jobhistory.address", "value": "awscdh57singlenode.alpinenow.local:10020"},
        {"key": "mapreduce.jobhistory.webapp.address", "value": "awscdh57singlenode.alpinenow.local:19888"},
        {"key": "yarn.app.mapreduce.am.staging-dir", "value": "/tmp"},
        {"key": "yarn.resourcemanager.admin.address", "value": "awscdh57singlenode.alpinenow.local:8033"},
        {"key": "yarn.resourcemanager.resource-tracker.address",
         "value": "awscdh57singlenode.alpinenow.local:8031"},
        {"key": "yarn.resourcemanager.scheduler.address", "value": "awscdh57singlenode.alpinenow.local:8030"}
    ]
    alpine_session = Alpine(alpine_host, alpine_port)
    # Login with the admin user credential
    alpine_session.login(username, password)
    alpine_session.datasource.delete_db_data_source_if_exists(sample_datasource_db_name)
    datasource_gp = alpine_session.datasource.add_greenplum_data_source(sample_datasource_db_name,
                                                                        sample_datasource_db_description,
                                                                        sample_datasource_db_host,
                                                                        sample_datasource_db_port,
                                                                        sample_datasource_db_database_name,
                                                                        sample_datasource_db_database_username,
                                                                        sample_datasource_db_database_password)

    # Create a Hadoop datasource
    alpine_session.datasource.delete_hadoop_data_source_if_exists(sample_datasource_hadoop_name)

    datasource_hadoop = alpine_session.datasource.add_hadoop_data_source(sample_datasource_hadoop_version_string,
                                                                         sample_datasource_hadoop_name,
                                                                         sample_datasource_hadoop_description,
                                                                         sample_datasource_hadoop_namenode_host,
                                                                         sample_datasource_hadoop_namenode_port,
                                                                         sample_datasource_hadoop_resource_manager_host,
                                                                         sample_datasource_hadoop_resource_manager_port,
                                                                         sample_datasource_hadoop_username,
                                                                         sample_datasource_hadoop_group_list,
                                                                         sample_datasource_hadoop_additional_parameters
                                                                         )
    db_data_source_id = datasource_gp['id']
    hadoop_data_source_id = datasource_hadoop['id']


def tearDown(alpine_host, alpine_port, username, password):
    sample_datasource_db_name = "Demo_GP"
    sample_datasource_hadoop_name = "Demo_Hadoop"
    sample_username = "test_user"
    sample_workspace_name = "API Sample Workspace"

    alpine_session = Alpine(alpine_host, alpine_port)
    # Login with the admin user credential
    alpine_session.login(username, password)
    # Delete the Datasource
    response = alpine_session.datasource.delete_db_data_source(sample_datasource_db_name)
    print "Received response code {0} with reason {1}...".format(response.status_code, response.reason)
    response = alpine_session.datasource.delete_hadoop_data_source(sample_datasource_hadoop_name)
    print "Received response code {0} with reason {1}...".format(response.status_code, response.reason)

    # Delete the workspace
    response = alpine_session.workspace.delete_workspace(sample_workspace_name)
    print "Received response code {0} with reason {1}...".format(response.status_code, response.reason)

    # Delete the user.
    response = alpine_session.user.delete_user(sample_username)
    print "Received response code {0} with reason {1}...".format(response.status_code, response.reason)


def main(alpine_host, alpine_port, username, password):
    alpine_host = alpine_host
    alpine_port = alpine_port
    # Use the setup function to create datasource for use
    setUp(alpine_host, alpine_port, username, password)
    sample_username = "test_user"
    sample_password = "password"
    sample_firstname = "First"
    sample_lastname = "Last"
    sample_member_role = "Business Analyst"
    sample_email = "test_user@alpinenow.com"
    sample_title = "Title"
    sample_deparment = "Department"
    sample_admin_type = "admin"
    sample_user_type = "analytics_developer"
    sample_workspace_name = "API Sample Workspace"
    sample_workspace_public_state_true = True

    # Create a Alpine session
    # alpine_session = Alpine(alpine_host, alpine_port)
    # alpine_session.login(username, password)
    alpine_session = Alpine(alpine_host, alpine_port, username, password)

    # Logging Examples
    # use default logger
    alpine_session.logger.debug("This is a debug message")
    alpine_session.logger.info("This is a info message")
    alpine_session.logger.error("This is a error message")

    # use a custom logger
    custom_logger = logging.getLogger("custom")
    custom_logger.debug("This is a custom debug message")
    custom_logger.info("This is a custom info message")
    custom_logger.error("This is a custom error message")

    # Workspace Examples
    # Delete sample workspaces if exists
    try:
        workspace_id = alpine_session.workspace.get_id(workspace_name=sample_workspace_name)
        alpine_session.workspace.delete(workspace_id)
    except WorkspaceNotFoundException:
        pass
    # Create a new sample workspace
    workspace_info = alpine_session.workspace.create(workspace_name=sample_workspace_name, public=sample_workspace_public_state_true,
                                           summary="")
    workspace_id = workspace_info['id']
    # User Examples
    # Create a new sample user with admin roles
    try:
        user_id = alpine_session.user.get_id(sample_username)
        alpine_session.user.delete(user_id)
    except UserNotFoundException:
        pass
    user_info = alpine_session.user.create(sample_username, sample_password, sample_firstname, sample_lastname, sample_email,
                                 sample_title, sample_deparment, admin_role=sample_admin_type, app_role=sample_user_type)

    member_list = alpine_session.workspace.member.add(workspace_id, user_info['id'], sample_member_role)

    # Workflow Examples
    afm_path = "afm/demo_hadoop_row_filter_regression.afm"
    try:
        workfile_id = alpine_session.workfile.get_id("demo_hadoop_row_filter_regression", workspace_id)
        alpine_session.workfile.delete(workfile_id)
    except WorkfileNotFoundException:
        pass
    workfile_info = alpine_session.workfile.upload_hdfs_afm(workspace_info['id'], hadoop_data_source_id, afm_path)
    print "Uploaded Workfile Info: {0}".format(workfile_info)

    variables = [{"name": "@min_credit_line", "value": "7"}]
    process_id = alpine_session.workfile.process.run(workfile_info['id'], variables)
    workfile_status = None
    max_waiting_seconds = 100
    for i in range(0, max_waiting_seconds):
        workfile_status = alpine_session.workfile.process.query_status(process_id)
        if workfile_status in ["WORKING"]:
            time.sleep(10)
        elif workfile_status == "FINISHED":
            print "Workfile Finished after waiting for {0} seconds".format(i*10)
            break
        else:
            raise RunFlowFailureException("Workflow run into unexpected stage: {0}".format(workfile_status))
    if workfile_status != "FINISHED":
        raise RunFlowFailureException("Run Flow not Finished after running for {0} seconds"
                                          .format(max_waiting_seconds*10))

    # Use the Tear dowon function to delete the datasource if needed
    # tearDown(alpine_host, alpine_port, username, password)


if __name__ == '__main__':
    self = sys.modules['__main__']
    if len(sys.argv) >= 5:
        host = sys.argv[1].split('=')[1]
        port = sys.argv[2].split('=')[1]
        username = sys.argv[3].split('=')[1]
        password = sys.argv[4].split('=')[1]
        main(host, port, username,password)
    else:
        help()