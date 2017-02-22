import json
from urlparse import urljoin
from urlparse import urlparse
from api.exception import *
from api.alpineobject import AlpineObject
from api.jobtask import JobTask


class Job(AlpineObject):
    """
    Setup and run jobs and tasks
    """

    task = None
    def __init__(self, base_url, session, token):
        super(Job, self).__init__(base_url, session, token)
        self.chorus_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(self.base_url))
        self.logger.debug(self.chorus_domain)
        self.alpine_base_url = urljoin(self.chorus_domain,
                                       "alpinedatalabs/api/{0}/json".format(self._alpine_api_version))
        self.logger.debug("alpine_base_url is: {0}".format(self.alpine_base_url))
        self.task = JobTask(base_url, session, token)

    def create(self, workspace_id, job_name, interval_unit="on_demand", interval_value=0, next_run=""):
        """
        Adding a job to a workspace with specified configuration

        :param workspace_id: id of the workspace where the job to be created
        :param job_name: name of the job that to be created
        :param interval_unit: units on_demand or in weeks days and hours
        :param interval_value: how many times should it run
        :param next_run: when should the next run happen
        :return: Job info of the new added one
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
        Delete job from a workspace

        :param workspace_id: Id of the workspace to be deleted in
        :param job_name: name of the job to delete
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
