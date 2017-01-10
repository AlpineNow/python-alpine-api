from api.chorus.job import Job

from api.chorus import Chorus
from api.exception import *
from chorusunittest import ChorusTestCase


class TestJob(ChorusTestCase):

    def test_get_jobs_list(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        job_session = Job(chorus_session)
        jobs_list = job_session.get_jobs_list(1)
        self.assertIsNotNone(jobs_list)

    def test_get_job_detail(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        job_session = Job(chorus_session)
        job_detail = job_session.get_job_info(1, "test")
        self.assertEqual(job_detail['name'], "test")

    def test_get_job_id(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        job_session = Job(chorus_session)
        job_session.delete_job_from_workspace_if_exists(1, "test")
        job_info=job_session.add_job(1, "test")
        job_id = job_session.get_job_id(1, "test")
        self.assertEqual(job_id, job_info['id'])

    def test_add_job(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        job_session = Job(chorus_session)
        job_session.delete_job_from_workspace_if_exists(1, "test")
        job_info = job_session.add_job(1, "test", "on_demand", 0, "")
        self.assertIsNotNone(job_info)

    def test_delete_job_from_workspace(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        job_session = Job(chorus_session)
        job_session.delete_job_from_workspace_if_exists(1, "test")
        job_session.add_job(1, "test")
        response = job_session.delete_job_from_workspace(1, "test")
        self.assertEqual(response.status_code, 200)
        # Verify the Job is successfully deleted
        try:
            job_session.get_job_info(1, "test")
        except JobNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Job {0}".format("test"))

    def test_get_tasks_on_a_job(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        job_session = Job(chorus_session)
        #job_session.delete_job_from_workspace_if_exists(1, "test")
        #job_session.add_job(1, "test")
        tasks_list = job_session.get_tasks_on_a_job(1, "test")
        self.assertIsNotNone(tasks_list)

    def test_add_workfile_task(self):
        self.fail()

    def test_add_workflow_task(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        job_session = Job(chorus_session)
        job_session.delete_job_from_workspace_if_exists(1, "test")
        job_session.add_job(1, "test")
        task_info = job_session.add_workflow_task(1, "test", 2)
        self.assertIsNotNone(task_info)

    def test_add_sqlworkfile_task(self):
        self.fail()

    def test_get_task_info(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        job_session = Job(chorus_session)
        job_session.delete_job_from_workspace_if_exists(1, "test")
        job_session.add_job(1, "test")
        task_info1 =job_session.add_workflow_task(1, "test", 2)
        task_info = job_session.get_task_info(1, "test", "Madlib_6.2")
        self.assertEqual(task_info1, task_info)

    def test_get_task_id(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        job_session = Job(chorus_session)
        job_session.delete_job_from_workspace_if_exists(1, "test")
        job_session.add_job(1, "test")
        task_info = job_session.add_workflow_task(1, "test", 2)
        task_id = job_session.get_task_id(1, "test", "Madlib_6.2")
        self.assertEqual(task_info['id'], task_id)

    def test_delete_task(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        job_session = Job(chorus_session)
        job_session.delete_job_from_workspace_if_exists(1, "test")
        job_session.add_job(1, "test")
        job_session.add_workflow_task(1, "test", 2)
        response = job_session.delete_task(1, "test", "Madlib_6.2")
        self.assertEqual(response.status_code, 200)
        # Verify the Job is successfully deleted
        try:
            job_session.get_task_info(1, "test", "Madlib_6.2")
        except TaskNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Task {0}".format("Madlib_6.2"))