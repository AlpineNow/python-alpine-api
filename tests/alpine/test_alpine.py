from tests.chorus.chorusunittest import ChorusTestCase
from api.alpine.alpine import *
import time


class TestAlpine(ChorusTestCase):

    def test_clear_step_run_results(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        alpine = Alpine(chorus_session)
        process_id = alpine.run_workflow(15, variables)
        workfile_status = alpine.query_workflow_status(process_id)
        while workfile_status != "FINISHED":
            time.sleep(1)
            workfile_status = alpine.query_workflow_status(process_id)
        response = alpine.download_workflow_results(15, process_id)
        alpine.clear_step_run_results()
        process_id = alpine.run_workflow(15, variables)
        while workfile_status != "FINISHED":
            time.sleep(1)
            workfile_status = alpine.query_workflow_status(process_id)
        response = alpine.download_workflow_results(15, process_id)

    def test_run_workflow(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        alpine = Alpine(chorus_session)
        alpine.run_workflow(15, variables)

    def test_query_workflow_status(self):
        valid_workfile_status = ["WORKING", "FINISHED"]
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        alpine = Alpine(chorus_session)
        process_id = alpine.run_workflow(15, variables)
        for i in range(0, 100):
            workfile_status = alpine.query_workflow_status(process_id)
            if workfile_status in valid_workfile_status:
                time.sleep(1)
            else:
                self.fail("Invalid workfile status {0}".format(workfile_status))

    def test_download_workflow_results(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        alpine = Alpine(chorus_session)
        process_id = alpine.run_workflow(15, variables)
        workfile_status = alpine.query_workflow_status(process_id)
        while workfile_status != "FINISHED":
            time.sleep(1)
            workfile_status = alpine.query_workflow_status(process_id)
        response =alpine.download_workflow_results(15, process_id)

    def test_stop_workflow(self):
        variables = [{"name": "@min_credit_line", "value": "7"}]
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        alpine = Alpine(chorus_session)
        process_id = alpine.run_workflow(15, variables)
        finish_state =alpine.stop_workflow(process_id)
        self.assertEqual(finish_state, "FINISHED")