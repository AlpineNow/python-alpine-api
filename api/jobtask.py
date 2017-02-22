import json
from urlparse import urljoin
from urlparse import urlparse
from api.exception import *
from api.alpineobject import AlpineObject


class JobTask(AlpineObject):
    """
    Setup job tasks
    """

    def __init__(self, base_url, session, token):
        super(JobTask, self).__init__(base_url, session, token)
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
        payload = { "action": task_type, "workfile_id": workfile_id}

        self.logger.debug("POSTing payload {0} to URL {1}".format(payload, url))
        response = self.session.post(url, data=payload, verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
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
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
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
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
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
                self.logger.debug("We have successfully verified that we have created the task id: <{0}>".format(task_id))
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

