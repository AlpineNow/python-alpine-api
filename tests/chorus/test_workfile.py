from chorusunittest import ChorusTestCase
from api.chorus.chorus import Chorus
from api.chorus.workfile import Workfile
import time
import os


class TestWorkfile(ChorusTestCase):

    def test_get_workfiles_list(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        workfile_list = workfile_session.get_workfiles_list(1)
        self.assertIsNotNone(workfile_list)
        #TODO add more validation for this test

    def test_get_workfile_details(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        workfile_info = workfile_session.get_workfile_info("Madlib_6.2", 1)
        self.assertIsNotNone(workfile_info)
        #TODO add more validation

    def test_get_workfile_id(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        workfile_id = workfile_session.get_workfile_id("Madlib_6.2", 1)
        self.assertIsNotNone(workfile_id)
        # TODO add more validation

    def test_run_workflow(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        response = workfile_session.run_workflow("test_row_filter_hd", 2, variables)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()['response']['status'], "running")

    def test_query_workflow_status(self):
        valid_workfile_status = ["running","idle"]
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        response = workfile_session.run_workflow("test_row_filter_hd", 2, variables)
        self.assertEqual(response.json()['response']['status'], "running")
        for i in range(0, 100):
            workfile_status = workfile_session.query_workflow_status("test_row_filter_hd",2)
            if workfile_status in valid_workfile_status:
                time.sleep(1)
            else:
                self.fail("Invalid workfile_session status {0}".format(workfile_status))

    def test_stop_workflow(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        workfile_session.run_workflow("test_row_filter_hd", 2)
        response = workfile_session.stop_workflow("test_row_filter_hd", 2)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()['response']['status'], "idle")

    def test_download_workflow_results(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        workfile_session.get_workflow_results("test_row_filter_hd", 2)

    def test_get_running_workflows(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        response = workfile_session.run_workflow("test_row_filter_hd", 2, variables)
        workfile_session.get_running_workflows()

    def test_upload_hdfs_afm(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        base_dir = os.getcwd()
        afm_path = "{0}/../data/afm/hadoop_bat_column_filter.afm".format(base_dir)
        #afm_path = "hadoop_bat_column_filter.afm"
        workfile_session.delete_workfile_if_exists("hadoop_bat_column_filter", 2)
        workfile_info = workfile_session.upload_hdfs_afm(2, 1, afm_path)
        self.assertEqual(workfile_info['file_name'], "hadoop_bat_column_filter")

    def test_upload_db_afm(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        base_dir = os.getcwd()
        afm_path = "{0}/../data/afm/db_bat_row_fil.afm".format(base_dir)
        #afm_path = "db_bat_row_fil.afm"
        workfile_session.delete_workfile_if_exists("db_bat_row_fil", 2)

        workfile_info = workfile_session.upload_db_afm(2, 1, 1, "GpdbDataSource", "gpdb_database", afm_path)
        self.assertEqual(workfile_info['file_name'], "db_bat_row_fil")

