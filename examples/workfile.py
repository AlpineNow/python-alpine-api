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

from api.chorus.datasource import DataSource
from api.chorus.user import User
from api.chorus.workfile import Workfile
from api.chorus.workspace import Workspace

from api.chorus import Chorus
from api.exception import *


def help():
    print "Usage: host=[host] port=[port] user=[username] password=[password]"

def main(chorus_host, chorus_port, username, password):
    chorus_host = chorus_host
    chorus_port = chorus_port
    admin_username = username
    admin_password = password
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
    # Demo Database Info (Greenplum)
    sample_datasource_db_name = "Demo_GP"
    sample_datasource_db_description = "Test Greenplum"
    sample_datasource_db_host = "10.10.0.151"
    sample_datasource_db_port = 5432
    sample_datasource_db_database_name = "miner_demo"
    sample_datasource_db_database_username = "miner_demo"
    sample_datasource_db_database_password = "miner_demo"

    # Demo Hadoop Info (Cloudera CDH5.7)
    sample_datasource_hadoop_name = "Demo_Cloudera"
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
    # Create a chorus session
    chorus_session = Chorus(chorus_host, chorus_port)
    #use chorus logger
    chorus_session.logger.debug("This is a debug message")
    chorus_session.logger.info("This is a info message")
    chorus_session.logger.error("This is a error message")

    # use a custom logger
    custom_logger = logging.getLogger("custom")
    custom_logger.debug("This is a custom debug message")
    custom_logger.info("This is a custom info message")
    custom_logger.error("This is a custom error message")

    # Login with the admin user credential
    chorus_session.login(admin_username, admin_password)

    # Create a datasource_session for datasource management
    datasource_session = DataSource(chorus_session)
    # Create a Greenplum Datasource
    datasource_session.delete_db_data_source_if_exists(sample_datasource_db_name)
    datasource_gp = datasource_session.add_greenplum_data_source(sample_datasource_db_name,
                                                              sample_datasource_db_description,
                                                              sample_datasource_db_host, sample_datasource_db_port,
                                                              sample_datasource_db_database_name,
                                                              sample_datasource_db_database_username,
                                                              sample_datasource_db_database_password)

    # Create a Hadoop datasource
    datasource_session.delete_hadoop_data_source_if_exists(sample_datasource_hadoop_name)

    datasource_hadoop = datasource_session.add_hadoop_data_source(sample_datasource_hadoop_version_string,
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
    # Create a workspace session for workspace management
    workspace_session = Workspace(chorus_session)
    # Delete sample workspaces if exists
    workspace_session.delete_workspace_if_exists(workspace_name=sample_workspace_name)
    # Create a new sample workspace
    workspace_info = workspace_session.create_new_workspace(workspace_name=sample_workspace_name, public=sample_workspace_public_state_true,
                                           summary="")

    # Create a new sample user with admin roles
    user_session = User(chorus_session)
    user_session.delete_user_if_exists(sample_username)
    user_session.create_user(sample_username, sample_password, sample_firstname, sample_lastname, sample_email,
                                 sample_title, sample_deparment, admin=sample_admin_type, user_type=sample_user_type)

    member_list = workspace_session.update_workspace_membership(sample_workspace_name, sample_username, sample_member_role)

    workfile_session = Workfile(chorus_session)
    afm_path = "afm/hadoop_bat_column_filter.afm"
    workfile_session.delete_workfile_if_exists("hadoop_bat_column_filter", workspace_info['id'])
    workfile_info = workfile_session.upload_hdfs_afm(workspace_info['id'], datasource_hadoop['id'], afm_path)
    print "Uploaded Workfile Info: {0}".format(workfile_info)

    variables = [{"name": "@min_credit_line", "value": "7"}]
    process_id = workfile_session.run_workflow(workfile_info['id'], variables)
    workfile_status = None
    max_waiting_seconds = 100
    for i in range(0, max_waiting_seconds):
        workfile_status = workfile_session.query_workflow_status(process_id)
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


    # Delete the Datasource
    #response = datasource_session.delete_db_data_source(sample_datasource_db_database_name)
    #print "Received response code {0} with reason {1}...".format(response.status_code, response.reason)
    #response = datasource_session.delete_hadoop_data_source(sample_datasource_hadoop_name)
    #print "Received response code {0} with reason {1}...".format(response.status_code, response.reason)

    # Delete the workspace
    #response = workspace_session.delete_workspace(sample_workspace_name)
    #print "Received response code {0} with reason {1}...".format(response.status_code, response.reason)

    # Delete the user.
    #response = user_session.delete_user(sample_username)
    #print "Received response code {0} with reason {1}...".format(response.status_code, response.reason)

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