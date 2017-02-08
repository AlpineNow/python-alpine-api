from api.alpine import Alpine
from api.job import Job
from api.exception import *
from alpineunittest import AlpineTestCase


class TestJob(AlpineTestCase):
    def setUp(self):
        super(TestJob, self).setUp()
        global workspace_id
        global job_id
        # Creating a Workspace for Job tests
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.workspace.delete("Workspace for Job Tests")
        workspace_info = alpine_session.workspace.create("Workspace for Job Tests")
        workspace_id = workspace_info['id']
        job_info = alpine_session.job.add_job(workspace_id,"Job for Test")
        job_id = job_info['id']
        alpine_session.logout

    def tearDown(self):
        # Drop the datasources created in setup
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.workspace.delete("Workspace for Job Tests")

    def test_get_jobs_list(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        jobs_list = alpine_session.job.get_jobs_list(1)
        self.assertIsNotNone(jobs_list)

    def test_get_job_detail(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        job_detail = alpine_session.job.get_job_info(1, "test")
        self.assertEqual(job_detail['name'], "test")

    def test_get_job_id(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.job.delete_job_from_workspace_if_exists(workspace_id, "test")
        job_info=alpine_session.job.add_job(workspace_id, "test")
        job_id = alpine_session.job.get_job_id(workspace_id, "test")
        self.assertEqual(job_id, job_info['id'])

    def test_add_job(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.job.delete_job_from_workspace_if_exists(workspace_id, "test1")
        job_info = alpine_session.job.add_job(workspace_id, "test1", "on_demand", 0, "")
        self.assertIsNotNone(job_info)

    def test_delete_job_from_workspace(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.job.delete_job_from_workspace_if_exists(1, "test")
        alpine_session.job.add_job(1, "test")
        response = alpine_session.job.delete_job_from_workspace(1, "test")
        self.assertEqual(response.status_code, 200)
        # Verify the Job is successfully deleted
        try:
            alpine_session.job.get_job_info(1, "test")
        except JobNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Job {0}".format("test"))

    def test_get_tasks_on_a_job(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        #alpine_session.job.delete_job_from_workspace_if_exists(1, "test")
        #alpine_session.job.add_job(1, "test")
        tasks_list = alpine_session.job.get_tasks_on_a_job(1, "test")
        self.assertIsNotNone(tasks_list)

    def test_add_workfile_task(self):
        self.fail()

    def test_add_workflow_task(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.job.delete_job_from_workspace_if_exists(1, "test")
        alpine_session.job.add_job(1, "test")
        task_info = alpine_session.job.add_workflow_task(1, "test", 2)
        self.assertIsNotNone(task_info)

    def test_add_sqlworkfile_task(self):
        self.fail()

    def test_get_task_info(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.job.delete_job_from_workspace_if_exists(1, "test")
        alpine_session.job.add_job(1, "test")
        task_info1 =alpine_session.job.add_workflow_task(1, "test", 2)
        task_info = alpine_session.job.get_task_info(1, "test", "Madlib_6.2")
        self.assertEqual(task_info1, task_info)

    def test_get_task_id(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.job.delete_job_from_workspace_if_exists(1, "test")
        alpine_session.job.add_job(1, "test")
        task_info = alpine_session.job.add_workflow_task(1, "test", 2)
        task_id = alpine_session.job.get_task_id(1, "test", "Madlib_6.2")
        self.assertEqual(task_info['id'], task_id)

    def test_delete_task(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.job.delete_job_from_workspace_if_exists(1, "test")
        alpine_session.job.add_job(1, "test")
        alpine_session.job.add_workflow_task(1, "test", 2)
        response = alpine_session.job.delete_task(1, "test", "Madlib_6.2")
        self.assertEqual(response.status_code, 200)
        # Verify the Job is successfully deleted
        try:
            alpine_session.job.get_task_info(1, "test", "Madlib_6.2")
        except TaskNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Task {0}".format("Madlib_6.2"))