__author__ = 'guohuigao'

import requests
import json
from chorus import *

from api.exception import *

class Workfile(ChorusObject):

    def __init__(self, chorus_session=None):
        super(Workfile, self).__init__()
        if chorus_session:
            self.base_url = chorus_session.base_url
            self.session = chorus_session.session
            self.token = chorus_session.token
        else:
            raise ChorusSessionNotFoundException()

    def get_workfiles_list(self, workspace_id, per_page=100):
        """

        :param workspace_id:
        :param per_page:
        :return:
        """
        workfile_list = None
        url = "{0}/workspaces/{1}/workfiles".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)

        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")
        page_current = 0
        while True:
            payload = {"no_published_worklets": True,
                       "order": "file_name",
                       "per_page": per_page,
                       "page": page_current + 1,
                       }
            workfile_list_response = self.session.get(url, data=json.dumps(payload), verify=False).json()
            page_total = workfile_list_response['pagination']['total']
            page_current = workfile_list_response['pagination']['page']
            if workfile_list:
                workfile_list.extend(workfile_list_response['response'])
            else:
                workfile_list = workfile_list_response['response']
            if page_total == page_current:
                break;
        return workfile_list

    def get_workfile_details(self, workfile_name, workspace_id):
        """

        :param workfile_name:
        :param workspace_id:
        :return:
        """
        workfile_list = self.get_workfiles_list(workspace_id)
        for workfile in workfile_list:
            if workfile['file_name'] == workfile_name:
                return workfile
        raise WorkfileNotFoundException("The Work file with name <{0}> is not found in workspace id:{1}".format(
            workfile_name, workspace_id
        ))

    def get_workfile_id(self, workfile_name, workspace_id):
        """

        :param workfile_name:
        :param workspace_id:
        :return:
        """
        workfile_detail = self.get_workfile_details(workfile_name, workspace_id)
        return workfile_detail['id']

    def run_workflow(self, workfile_name, workspace_id, variables=None):
        """

        :param workfile_name:
        :param workspace_id:
        :param variables:
        :return:
        """
        #Using the Chorus API to run a workflow
        #TODO variable is not working for chorus API
        # Format workflow variables
        workflow_id = self.get_workfile_id(workfile_name, workspace_id)
        workflow_variables = '{{"meta": {{"version": 1}}, "variables": {0}}}'.format(variables).replace("\'", "\"")

        url = "{0}/workfiles/{1}/run".format(self.base_url, workflow_id)
        url = self._add_token_to_url(url)
        response = self.session.post(url, data=workflow_variables,timeout=30)
        if response.status_code == 202:
            self.logger.debug("Workflow {0} started".format(workflow_id))
            return response
        else:
            raise RunFlowFailureException("Run Workflow {0} failed with status code {1}".format(workflow_id, response.status_code))

    def query_workflow_status(self, workfile_name, workspace_id):
        """

        :param workfile_name:
        :param workspace_id:
        :return:
        """
        workfile_detail = self.get_workfile_details(workfile_name, workspace_id)
        return workfile_detail['status']

    def stop_workflow(self, workfile_name, workspace_id ):
        """

        :param workfile_name:
        :param workspace_id:
        :return:
        """
        workflow_id = self.get_workfile_id(workfile_name, workspace_id)
        url = "{0}/workfiles/{1}/stop".format(self.base_url, workflow_id)
        url = self._add_token_to_url(url)
        response = self.session.post(url, timeout=30)
        if response.status_code == 202:
            self.logger.debug("Workflow {0} stopped".format(workflow_id))
            return response
        else:
            raise StopFlowFailureException(
                "Stop Workflow {0} failed with status code {1}".format(workflow_id, response.status_code))

    def get_workflow_results(self, workfile_name, workspace_id):
        """

        :param workfile_name:
        :param workspace_id:
        :return:
        """
        workflow_id = self.get_workfile_id(workfile_name, workspace_id)
        url = "{0}workfiles/{1}/results".format(self.base_url, workflow_id)
        url = self._add_token_to_url(url)
        response = self.session.get(url, timeout=30)
        if response.status_code == 202:
            return response
        else:
            raise Exception("failed to get workflow results")

    def get_running_workflows(self):
        """

        :return:
        """
        self.base_url = "http://10.10.0.204:8080/"
        url = "{0}/#admin/running_workflow".format(self.base_url)
        url = self._add_token_to_url(url)
        self.logger.debug("debug")
        response = self.session.get(url, timeout=30)
        self.logger.debug(response)
        if response.status_code == 202:
            return response
        else:
            raise Exception("failed to get workflow results")

    def download_workflow_results(self, workflow_id, process_id):
        """

        :param workflow_id:
        :param process_id:
        :return:
        """
        result_url = self.alpine_base_url + "/alpinedatalabs/api/v1/json/workflows/" \
                     + str(workflow_id) + "/results/" + str(process_id)
        response = self.alpine_session.get(result_url)
        return response

    def create_new_workflow(self, workflow_name):
        pass

    def create_new_notebook(self, workflow_name):
        pass

    def create_new_link(self, workflow_name):
        pass

    def create_new_sql_file(self, workflow_name):
        pass

    def delete_workfile(self):
        pass

    def update_workfile(self):
        pass

    def test_logging(self):
        self.logger.info("INFO")
        self.logger.debug("debug")
        self.logger.warning("warning")
        self.logger.error("error")
        self.logger.critical("critical")
