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

    def get_workfile_info(self, workfile_name, workspace_id):
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
        workfile_detail = self.get_workfile_info(workfile_name, workspace_id)
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
        workfile_detail = self.get_workfile_info(workfile_name, workspace_id)
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

    def delete_workfile(self, workfile_name, workspace_id):
        """

        :param workfile_name:
        :param workspace_id:
        :return:
        """
        workfile_id = self.get_workfile_id(workfile_name, workspace_id)
        self.logger.debug("We have found the workfile id of workfile {0} and id {1}".format(workfile_name, workfile_id))

        # Construct the URL
        url = "{0}/workfiles/{1}".format(self.base_url, workfile_id)
        url = self._add_token_to_url(url)
        self.logger.debug("We have constructed the URL and the URL is {0}...".format(url))

        # POSTing a HTTP DELETE
        self.logger.debug("Deleting the workfile with name {0} and id {1}".format(workfile_name, workfile_id))
        response = self.session.delete(url, verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        return response

    def delete_workfile_if_exists(self, workfile_name, workspace_id):
        try:
            self.delete_workfile(workfile_name, workspace_id)
        except WorkfileNotFoundException:
            self.logger.debug ("Workspace {0} not found, don't need to delete the Workspace".format(workfile_name))

    def update_workfile(self):
        pass

    def upload_hdfs_afm(self, workspace_id, data_source_id, afm_file):
        """

        :param workspace_id:
        :param data_source_id:
        :param afm_file:
        :return:
        """
        url = "{0}/workspaces/{1}/workfiles".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        try:
            self.session.headers.pop("Content-Type")  # Remove header
        except:
            pass
        # payload is made up of file / destination meta-data (see firebug POST trace for info)
        payload = {"data_source": "{0}HdfsDataSource".format(data_source_id),
                   "workfile[entity_subtype]": "alpine",
                   "workfile[execution_locations][0][entity_type]": "hdfs_data_source",
                   "workfile[execution_locations][0][id]": data_source_id}
        # files is used to create a multipart upload content-type with requests, we send in a file object
        files = {"workfile[versions_attributes][0][contents]": open(afm_file, 'rb')}
        self.logger.debug("POSTing to: {0}\n With payload: {1}".format(url, payload))
        response = self.session.post(url, files=files, data=payload, verify=False)
        return response.json()['response']

    def upload_db_afm(self, workspace_id, data_source_id, database_id, datasource_type, database_type, afm_file):
        """
        Uploads a DB afm file for execution
        :param workspace_id:
        :param data_source_id:
        :param database_id:
        :param datasource_type:
        :param database_type:
        :param afm_file:
        :return:
        """
        url = "{0}/workspaces/{1}/workfiles".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        try:
            self.session.headers.pop("Content-Type")  # Remove header
        except:
            pass
        payload = {"data_source": str(data_source_id) + datasource_type,
                   "database": database_id,
                   "workfile[entity_subtype]": "alpine",
                   "workfile[execution_locations][0][entity_type]": database_type,
                   "workfile[execution_locations][0][id]": database_id}
        # files is used to create a multipart upload content-type with requests, we send in a file object
        files = {"workfile[versions_attributes][0][contents]": open(afm_file, 'rb')}
        self.logger.debug("POSTing to: {0}\n With payload: {1}".format(url, payload))
        response = self.session.post(url, files=files, data=payload, verify=False)
        return response.json()['response']

    # TODO
    def upload_hdfs_and_db_afm(self, workspace_id, hdfs_datasource_id,
                               db_datasource_id, db_datasource_type, database_id, database_type, afm_file):
        """
        Uploads an afm with both a hdfs and a db data source.
        :param token: session_id
        :param chorus_address: the root url
        :param workspace_name: the workspace where the afm will be uploaded
        :param hdfs_datasource_name: the hdfs data source
        :param database_datasource_name: the db data source
        :param database_name: the database within the the db data source
        :param afm_file: work file name.
        :return:
        """
        url = "{0}/workspaces/{1}/workfiles".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        payload = [("data_source", str(hdfs_datasource_id) + "HdfsDataSource"),
                   ("database", ''),
                   ("data_source", str(database_id) + db_datasource_type),
                   ("database", database_id),
                   ("workfile[entity_subtype]", "alpine"),
                   ("workfile[execution_locations][0][entity_type]", 'hdfs_data_source'),
                   ("workfile[execution_locations][0][id]", hdfs_datasource_id),
                   ("workfile[execution_locations][1][entity_type]", database_type),
                   ("workfile[execution_locations][1][id]", database_id )]
        files = {"workfile[versions_attributes][0][contents]": open(afm_file, 'rb')}
        response = self._post_afm(url, files, payload)
        return response

