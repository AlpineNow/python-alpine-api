__author__ = 'guohuigao'

import requests
import os
import sys
from api.chorus.chorus import *
from api.exception import *
from urlparse import urljoin
from urlparse import urlparse

class Alpine(ChorusObject):
    api_version = "v1"
    def __init__(self, chorus_session=None):
        super(Alpine, self).__init__()
        if chorus_session:
            self.base_url = chorus_session.base_url
            self.session = chorus_session.session
            self.token = chorus_session.token
            self.chorus_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(self.base_url))
            self.logger.debug(self.chorus_domain)
            self.alpine_base_url = urljoin(self.chorus_domain,
                                               "alpinedatalabs/api/{0}/json".format(self.api_version))
            self.logger.debug("alpine_base_url is: {0}".format(self.alpine_base_url))
        else:
            raise ChorusSessionNotFoundException()

    def run_workflow(self, workflow_id, variables=None):
        """

        :param workflow_id:
        :param variables:
        :return:
        """
        workflow_variables = '{{"meta": {{"version": 1}}, "variables": {0}}}'.format(variables).replace("\'", "\"")

        url = "{0}/workflows/{1}/run?saveResult=true".format(self.alpine_base_url, workflow_id)

        self.session.headers.update({"x-token": self.token})
        self.session.headers.update({"Content-Type": "application/json"})

        response = self.session.post(url, data=workflow_variables, timeout=30)
        self.logger.debug(response.content)
        if response.status_code == 200:
            process_id = response.json()['meta']['processId']

            self.logger.debug("Workflow {0} started with process {1}".format(workflow_id, process_id))
            return process_id
        else:
            raise RunFlowFailureException(
                "Run Workflow {0} failed with status code {1}".format(workflow_id, response.status_code))

    def query_workflow_status(self, process_id):
        """

        :param process_id:
        :return:
        """
        url = "{0}/processes/{1}/query".format(self.alpine_base_url, process_id)
        response = self.session.get(url, timeout=60)

        self.logger.debug(response.text)

        in_progress_states = ["IN_PROGRESS", "NODE_STARTED", "STARTED", "NODE_FINISHED"]
        if response.status_code == 200:
            try:
                if response.json()['meta']['state'] in in_progress_states:
                    return "WORKING"
            except ValueError:
                if response.text == 'Workflow not started or already stopped.\n' or \
                                response.text == "invalid processId or workflow already stopped.\n":
                    return "FINISHED"
                else:
                    return "FAILED"
        else:
            raise RunFlowFailureException("Workflow failed with status {0}: {1}"
                                          .format(response.status_code, response.reason))

    def download_workflow_results(self, workflow_id, process_id):
        """

        :param workflow_id:
        :param process_id:
        :return:
        """
        url = "{0}/workflows/{1}/results/{2}".format(self.alpine_base_url, workflow_id, process_id)
        response = self.session.get(url)
        self.logger.debug(response.content)
        if response.status_code == 200:
            if response.content == "\"\"":
                raise Exception("results of flow {0} for session {1} is empty, "
                                "please check whether there is results not cleared."
                                .format(workflow_id, process_id))
            else:
                return response
        else:
            raise Exception("Download Workflow Results failed with status {0}: {1}"
                                          .format(response.status_code, response.reason))

    def stop_workflow(self, process_id):
        """

        :param process_id:
        :return:
        """
        url = "{0}/processes/{1}/stop".format(self.alpine_base_url, process_id)
        response = self.session.post(url, timeout=60)
        self.logger.debug(response.text)
        if response.status_code == 200:
            if response.json()['status'] == "Flow stopped.\n":
                return "FINISHED"
            else:
                return "FAILED"
        else:
            raise StopFlowFailureException("Workflow failed with status {0}: {1}"
                                          .format(response.status_code, response.reason))
