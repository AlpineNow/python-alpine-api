import json
import pytz
from datetime import datetime, timedelta

try:
    # For Python 3.0 and later
    from urllib.parse import urlparse
    from urllib.parse import urljoin
except ImportError:
    # Fall back to Python 2.7
    from urlparse import urlparse
    from urlparse import urljoin
from .exception import *
from .alpineobject import AlpineObject


class Job(AlpineObject):
    """
    A class for interacting with jobs. The top-level methods deal with jobs. The subclass `Task` can be used to interact with
    individual tasks within a job.
    """

    task = None

    @property
    def scheduleType(self):
        return self.ScheduleType()

    def __init__(self, base_url, session, token):
        super(Job, self).__init__(base_url, session, token)
        self.task = Job.Task(base_url, session, token)

    def create(self, workspace_id, job_name, schedule_type=None, interval_value=0, next_run=None,
               time_zone=None):
        """
        Create a new job in a workspace with specified configuration.

        :param int workspace_id: ID of the workspace where the job is to be created.
        :param str job_name: Name of the job to be created.
        :param str schedule_type: Job run interval time unit. Use the `Job.ScheduleType` object for convenience.
                                The default value is "on_demand".
        :param int interval_value: Job run interval value. If you choose 'Job.ScheduleType.Weekly' for
                                `schedule_type` and '2' for `interval_value`, then it will run every 2 weeks.
        :param datetime next_run: When the next run should happen.
        :param timezone time_zone: Time zone info. If no time zone is provided, we use UTC.
        :return: Created job metadata.
        :rtype: dict

        Example::

            >>> session.job.create(workspace_id = 1672, job_name = "APICreatedJob",
            >>>                     schedule_type = Job.ScheduleType.Weekly, interval_value = 2,
            >>>                     next_run = datetime.today().now(pytz.timezone('US/Pacific')) + timedelta(hours=1),
            >>>                     time_zone =pytz.timezone('US/Pacific')
            >>>                   )

        """
        if time_zone is None:
            time_zone = pytz.utc

        if schedule_type is None:
            schedule_type = Job.ScheduleType.OnDemand

        if next_run is None and schedule_type != Job.ScheduleType.OnDemand:
            next_run = datetime.now(time_zone)
        url = "{0}/workspaces/{1}/jobs".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)

        # Building the payload information to send with our HTTP POST to create the job
        payload = {"name": job_name,
                   "interval_unit": schedule_type,
                   "interval_value": interval_value,
                   "next_run": next_run,
                   "sucess_notify": "nobody",
                   "description": "",
                   "endrun": False,
                   "time_zone": time_zone
                   }

        # Posting the payload via HTTP POST
        self.logger.debug("POSTing payload {0} to URL {1}".format(payload, url))
        response = self.session.post(url, data=payload, verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        try:
            return response.json()['response']
        except KeyError:
            return response.json()

    def delete(self, workspace_id, job_id):
        """
        Delete a job from a workspace.

        :param int workspace_id: ID of the workspace that contains the job.
        :param str job_id: ID of the job to delete.
        :return: None.
        :rtype: NoneType
        :exception JobNotFoundException: The job does not exist.
        :exception InvalidResponseCodeException: The request got an unexpected HTTP status code in response (not 200 OK).

        Example::

            >>> session.job.delete(workspace_id = 1672, job_id = 675)

        """
        try:
            url = "{0}/workspaces/{1}/jobs/{2}".format(self.base_url, workspace_id, job_id)
            url = self._add_token_to_url(url)

            # POSTing a HTTP delete
            self.logger.debug("Deleting the job ID: <{0}> from workspace ID: <{1}>".format(job_id, workspace_id))
            response = self.session.delete(url, verify=False)
            self.logger.debug("Received response code {0} with reason {1}".
                              format(response.status_code, response.reason)
                              )
            if response.status_code == 200:
                self.logger.debug("Job successfully deleted.")
            else:
                raise InvalidResponseCodeException("Response code invalid, the expected response code is {0}, "
                                                   "the actual response code is {1}".format(200, response.status_code))
            return None
        except JobNotFoundException as err:
            self.logger.debug("Job not found, error {0}".format(err))

    def get_list(self, workspace_id, per_page=50):
        """
        Get a list of all jobs in a workspace.

        :param int workspace_id: ID of the workspace.
        :param int per_page: Maximum number to fetch with each API call.
        :return: List of jobs' metadata.
        :rtype: list of dict

        Example::

            >>> all_jobs = session.job.get_list(workspace_id = 1672)

        """
        jobs_list = None
        url = "{0}/workspaces/{1}/jobs".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        page_current = 0
        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")
        while True:
            payload = {
                   "per_page": per_page,
                   "page": page_current + 1,
                   }
            job_list_response = self.session.get(url, data=json.dumps(payload), verify=False).json()
            page_total = job_list_response['pagination']['total']
            page_current = job_list_response['pagination']['page']
            if jobs_list:
                jobs_list.extend(job_list_response['response'])
            else:
                jobs_list = job_list_response['response']
            if page_total == page_current:
                break
        return jobs_list

    def get(self, workspace_id, job_id):
        """
        Get one job's metadata.

        :param int workspace_id: ID of the workspace that contains the job.
        :param str job_id: ID of the job.
        :return: Selected job's metadata.
        :rtype: dict

        Example::

            >>> job_info = session.job.get(workspace_id = 1672, job_id = 675)

        """
        url = "{0}/workspaces/{1}/jobs/{2}".format(self.base_url, workspace_id, job_id)
        url = self._add_token_to_url(url)

        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")

        r = self.session.get(url, verify=False)
        job_response = r.json()

        try:
            if job_response['response']:
                self.logger.debug("Found job ID: <{0}>".format(job_id))
                return job_response['response']
            else:
                raise JobNotFoundException("Job ID: <{0}> not found".format(job_id))
        except Exception as err:
            raise JobNotFoundException("Job ID: <{0}> not found".format(job_id))

    def get_id(self, workspace_id, job_name):
        """
        Gets the job ID.

        :param int workspace_id: ID of the workspace the job is in.
        :param str job_name: Name of the job.
        :return: ID of the job.
        :rtype: int

        Example::

            >>> job_id = session.job.get_id(workspace_id = 1672, job_name = "DemoJob")
            >>> print(job_id)
            675

        """
        job_list = self.get_list(workspace_id)
        for job_info in job_list:
            if job_info['name'] == job_name:
                return job_info['id']
        raise JobNotFoundException("Job {0} not found".format(job_name))

    def run(self, job_id):
        """
        Run a job.

        :param int job_id: ID of the job.
        :return: HTTP response.
        :rtype: response

        Example::

            >>> session.job.run(job_id = 675)

        """
        url = "{0}/jobs/{1}/run?saveResult=true".format(self.base_url, job_id)

        self.session.headers.update({"x-token": self.token})
        self.session.headers.update({"Content-Type": "application/json"})

        response = self.session.post(url, timeout=30)

        self.session.headers.pop("Content-Type")
        self.logger.debug(response.content)
        if response.status_code == 202:
            job = response.json()['response']
            self.logger.debug("Job with ID: <{0}> run started".format(job['id']))
            return job
        else:
            raise RunJobFailureException("Running job with ID: <{0}> failed with status code {1}".
                                         format(job_id, response.status_code))


    class Task(AlpineObject):
        """
        A class for interacting with job tasks.
        """

        def __init__(self, base_url, session, token):
            super(Job.Task, self).__init__(base_url, session, token)
            self.chorus_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(self.base_url))
            self.logger.debug(self.chorus_domain)
            self.alpine_base_url = urljoin(self.chorus_domain,
                                           "alpinedatalabs/api/{0}/json".format(self._alpine_api_version))
            self.logger.debug("alpine_base_url is: {0}".format(self.alpine_base_url))

        def create(self, workspace_id, job_id, workfile_id, task_type=None):
            """
            Add a new task to an existing job using an existing workfile.

            :param int workspace_id: ID of the workspace.
            :param int job_id: ID of the job to which the task is to be added.
            :param int workfile_id: ID of the workfile to be added as a task.
            :param str task_type:  Task type. Use the `Workspace.Stage` object for convenience.
                                   The default is "run_work_flow".
            :return: Metadata of the new task.
            :rtype: dict

            Example::

                >>> session.job.task.create(workspace_id = 1672, job_id = 675, workfile_id = 823)

            """
            if task_type is None:
                task_type = "run_work_flow"
            self.logger.debug("The job ID: <{0}>".format(job_id))
            url = "{0}/workspaces/{1}/jobs/{2}/job_tasks".format(self.base_url, workspace_id, job_id)
            url = self._add_token_to_url(url)
            self.logger.debug("The URL that we will be posting is: {0}".format(url))

            # constructing the payload for adding a task
            payload = {"action": task_type, "workfile_id": workfile_id}

            self.logger.debug("POSTing payload {0} to URL {1}".format(payload, url))
            response = self.session.post(url, data=payload, verify=False)
            self.logger.debug(
                "Received response code {0} with reason {1}...".format(response.status_code, response.reason))
            try:
                return response.json()['response']
            except KeyError:
                return response.json()

        def delete(self, workspace_id, job_id, task_id):
            """
            Delete a task from a job.

            :param int workspace_id: ID of the workspace.
            :param int job_id: ID of the job that has the task to be deleted.
            :param int task_id: ID of the task.
            :return: None
            :rtype: NoneType
            :exception TaskNotFoundException: The job does not exist.
            :exception InvalidResponseCodeException: The request got an unexpected HTTP status code in response (not 200 OK).

            Example::

                >>> session.job.task.delete(workspace_id = 1672, job_id = 675, task_id = 344)

            """
            try:
                self.logger.debug("Constructing the URL for task deletion")
                url = "{0}/workspaces/{1}/jobs/{2}/job_tasks/{3}".format(self.base_url, workspace_id, job_id, task_id)
                url = self._add_token_to_url(url)
                self.logger.debug("We have constructed the URL for task deletion. It is: {0}".format(url))
                response = self.session.delete(url)
                self.logger.debug(
                    "Received response code {0} with reason {1}...".format(response.status_code, response.reason))
                if response.status_code == 200:
                    self.logger.debug("Task successfully deleted.")
                else:
                    raise InvalidResponseCodeException("Response code invalid. the expected response code is {0}, "
                                                       "the actual response code is {1}".format(200,
                                                                                                response.status_code))
                return None
            except TaskNotFoundException as err:
                self.logger.debug("Task not found, error {0}".format(err))

        def get_list(self, workspace_id, job_id):
            """
            Get a list of all tasks in a job.

            :param int workspace_id: ID of the workspace.
            :param int job_id: ID of the job.
            :return: List of all tasks in the job.
            :rtype: list of dict

            Example::

                >>> session.job.task.get_list(workspace_id = 1672, job_id = 675);

            """
            self.logger.debug("Getting the job ID: {0}".format(job_id))

            # Constructing the URL to retrieve the contents
            url = "{0}/workspaces/{1}/jobs/{2}".format(self.base_url, workspace_id, job_id)
            url = self._add_token_to_url(url)

            # Doing a HTTP GET
            self.logger.debug("POSTing a HTTP GET to retrieve the tasks on the workspace.")
            response = self.session.get(url)
            self.logger.debug(
                "Received response code {0} with reason {1}...".format(response.status_code, response.reason))
            task_list = response.json()['response']['tasks']
            return task_list

        def get(self, workspace_id, job_id, task_id):
            """
            Return metadata of one task.

            :param int workspace_id: ID of the workspace.
            :param  int job_id: ID of the job.
            :param int task_id: ID of the task.
            :return: Selected task's metadata.
            :rtype: dict

            Example::

                >>> session.job.task.get(workspace_id = 1672, job_id = 675, task_id = 344)

            """
            task_list = self.get_list(workspace_id, job_id)
            for task in task_list:
                if task['id'] == task_id:
                    self.logger.debug(
                        "Found the task ID: <{0}>".format(task_id))
                    return task
            raise TaskNotFoundException("The task ID: <{0}> does not exist".format(task_id))

        def get_id(self, workspace_id, job_id, task_name):
            """
            Return the ID of a task.

            :param int workspace_id: ID of the workspace.
            :param int job_id: ID of the job.
            :param str task_name: Name of the task.
            :return: ID of the task.
            :rtype: int

            Example::

                >>> session.job.task.get_id(workspace_id = 1672, job_id = 675, task_name = "Run test2")
                344

            """
            task_list = self.get_list(workspace_id, job_id)
            for task in task_list:
                if task['name'] == task_name:
                    return int(task['id'])
            # return None
            raise TaskNotFoundException("The task with name: {0} does not exist".format(task_name))

    class ScheduleType(object):
        """
        Convenience strings for schedule types.
        """
        OnDemand = "on_demand"
        Monthly = "months"
        Weekly = "weeks"
        Daily = "days"
        Hourly = "hours"

    class TaskType(object):
        """
        Convenience strings for task types.
        """
        RunWorkflow = "run_work_flow"
        RunSQLFile = "run_sql_workfile"
        RunNotebook = "notebook"
