import os, time
import pytz
from datetime import datetime,timedelta

from alpine import APIClient
from alpine.exception import *
from alpine.job import *
from alpine.datasource import *
from .alpineunittest import AlpineTestCase



class TestJob(AlpineTestCase):
    def setUp(self):
        super(TestJob, self).setUp()
        # Creating Alpine Client in setUp Function for tests
        global alpine_client
        global login_info
        alpine_client = APIClient(self.host, self.port)
        login_info = alpine_client.login(self.username, self.password)

        global workspace_id
        global job_id
        global task_id
        global workflow_id

        gpdb_datasource_name = "API_Test_GPDB"
        hadoop_datasource_name = "API_Test_Hadoop"
        database_name = "miner_demo"

        # Creating a Workspace for Job tests
        db_datasource_id = alpine_client.datasource.get_id(gpdb_datasource_name, "Database")
        hadoop_datasource_id = alpine_client.datasource.get_id(hadoop_datasource_name, "Hadoop")
        try:
            workspace_id = alpine_client.workspace.get_id("Workspace for Job Tests")
            alpine_client.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info = alpine_client.workspace.create("Workspace for Job Tests")
        workspace_id = workspace_info['id']
        workspace_name = workspace_info['name']


        # Upload a DB flow
        base_dir = os.getcwd()
        afm_path = "{0}/data/afm/db_row_fil_with_variable.afm".format(base_dir)
        # afm_path = "db_bat_row_fil.afm"
        try:
            workfile_id = alpine_client.workfile.get_id("db_row_fil_with_variable", workspace_id)
            alpine_client.workfile.delete(workfile_id)
        except WorkfileNotFoundException:
            pass
        data_source_id = alpine_client.datasource.get_id(gpdb_datasource_name, "Database")
        database_list = alpine_client.datasource.get_database_list(data_source_id)
        for database in database_list:
            if database['name'] == "miner_demo":
                database_id = database['id']
        datasource_info = [{"data_source_type": DataSource.DSType.GreenplumDatabase,
                            "data_source_id": db_datasource_id,
                            "database_id": database_id
                            }]
        workfile_info = alpine_client.workfile.upload(workspace_id, afm_path, datasource_info)
        workflow_id = workfile_info['id']
        workfile_name = workfile_info['file_name']

        # Creating a Workspace for Job tests
        job_info = alpine_client.job.create(workspace_id, "Job for Test")
        job_id = job_info['id']
        task_info = alpine_client.job.task.create(workspace_id, job_id, workflow_id)
        task_id = task_info['id']

    def tearDown(self):
        try:
            alpine_client.workspace.delete(workspace_id)
            alpine_client.logout()
        except:
            pass

    def test_get_jobs_list(self):
        jobs_list = alpine_client.job.get_list(workspace_id)
        self.assertIsNotNone(jobs_list)

    def test_get_job_detail(self):
        job_detail = alpine_client.job.get(workspace_id, job_id)
        self.assertEqual(job_detail['name'], "Job for Test")

    def test_get_job_id(self):
        job_name = "test"
        try:
            job_id = alpine_client.job.get_id(workspace_id, job_name)
            alpine_client.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        job_info=alpine_client.job.create(workspace_id, job_name)
        job_id = alpine_client.job.get_id(workspace_id, job_name)
        self.assertEqual(job_id, job_info['id'])

    def test_create_job_on_demand(self):
        job_name = "test_job_schedule_on_demand"
        try:
            job_id = alpine_client.job.get_id(workspace_id, job_name)
            alpine_client.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        job_info = alpine_client.job.create(workspace_id, job_name, Job.ScheduleType.OnDemand, 0, "")
        self.assertIsNotNone(job_info)

    def test_create_job_on_monthly(self):
        job_name = "test_job_schedule_monthly"
        next_run_datetime_format = "%Y-%m-%dT%H:%M:%S"
        job_interval_unit = Job.ScheduleType.Monthly
        job_interval_value = 1
        try:
            job_id = alpine_client.job.get_id(workspace_id, job_name)
            alpine_client.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        start_time = (datetime.today().now(pytz.utc) + timedelta(minutes = 1)).strftime(next_run_datetime_format)
        print(start_time)
        job_info = alpine_client.job.create(workspace_id, job_name,
                                             job_interval_unit, job_interval_value, start_time)
        print(job_info)
        self.assertIsNotNone(job_info)
        self.assertEqual(job_info['name'], job_name)
        self.assertEqual(job_info['interval_unit'],job_interval_unit )
        self.assertEqual(job_info['interval_value'],job_interval_value)
        next_run_info_utc = datetime.strptime("".join(job_info['next_run'].rsplit('Z', 1)),next_run_datetime_format).\
            replace(tzinfo = pytz.utc)
        self.assertEqual(next_run_info_utc.strftime(next_run_datetime_format),
                         start_time,next_run_datetime_format)

    def test_create_job_on_weekly(self):
        job_name = "test_job_schedule_weekly"
        next_run_datetime_format = "%Y-%m-%dT%H:%M:%S"
        job_interval_unit = Job.ScheduleType.Weekly
        job_interval_value = 1
        try:
            job_id = alpine_client.job.get_id(workspace_id, job_name)
            alpine_client.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        start_time = (datetime.today().now(pytz.utc) + timedelta(minutes = 1)).strftime(next_run_datetime_format)
        print(start_time)
        job_info = alpine_client.job.create(workspace_id, job_name,
                                             job_interval_unit, job_interval_value, start_time)
        print(job_info)
        self.assertIsNotNone(job_info)
        self.assertEqual(job_info['name'], job_name)
        self.assertEqual(job_info['interval_unit'],job_interval_unit )
        self.assertEqual(job_info['interval_value'],job_interval_value)
        next_run_info_utc = datetime.strptime("".join(job_info['next_run'].rsplit('Z', 1)),next_run_datetime_format).\
            replace(tzinfo = pytz.utc)
        self.assertEqual(next_run_info_utc.strftime(next_run_datetime_format),
                         start_time,next_run_datetime_format)

    def test_create_job_on_daily(self):
        job_name = "test_job_schedule_daily"
        next_run_datetime_format = "%Y-%m-%dT%H:%M:%S"
        job_interval_unit = Job.ScheduleType.Daily
        job_interval_value = 1
        try:
            job_id = alpine_client.job.get_id(workspace_id, job_name)
            alpine_client.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        #start_time = (datetime.today().now(timezone.utc) + timedelta(minutes = 1)).strftime(next_run_datetime_format)
        job_info = alpine_client.job.create(workspace_id, job_name,
                                             job_interval_unit, job_interval_value)
        print(job_info)
        self.assertIsNotNone(job_info)
        self.assertEqual(job_info['name'], job_name)
        self.assertEqual(job_info['interval_unit'],job_interval_unit )
        self.assertEqual(job_info['interval_value'],job_interval_value)
        next_run_info_utc = datetime.strptime("".join(job_info['next_run'].rsplit('Z', 1)),next_run_datetime_format).\
            replace(tzinfo = pytz.utc)
        self.assertIsNotNone(next_run_info_utc.strftime(next_run_datetime_format))

    def test_create_job_on_hourly(self):
        job_name = "test_job_schedule_hourly"
        next_run_datetime_format = "%Y-%m-%dT%H:%M:%S"
        job_interval_unit = Job.ScheduleType.Hourly
        job_interval_value = 1
        try:
            job_id = alpine_client.job.get_id(workspace_id, job_name)
            alpine_client.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        #start_time = (datetime.today().now(timezone.utc) + timedelta(minutes = 1)).strftime(next_run_datetime_format)
        start_time = datetime.today().now(pytz.utc) + timedelta(minutes=1)

        print(start_time)
        job_info = alpine_client.job.create(workspace_id, job_name,
                                             job_interval_unit, job_interval_value, start_time)
        print(job_info)
        self.assertIsNotNone(job_info)
        self.assertEqual(job_info['name'], job_name)
        self.assertEqual(job_info['interval_unit'],job_interval_unit )
        self.assertEqual(job_info['interval_value'],job_interval_value)
        next_run_info_utc = datetime.strptime("".join(job_info['next_run'].rsplit('Z', 1)),next_run_datetime_format).\
            replace(tzinfo = pytz.utc)
        self.assertEqual(next_run_info_utc.strftime(next_run_datetime_format),
                         start_time.strftime(next_run_datetime_format))

    def test_delete_job_from_workspace(self):
        job_name = "test_job_to_be_deleted"
        try:
            job_id = alpine_client.job.get_id(workspace_id, job_name)
            alpine_client.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        job_info = alpine_client.job.create(workspace_id, job_name)
        response = alpine_client.job.delete(workspace_id, job_info['id'])
        # Verify the Job is successfully deleted
        try:
            alpine_client.job.get(workspace_id, job_info['id'])
        except JobNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Job {0}".format(job_name))

    def test_get_tasks_on_a_job(self):
        tasks_list = alpine_client.job.task.get_list(workspace_id, job_id)
        self.assertNotEqual(0, len(tasks_list))
        self.assertEqual(tasks_list[0]['id'], task_id)

    def test_add_workflow_task(self):
        job_name = "test_job_with_workflow_tasks"
        next_run_datetime_format = "%Y-%m-%dT%H:%M:%S"
        #next_run_datetime_format = "%Y-%m-%dT%H:%M:%S"
        job_interval_unit = Job.ScheduleType.Weekly
        job_interval_value = 2
        try:
            job_id = alpine_client.job.get_id(workspace_id, job_name)
            alpine_client.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        #start_time = (datetime.today().now(pytz.timezone('US/Pacific')) + timedelta(minutes = 1)).strftime(next_run_datetime_format)
        start_time = datetime.today().now(pytz.utc) + timedelta(minutes = 1)
        print(start_time)
        job_info = alpine_client.job.create(workspace_id, job_name, job_interval_unit,job_interval_value,
                                             start_time, pytz.utc)
        task_info = alpine_client.job.task.create(workspace_id, job_info['id'], workflow_id)
        self.assertIsNotNone(task_info)
        self.assertTrue(task_info['is_valid'])
        wait_interval_max = 300
        print("Wait for max to {0} seconds for the scheduled job run finished".format(wait_interval_max))
        for i in range(0, wait_interval_max):
            job_info_new = alpine_client.job.get(workspace_id, job_info['id'])
            if job_info_new['last_run'] is None:
                time.sleep(1)
            else:
                break
        self.assertIsNotNone(job_info_new['last_run'])

        next_run_info_new = datetime.strptime("".join(job_info_new['next_run'].rsplit('Z', 1)),
                                              next_run_datetime_format).replace(tzinfo=pytz.utc)
        self.assertEqual(next_run_info_new.strftime(next_run_datetime_format),
                         (start_time + timedelta(weeks=2)).strftime(next_run_datetime_format))

    def test_get_task_info(self):
        task_info = alpine_client.job.task.get(workspace_id, job_id, task_id)
        self.assertEqual(task_info['id'], task_id)

    def test_get_task_id(self):
        task_name = alpine_client.job.task.get(workspace_id, job_id, task_id)['name']
        task_id_get = alpine_client.job.task.get_id(workspace_id, job_id, task_name)
        self.assertEqual(task_id,task_id_get)

    def test_delete_task(self):
        job_info = alpine_client.job.create(workspace_id, "Job for Test Delete Tasks")
        task_info = alpine_client.job.task.create(workspace_id, job_info['id'], workflow_id)
        tasks = alpine_client.job.task.get_list(workspace_id, job_info['id'])
        self.assertEqual(1, len(tasks))
        alpine_client.job.task.delete(workspace_id, job_info['id'], task_info['id'])
        time.sleep(5)
        new_tasks = alpine_client.job.task.get_list(workspace_id, job_info['id'])
        self.assertEqual(0, len(new_tasks))
        try:
            alpine_client.job.task.get(workspace_id, job_info['id'], task_info['id'])
        except TaskNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Task {0}".format(task_info['name']))

    def test_run_workflow_task(self):
        job_name = "test_job_with_workflow_tasks"
        #next_run_datetime_format = "%Y-%m-%dT%H:%M:%S"
        #next_run_datetime_format = "%Y-%m-%dT%H:%M:%S%z"
        job_interval_unit = Job.ScheduleType.OnDemand
        job_interval_value = 0
        try:
            job_id = alpine_client.job.get_id(workspace_id, job_name)
            alpine_client.job.delete(workspace_id, job_id)
        except JobNotFoundException:
            pass
        #start_time = (datetime.today().now(pytz.timezone('US/Pacific')) + timedelta(minutes = 1)).strftime(next_run_datetime_format)
        #start_time = datetime.today().now(pytz.utc) + timedelta(minutes = 1)
        #print(start_time)
        job_info = alpine_client.job.create(workspace_id, job_name, job_interval_unit,job_interval_value)
        task_info = alpine_client.job.task.create(workspace_id, job_info['id'], workflow_id)
        self.assertIsNotNone(task_info)
        self.assertTrue(task_info['is_valid'])
        s = alpine_client.job.run(job_info['id'])
        wait_interval_max = 300
        print("Wait for max to {0} seconds for the scheduled job run finished".format(wait_interval_max))
        for i in range(0, wait_interval_max):
            job_info_new = alpine_client.job.get(workspace_id, job_info['id'])
            if job_info_new['last_run'] is None or job_info_new['status'] == "running":
                time.sleep(1)
            else:
                break
        self.assertIsNotNone(job_info_new['last_run'])
