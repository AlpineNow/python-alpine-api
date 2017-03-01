from alpineapi.alpine import Alpine
from alpineapi.exception import *
from alpineunittest import AlpineTestCase


class TestJob(AlpineTestCase):
    def setUp(self):
        super(TestJob, self).setUp()
        global workspace_id
        global job_id
        global task_id
        global workflow_id

        # Need to upload the workflow to get id
        workflow_id = 1
        # Creating a Workspace for Job tests
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            workspace_id = alpine_session.workspace.get_id("Workspace for Job Tests")
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info = alpine_session.workspace.create("Workspace for Job Tests")
        workspace_id = workspace_info['id']
        job_info = alpine_session.job.create(workspace_id, "Job for Test")
        job_id = job_info['id']
        task_info = alpine_session.job.task.create(workspace_id, job_id, workflow_id)
        task_id = task_info['id']
        alpine_session.logout

    def tearDown(self):
        # Drop the datasources created in setup
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        #alpine_session.workspace.delete(workspace_id)

    def test_get_jobs_list(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        jobs_list = alpine_session.job.get_list(workspace_id)
        self.assertIsNotNone(jobs_list)

    def test_get_job_detail(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        job_detail = alpine_session.job.get(workspace_id, job_id)
        self.assertEqual(job_detail['name'], "Job for Test")

    def test_get_job_id(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        job_name = "test"
        try:
            job_id = alpine_session.job.get_id(workspace_id, job_name)
            alpine_session.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        job_info=alpine_session.job.create(workspace_id, job_name)
        job_id = alpine_session.job.get_id(workspace_id, job_name)
        self.assertEqual(job_id, job_info['id'])

    def test_add_job(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        job_name = "test1"
        try:
            job_id = alpine_session.job.get_id(workspace_id, job_name)
            alpine_session.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        job_info = alpine_session.job.create(workspace_id, job_name, "on_demand", 0, "")
        self.assertIsNotNone(job_info)

    def test_delete_job_from_workspace(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        job_name = "test"
        try:
            job_id = alpine_session.job.get_id(workspace_id, job_name)
            alpine_session.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        job_info = alpine_session.job.create(workspace_id, job_name)
        response = alpine_session.job.delete(workspace_id, job_info['id'])
        self.assertEqual(response.status_code, 200)
        # Verify the Job is successfully deleted
        try:
            alpine_session.job.get(workspace_id, job_info['id'])
        except JobNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Job {0}".format(job_name))

    def test_get_tasks_on_a_job(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        tasks_list = alpine_session.job.task.get_list(workspace_id, job_id)
        self.assertNotEqual(0, len(tasks_list))
        self.assertEqual(tasks_list[0]['id'], task_id)

    def test_add_workflow_task(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        job_name = "test3"
        try:
            job_id = alpine_session.job.get_id(workspace_id, job_name)
            alpine_session.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        job_info = alpine_session.job.create(workspace_id, job_name, "on_demand")
        task_info = alpine_session.job.task.create(workspace_id, job_info['id'], workflow_id)
        self.assertIsNotNone(task_info)

    def test_get_task_info(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        task_info = alpine_session.job.task.get(workspace_id, job_id, task_id)
        self.assertEqual(task_info['id'], task_id)

    def test_get_task_id(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        task_name = alpine_session.job.task.get(workspace_id, job_id, task_id)['name']
        task_id_get = alpine_session.job.task.get_id(workspace_id, job_id, task_name)
        self.assertEqual(task_id,task_id_get)

    def test_delete_task(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        job_info = alpine_session.job.create(workspace_id, "Job for Test Delete Tasks")
        task_info = alpine_session.job.task.create(workspace_id, job_info['id'], workflow_id)
        tasks = alpine_session.job.task.get_list(workspace_id, job_info['id'])
        self.assertEqual(1, len(tasks))
        alpine_session.job.task.delete(workspace_id, job_info['id'], task_info['id'])
        new_tasks = alpine_session.job.task.get_list(workspace_id, job_info['id'])
        self.assertEqual(0, len(new_tasks))
        try:
            alpine_session.job.task.get(workspace_id, job_info['id'], task_info['id'])
        except TaskNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Task {0}".format(task_info['name']))