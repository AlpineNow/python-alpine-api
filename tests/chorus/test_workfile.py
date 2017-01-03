from chorusunittest import ChorusTestCase
from api.chorus.chorus import Chorus
from api.chorus.workfile import Workfile
import time


class TestWorkfile(ChorusTestCase):

    def test_get_workfiles_list(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile = Workfile(chorus_session)
        workfile_list = workfile.get_workfiles_list(1)
        self.assertIsNotNone(workfile_list)
        #TODO add more validation for this test

    def test_get_workfile_details(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile = Workfile(chorus_session)
        workfile_info = workfile.get_workfile_details("Madlib_6.2", 1)
        self.assertIsNotNone(workfile_info)
        #TODO add more validation

    def test_get_workfile_id(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile = Workfile(chorus_session)
        workfile_id = workfile.get_workfile_id("Madlib_6.2", 1)
        self.assertIsNotNone(workfile_id)
        # TODO add more validation

    def test_run_workflow(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile = Workfile(chorus_session)
        response = workfile.run_workflow("test_row_filter_hd", 2, variables)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()['response']['status'], "running")

    def test_query_workflow_status(self):
        valid_workfile_status = ["running","idle"]
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile = Workfile(chorus_session)
        response = workfile.run_workflow("test_row_filter_hd", 2, variables)
        self.assertEqual(response.json()['response']['status'], "running")
        for i in range(0, 100):
            workfile_status = workfile.query_workflow_status("test_row_filter_hd",2)
            if workfile_status in valid_workfile_status:
                time.sleep(1)
            else:
                self.fail("Invalid workfile status {0}".format(workfile_status))

    def test_stop_workflow(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile = Workfile(chorus_session)
        workfile.run_workflow("test_row_filter_hd", 2)
        response = workfile.stop_workflow("test_row_filter_hd", 2)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()['response']['status'], "idle")

    def test_download_workflow_results(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile = Workfile(chorus_session)
        workfile.get_workflow_results("test_row_filter_hd", 2)

    def test_get_running_workflows(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        workfile = Workfile(chorus_session)
        response = workfile.run_workflow("test_row_filter_hd", 2, variables)
        workfile.get_running_workflows()

    def test_test_logging(self):
        chorus_session = Chorus(self.host, self.port)
        workfile = Workfile(chorus_session)
        workfile.test_logging()

