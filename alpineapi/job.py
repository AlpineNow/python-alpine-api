import json
from urlparse import urljoin
from urlparse import urlparse
from exception import *
from alpineobject import AlpineObject


class Job(AlpineObject):
    """
    A class for interacting with jobs. Top-level methods deal with jobs. The subclass Task can be used to interact with individual tasks within a job.
    """

    task = None
    def __init__(self, base_url, session, token):
        super(Job, self).__init__(base_url, session, token)
        self.chorus_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(self.base_url))
        self.logger.debug(self.chorus_domain)
        self.alpine_base_url = urljoin(self.chorus_domain,
                                       "alpinedatalabs/api/{0}/json".format(self._alpine_api_version))
        self.logger.debug("alpine_base_url is: {0}".format(self.alpine_base_url))
        self.task = Job.Task(base_url, session, token)

    def create(self, workspace_id, job_name, interval_unit="on_demand", interval_value=0, next_run=""):
        """
        Add a job to a workspace with specified configuration.

        :param int workspace_id: ID of the workspace where the job is to be created.
        :param str job_name: Name of the job to be created.
        :param ??? interval_unit: Units on_demand or in weeks, days, and hours.
        :param int interval_value: Number of times it should run.
        :param next_run: When the next run should happen.
        :return: Created job metadata.
        :rtype:

        Example::

            >>> placeholder

        """
        url = "{0}/workspaces/{1}/jobs".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)

        # Building the Payload information to send with our HTTP POST to create the job
        payload = {"name": job_name,
                   "interval_unit": interval_unit,
                   "interval_value": interval_value,
                   "next_run": next_run,
                   "sucess_notify": "nobody",
                   "description": "",
                   "endrun": False,
                   "time_zone": "Pacific Time (US & Canada)"
                   }

        # Posting the Payload via HTTP POST
        self.logger.debug("POSTing payload {0} to URL {1}".format(payload, url))
        response = self.session.post(url, data=payload, verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        return response.json()['response']

    def delete(self, workspace_id, job_id):
        """
        Delete a job from a workspace.

        :param int workspace_id: ID number of the workspace the job is in.
        :param str job_id: ID number of the job to delete.
        :return: response for the delete action
        """

        url = "{0}/workspaces/{1}/jobs/{2}".format(self.base_url, workspace_id, job_id)
        url = self._add_token_to_url(url)

        # POSTing a HTTP delete
        self.logger.debug("Deleting the job id: <{0}> from workspace id: <{1}>".format(job_id, workspace_id))
        response = self.session.delete(url, verify=False)
        self.logger.debug("Received response code {0} with reason {1}".format(response.status_code, response.reason))
        return response

    def get_list(self, workspace_id, per_page=50):
        """
        Get a list of jobs from a workspace

        :param workspace_id: Id of the workspace to query on
        :param per_page: How many jobs to search for each query
        :return: Returns the list of Jobs.
        """
        jobs_list = None
        url = "{0}/workspaces/{1}/jobs".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        page_current = 0
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
        Get Job info from a workspace

        :param workspace_id: Id of the workspace to query on
        :param job_name: name of the job to query on
        :return:
        """
        url = "{0}/workspaces/{1}/jobs/{2}".format(self.base_url, workspace_id, job_id)
        url = self._add_token_to_url(url)

        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")

        r = self.session.get(url, verify=False)
        job_response = r.json()

        try:
            if job_response['response']:
                self.logger.debug("Found Job id: <{0}>".format(job_id))
                return job_response['response']
            else:
                raise JobNotFoundException("Job id: <{0}> not found".format(job_id))
        except Exception as err:
            raise JobNotFoundException("Job id: <{0}> not found".format(job_id))

    def get_id(self, workspace_id, job_name):
        """
        Get Job Id from a workspace

        :param workspace_id: Id of the workspace to query on
        :param job_name: name of the job to query on
        :return:
        """
        job_list = self.get_list(workspace_id)
        for job_info in job_list:
            if job_info['name'] == job_name:
                return job_info['id']
        # return None
        raise JobNotFoundException("Job {0} not found".format(job_name))

    def run(self, job_id):
        """
        Run a job.

        :param string workflow_id:
        :param string variables:
        :return:
        :rtype: str
        """

        url = "{0}/jobs/{1}/run?saveResult=true".format(self.base_url, job_id)
        print(url)

        self.session.headers.update({"x-token": self.token})
        self.session.headers.update({"Content-Type": "application/json"})

        response = self.session.post(url, timeout=30)

        return response

        # self.session.headers.pop("Content-Type")
        # self.logger.debug(response.content)
        # if response.status_code == 200:
        #     process_id = response.json()['meta']['processId']
        #
        #     self.logger.debug("Workflow {0} started with process {1}".format(workflow_id, process_id))
        #     return process_id
        # else:
        #     raise RunFlowFailureException(
        #         "Run Workflow {0} failed with status code {1}".format(workflow_id, response.status_code))

    class Task(AlpineObject):
        """
        Setup job tasks
        """

        def __init__(self, base_url, session, token):
            super(Job.Task, self).__init__(base_url, session, token)
            self.chorus_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(self.base_url))
            self.logger.debug(self.chorus_domain)
            self.alpine_base_url = urljoin(self.chorus_domain,
                                           "alpinedatalabs/api/{0}/json".format(self._alpine_api_version))
            self.logger.debug("alpine_base_url is: {0}".format(self.alpine_base_url))

        def create(self, workspace_id, job_id, workfile_id, task_type="run_work_flow"):
            """
            Add a task to a job

            :param workspace_id: Id of the workspace for the job
            :param job_id: Name of the job for which the task is to be added
            :param workfile_id: Id of the workfile to be added as a task
            :param task_type: task type could be run_work_flow or run_sql_workfile
            :return: Info of the new added task

            """
            self.logger.debug("The job id of the job id: <{0}>".format(job_id))
            url = "{0}/workspaces/{1}/jobs/{2}/job_tasks".format(self.base_url, workspace_id, job_id)
            url = self._add_token_to_url(url)
            self.logger.debug("The URL that we will be posting is: {0}".format(url))

            # constructing the payload for adding a task
            payload = {"action": task_type, "workfile_id": workfile_id}

            self.logger.debug("POSTing payload {0} to URL {1}".format(payload, url))
            response = self.session.post(url, data=payload, verify=False)
            self.logger.debug(
                "Received response code {0} with reason {1}...".format(response.status_code, response.reason))
            return response.json()['response']

        def delete(self, workspace_id, job_id, task_id):
            """
            Delete a task from the job on a workspace

            :param workspace_id: Id of the workspace from which the task has to be deleted
            :param job_name: Name of the job to from which the task is to be deleted
            :param task_name: Name of the task
            :return: Response of the delete action
            """

            self.logger.debug("Constructing the URL for task deletion")
            url = "{0}/workspaces/{1}/jobs/{2}/job_tasks/{3}".format(self.base_url, workspace_id, job_id, task_id)
            url = self._add_token_to_url(url)
            self.logger.debug("We have constructed the URL for task deletion and is: {0}".format(url))
            response = self.session.delete(url)
            self.logger.debug(
                "Received response code {0} with reason {1}...".format(response.status_code, response.reason))
            return response

        def get_list(self, workspace_id, job_id):
            """

            :param workspace_id:
            :param job_name:
            :return:
            """
            self.logger.debug("Getting the Job id of Job: {0}".format(job_id))
            self.logger.debug("Retrieved the Job id of the job: {0} to be: {1}".format(job_id, job_id))

            # Constructing the URL to retrieve the contents
            url = "{0}/workspaces/{1}/jobs/{2}".format(self.base_url, workspace_id, job_id)
            url = self._add_token_to_url(url)

            # Doing a HTTP GET
            self.logger.debug("Posting a HTTP GET to retrieve the tasks on the workspace.")
            response = self.session.get(url)
            self.logger.debug(
                "Received response code {0} with reason {1}...".format(response.status_code, response.reason))
            return response.json()['response']['tasks']

        def get(self, workspace_id, job_id, task_id):
            """
            Get the infomation of a task

            :param workspace_id: Id of the workspace for the job
            :param job_name: Name of the job
            :param task_name: Name of the Task
            :return: Information of the task
            """
            task_list = self.get_list(workspace_id, job_id)
            for task in task_list:
                if task['id'] == task_id:
                    self.logger.debug(
                        "We have successfully verified that we have created the task id: <{0}>".format(task_id))
                    return task
            raise TaskNotFoundException("The Task with id: <{0}> doesn't exits".format(task_id))

        def get_id(self, workspace_id, job_id, task_name):
            """
            Get the Id of a task in a job

            :param workspace_id: Id of the workspace for the job
            :param job_name: Name of the job
            :param task_name: Name of the task
            :return: Id of the task
            """
            task_list = self.get_list(workspace_id, job_id)
            for task in task_list:
                if task['name'] == task_name:
                    self.logger.debug(
                        "We have successfully verified that we have created the task: {0}".format(task_name))
                    return int(task['id'])
            return None
            # raise TaskNotFoundException("The Task with name: {0} doesn't exits".format(task_name))
