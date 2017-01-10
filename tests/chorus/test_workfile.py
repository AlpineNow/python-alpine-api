import os
import time

from api.chorus.workfile import Workfile

from api.chorus import Chorus
from chorusunittest import ChorusTestCase


class TestWorkfile(ChorusTestCase):

    def test_get_workfiles_list(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        workfile_list = workfile_session.get_workfiles_list(1)
        self.assertIsNotNone(workfile_list)
        #TODO add more validation for this test

    def test_get_workfile_info(self):
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
        process_id = workfile_session.run_workflow(15, variables)
        workfile_session.wait_for_workflow_finished(process_id)

    def test_query_workflow_status(self):
        valid_workfile_status = ["WORKING", "FINISHED"]
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        process_id = workfile_session.run_workflow(15, variables)
        for i in range(0, 100):
            workfile_status = workfile_session.query_workflow_status(process_id)
            if workfile_status in valid_workfile_status:
                if workfile_status == "FINISHED":
                    break
                else:
                    time.sleep(1)
            else:
                self.fail("Invalid workfile status {0}".format(workfile_status))

    def test_download_workflow_results(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        process_id = workfile_session.run_workflow(15, variables)
        workfile_status = workfile_session.query_workflow_status(process_id)
        while workfile_status != "FINISHED":
            time.sleep(1)
            workfile_status = workfile_session.query_workflow_status(process_id)
        response = workfile_session.download_workflow_results(15, process_id)

    def test_stop_workflow(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile_session = Workfile(chorus_session)
        process_id = workfile_session.run_workflow(15, variables)
        finish_state = workfile_session.stop_workflow(process_id)
        self.assertEqual(finish_state, "FINISHED")

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
