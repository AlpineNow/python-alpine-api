import os
import time

from api.alpine import Alpine
from api.workfile import Workfile

from alpineunittest import AlpineTestCase


class TestWorkfile(AlpineTestCase):

    def setUp(self):
        super(TestWorkfile, self).setUp()
        global workspace_id
        global data_source_id
        global workfile_id
        global hadoop_datasource_id
        # Creating a Workspace for Job tests
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.workspace.delete_workspace_if_exists("Workspace for Workfile Tests")
        workspace_info = alpine_session.workspace.create_new_workspace("Workspace for Workfile Tests")
        alpine_session.datasource.delete_db_data_source_if_exists("GP_For_Workfile_Test")
        datasource = alpine_session.datasource.add_greenplum_data_source("GP_For_Workfile_Test", "Test Greenplum", "10.10.0.151",
                                                                         5432,
                                                                         "miner_demo", "miner_demo", "miner_demo")
        workspace_id = workspace_info['id']
        data_source_id = datasource['id']
        # Creating a Hadoop Datasource for test get/update functions
        alpine_session.datasource.delete_hadoop_data_source_if_exists("Test_Cloudera")
        additional_parameters = [
            {"key": "mapreduce.jobhistory.address", "value": "awscdh57singlenode.alpinenow.local:10020"},
            {"key": "mapreduce.jobhistory.webapp.address", "value": "awscdh57singlenode.alpinenow.local:19888"},
            {"key": "yarn.app.mapreduce.am.staging-dir", "value": "/tmp"},
            {"key": "yarn.resourcemanager.admin.address", "value": "awscdh57singlenode.alpinenow.local:8033"},
            {"key": "yarn.resourcemanager.resource-tracker.address",
             "value": "awscdh57singlenode.alpinenow.local:8031"},
            {"key": "yarn.resourcemanager.scheduler.address", "value": "awscdh57singlenode.alpinenow.local:8030"}
        ]
        datasource_hadoop = alpine_session.datasource.add_hadoop_data_source("Cloudera CDH5.4-5.7", "Test_Cloudera",
                                                                             "Test Cloudera",
                                                                             "awscdh57singlenode.alpinenow.local", 8020,
                                                                             "awscdh57singlenode.alpinenow.local", 8032,
                                                                             "yarn", "hadoop", additional_parameters
                                                                             )

        hadoop_datasource_id = datasource_hadoop['id']

        base_dir = os.getcwd()
        afm_path = "{0}/../data/afm/db_row_fil_with_variable.afm".format(base_dir)
        # afm_path = "db_bat_row_fil.afm"
        alpine_session.workfile.delete_workfile_if_exists("db_row_fil_with_variable",workspace_id)

        workfile_info = alpine_session.workfile.upload_db_afm(workspace_id, data_source_id, 1, "GpdbDataSource", "gpdb_database", afm_path)
        workfile_id = workfile_info['id']
        alpine_session.logout

    def tearDown(self):
        # Drop the datasources created in setup
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        #alpine_session.workspace.delete_workspace_if_exists("Workspace for Workfile Tests")

    def test_get_workfiles_list(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        workfile_list = alpine_session.workfile.get_workfiles_list(workspace_id)
        self.assertIsNotNone(workfile_list)
        self.assertEqual(workfile_list.__len__(), 1)

    def test_get_workfile_info(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        workfile_info = alpine_session.workfile.get_workfile_info("db_row_fil_with_variable", workspace_id)
        self.assertIsNotNone(workfile_info)

    def test_get_workfile_id(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        id = alpine_session.workfile.get_workfile_id("db_row_fil_with_variable", workspace_id)
        self.assertIsNotNone(workfile_id)
        self.assertEqual(workfile_id, id)

        # TODO add more validation

    def test_run_workflow(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        process_id = alpine_session.workfile.run_workflow(workfile_id, variables)
        alpine_session.workfile.wait_for_workflow_finished(process_id)

    def test_query_workflow_status(self):
        valid_workfile_status = ["WORKING", "FINISHED"]
        variables = [{"name": "@min_credit_line", "value": "7"}]
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        process_id = alpine_session.workfile.run_workflow(workfile_id, variables)
        for i in range(0, 100):
            workfile_status = alpine_session.workfile.query_workflow_status(process_id)
            if workfile_status in valid_workfile_status:
                if workfile_status == "FINISHED":
                    break
                else:
                    time.sleep(1)
            else:
                self.fail("Invalid workfile status {0}".format(workfile_status))

    def test_download_workflow_results(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        process_id = alpine_session.workfile.run_workflow(workfile_id, variables)
        workfile_status = alpine_session.workfile.query_workflow_status(process_id)
        while workfile_status != "FINISHED":
            time.sleep(1)
            workfile_status = alpine_session.workfile.query_workflow_status(process_id)
        response = alpine_session.workfile.download_workflow_results(workfile_id, process_id)

    def test_stop_workflow(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        process_id = alpine_session.workfile.run_workflow(workfile_id, variables)
        finish_state = alpine_session.workfile.stop_workflow(process_id)
        self.assertEqual(finish_state, "FINISHED")

    def test_upload_hdfs_afm(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        base_dir = os.getcwd()
        afm_path = "{0}/../data/afm/demo_hadoop_row_filter_regression.afm".format(base_dir)
        #afm_path = "demo_hadoop_row_filter_regression.afm"
        alpine_session.workfile.delete_workfile_if_exists("demo_hadoop_row_filter_regression", workspace_id)
        workfile_info = alpine_session.workfile.upload_hdfs_afm(workspace_id,hadoop_datasource_id, afm_path)
        self.assertEqual(workfile_info['file_name'], "demo_hadoop_row_filter_regression")

    def test_upload_db_afm(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        base_dir = os.getcwd()
        afm_path = "{0}/../data/afm/db_bat_row_fil.afm".format(base_dir)
        #afm_path = "db_bat_row_fil.afm"
        alpine_session.workfile.delete_workfile_if_exists("db_bat_row_fil", workspace_id)

        workfile_info = alpine_session.workfile.upload_db_afm(workspace_id, data_source_id, 1, "GpdbDataSource", "gpdb_database", afm_path)
        self.assertEqual(workfile_info['file_name'], "db_bat_row_fil")
