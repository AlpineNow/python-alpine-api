__author__ = 'guohuigao'

import requests
import json
from chorus import *

from api.exception import *

class Job(ChorusObject):

    def __init__(self, chorus_session=None):
        super(Job, self).__init__()
        if chorus_session:
            self.base_url = chorus_session.base_url
            self.session = chorus_session.session
            self.token = chorus_session.token
        else:
            raise ChorusSessionNotFoundException()

    def add_job(self, workspace_id, job_name, interval_unit="on_demand", interval_value=0, next_run=""):
        """

        :param workspace_id:
        :param job_name:
        :param interval_unit:
        :param interval_value:
        :param next_run:
        :return:
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

    def get_jobs_list(self, workspace_id, per_page=50):
        """

        :param workspace_id:
        :param per_page:
        :return:
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
                break;
        return jobs_list

    def get_job_info(self, workspace_id, job_name):
        """

        :param workspace_id:
        :param job_name:
        :return:
        """
        job_list = self.get_jobs_list(workspace_id)
        for job in job_list:
            if job['name'] ==job_name:
                return job
        raise JobNotFoundException("The Job with name {0} doesn't exits".format(job_name))

    def get_job_id(self, workspace_id, job_name):
        """

        :param workspace_id:
        :param job_name:
        :return:
        """
        job = self.get_job_info(workspace_id, job_name)
        return job['id']

    def delete_job_from_workspace(self, workspace_id, job_name):
        """

        :param workspace_id:
        :param job_name:
        :return:
        """
        job_id = self.get_job_id(workspace_id, job_name)
        self.logger.debug("The job id of the job: {0} is {1}".format(job_name, job_id))

        url = "{0}/workspaces/{1}/jobs/{2}".format(self.base_url, workspace_id, job_id)
        url = self._add_token_to_url(url)

        # POSTing a HTTP delete
        self.logger.debug("Deleting the job: {0} from workspace: {1}".format(job_name, workspace_id))
        response = self.session.delete(url, verify=False)
        self.logger.debug("Received response code {0} with reason {1}".format(response.status_code, response.reason))
        return response

    def delete_job_from_workspace_if_exists(self, workspace_id, job_name):
        """

        :param workspace_id:
        :param job_name:
        :return:
        """
        try:
            self.delete_job_from_workspace(workspace_id,job_name)
        except JobNotFoundException:
            self.logger.debug("Job not found, so we don't need to delete it")

    def add_workfile_task(self, workspace_id, job_name, workfile_id, task_type):
        """

        :param workspace_id:
        :param job_name:
        :param workfile_id:
        :param task_type:
        :return:
        """
        job_id = self.get_job_id(workspace_id, job_name)
        self.logger.debug("The job id of the job: {0} is {1}".format(job_name, job_id))
        url = "{0}/workspaces/{1}/jobs/{2}/job_tasks".format(self.base_url, workspace_id, job_id)
        url = self._add_token_to_url(url)
        self.logger.debug("The URL that we will be posting is: {0}".format(url))

        # constructing the payload for adding a task
        payload = { "action": task_type, "workfile_id": workfile_id}

        self.logger.debug("POSTing payload {0} to URL {1}".format(payload, url))
        response = self.session.post(url, data=payload, verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        return response.json()['response']

    def add_workflow_task(self, workspace_id, job_name, workflow_id):
        """

        :param workspace_id:
        :param job_name:
        :param workflow_id:
        :return:
        """
        # Setting the task type to run_work_flow, since this is adding a workflow as a task to a job on a workspace
        task_type = "run_work_flow"
        return self.add_workfile_task(workspace_id,job_name, workflow_id, task_type)

    def add_sqlworkfile_task(self, workspace_id, job_name, sql_workfile_id):
        """

        :param workspace_id:
        :param job_name:
        :param sql_workfile_id:
        :return:
        """
        sql_task_type = "run_sql_workfile"
        return self.add_workfile_task(workspace_id,job_name, sql_workfile_id, sql_task_type)

    def get_tasks_on_a_job(self, workspace_id, job_name):
        """

        :param workspace_id:
        :param job_name:
        :return:
        """
        # Getting the job id
        self.logger.debug("Getting the Job id of Job: {0}".format(job_name))
        job_id = self.get_job_id(workspace_id, job_name)
        self.logger.debug("Retrieved the Job id of the job: {0} to be: {1}".format(job_name, job_id))

        # Constructing the URL to retrieve the contents
        url = "{0}/workspaces/{1}/jobs/{2}".format(self.base_url, workspace_id, job_id)
        url = self._add_token_to_url(url)

        # Doing a HTTP GET
        self.logger.debug("Posting a HTTP GET to retrieve the tasks on the workspace.")
        response = self.session.get(url)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        return response.json()['response']['tasks']

    def get_task_info(self, workspace_id, job_name, task_name):
        """

        :param workspace_id:
        :param job_name:
        :param task_name:
        :return:
        """
        task_name = "Run " + task_name
        task_list = self.get_tasks_on_a_job(workspace_id, job_name)
        task_list = task_list
        for task in task_list:
            if task['name'] == task_name:
                self.logger.debug("We have successfully verified that we have created the task: {0}".format(task_name))
                return task
        raise TaskNotFoundException("The Task with name {0} doesn't exits".format(task_name))

    def get_task_id(self, workspace_id, job_name, task_name):
        """

        :param workspace_id:
        :param job_name:
        :param task_name:
        :return:
        """
        task = self.get_task_info(workspace_id, job_name, task_name)
        return int(task['id'])

    def delete_task(self, workspace_id, job_name, task_name):
        """

        :param workspace_id:
        :param job_name:
        :param task_name:
        :return:
        """
        job_id = self.get_job_id(workspace_id, job_name)
        task_id = self.get_task_id(workspace_id, job_name, task_name)

        self.logger.debug("Constructing the URL for task deletion")
        url = "{0}/workspaces/{1}/jobs/{2}/job_tasks/{3}".format(self.base_url, workspace_id, job_id, task_id)
        url = self._add_token_to_url(url)
        self.logger.debug("We have constructed the URL for task deletion and is: {0}".format(url))
        response = self.session.delete(url)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        return response
