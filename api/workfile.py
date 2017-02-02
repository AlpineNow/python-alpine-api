import time
import json
from urlparse import urljoin
from urlparse import urlparse
from api.alpineobject import AlpineObject
from api.exception import *


class Workfile(AlpineObject):
    """
    A collection of API wrappers and helper methods to interact with Alpine workfiles, including running workflows \
    with or without workflow variables, ...
    """

    def __init__(self, base_url, session, token):
        super(Workfile, self).__init__(base_url, session, token)
        self.chorus_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(self.base_url))
        self.logger.debug(self.chorus_domain)
        self.alpine_base_url = urljoin(self.chorus_domain,
                                       "alpinedatalabs/api/{0}/json".format(self._alpine_api_version))
        self.logger.debug("alpine_base_url is: {0}".format(self.alpine_base_url))

    @staticmethod
    def find_operator(name, operator_list):
        """
        Helper method to parse a downloaded workflow result to extract data for a single operator.

        :param str name: Operator name to extract. Must be an exact match to the name in the workflow.
        :param list operator_list: A list of operators and associated results. \
                              Get from download_workflow_results(...)['outputs']
        :return: Single operator dictionary.
        :rtype: dict
        """
        for operator in operator_list:
            if operator['out_title'] == name:
                return operator
        return []

    def get_workfiles_list(self, workspace_id, per_page=100):
        """
        Return all workfiles in a workspace.

        :param string workspace_id:
        :param int per_page:
        :return:
        :rtype:
        """
        workfile_list = None
        url = "{0}/workspaces/{1}/workfiles".format(self.base_url, str(workspace_id))
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
                break
        return workfile_list

    def get_workfile_info(self, workfile_name, workspace_id):
        """

        :param string workfile_name:
        :param string workspace_id:
        :return:
        :rtype:
        """
        workfile_list = self.get_workfiles_list(workspace_id)
        for workfile in workfile_list:
            if workfile['file_name'] == workfile_name:
                return workfile
        raise WorkfileNotFoundException("The workfile with name <{0}> is not found in workspace id:{1}".format(
            workfile_name, workspace_id
        ))

    def get_workfile_id(self, workfile_name, workspace_id):
        """

        :param string workfile_name:
        :param string workspace_id:
        :return:
        :rtype:
        """
        workfile_detail = self.get_workfile_info(workfile_name, workspace_id)
        return workfile_detail['id']

    def run_workflow(self, workflow_id, variables=[]):
        """
        Run a workflow, optionally including a list of workflow variables.

        :param string workflow_id:
        :param string variables:
        :return:
        :rtype: str
        """
        workflow_variables = '{{"meta": {{"version": 1}}, "variables": {0}}}'.format(variables).replace("\'", "\"")

        url = "{0}/workflows/{1}/run?saveResult=true".format(self.alpine_base_url, workflow_id)

        self.session.headers.update({"x-token": self.token})
        self.session.headers.update({"Content-Type": "application/json"})

        response = self.session.post(url, data=workflow_variables, timeout=30)
        self.session.headers.pop("Content-Type")
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
        self.session.headers.update({"Content-Type": "application/json"})
        response = self.session.get(url, timeout=60)
        self.session.headers.pop("Content-Type")
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
        :return: JSON object of workflow results.
        """
        url = "{0}/workflows/{1}/results/{2}".format(self.alpine_base_url, workflow_id, process_id)
        response = self.session.get(url)
        self.logger.debug(response.content)
        if response.status_code == 200:
            if response.content == "\"\"":
                raise Exception("Results of flow {0} for process {1} are empty, "
                                "please check whether there are results not cleared"
                                .format(workflow_id, process_id))
            else:
                return json.loads(response.json())
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

    def wait_for_workflow_to_finish(self, process_id, verbose=False, query_time=10, timeout=3600):
        """
        Waits for a workflow
        :param process_id: process ID of the workflow / worklet to monitor
        :param verbose:
        :param query_time:
        :param timeout: amount of time in seconds to wait for workflow / worklet to finish
        :return: True if success, otherwise, raise exception
        """
        self.logger.debug("Waiting for process ID: {0} to complete...".format(process_id))
        wait_count = 0
        workflow_status = self.query_workflow_status(process_id)
        while workflow_status == "WORKING":  # loop while waiting for workflow to complete
            self.logger.debug(
                "Workflow status: {0}, on retry {1} sleeping for 10 seconds".format(workflow_status, wait_count))
            time.sleep(query_time)
            wait_count += query_time

            if verbose == True:
                print("\rWorkflow in progress for ~{} seconds.".format(wait_count)),

            if wait_count >= timeout:
                self.stop_workflow(process_id)
                raise RunFlowTimeoutException(
                    "The Workflow with process ID: {0} has exceeded a runtime of {1} seconds".format(process_id,
                                                                                                     timeout))
            if workflow_status == "FAILED":  # we don't expect a failure...
                raise RunFlowFailureException("The workflow with process id: {0} failed...".format(process_id))
            workflow_status = self.query_workflow_status(process_id)
        return workflow_status

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
            self.logger.debug("Workspace {0} not found, don't need to delete the Workspace".format(workfile_name))

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

    def upload_db_afm(self, workspace_id, data_source_id, database_id, datasource_type, database_type,
                      afm_file):
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
