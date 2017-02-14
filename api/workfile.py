import time
import json
from urlparse import urljoin
from urlparse import urlparse
from api.alpineobject import AlpineObject
from api.exception import *
from .workspace import Workspace


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
    def find_operator(operator_name, flow_results):
        """
        Helper method to parse a downloaded workflow result to extract data for a single operator.

        :param str operator_name: Operator name to extract. Must be an exact match to the name in the workflow.
        :param dict flow_results: JSON object of Alpine flow results from download_results.
        :return: Single operator dictionary.
        :rtype: dict
        :exception FlowResultsMalformedException: Workflow result does not contain the key ['outputs'].
        """

        if 'outputs' in flow_results:
            for operator in flow_results['outputs']:
                if operator['out_title'] == operator_name:
                    return operator
        else:
            raise FlowResultsMalformedException("Workflow result does not contain the key ['outputs']")

    @staticmethod
    def get_flow_metadata(flow_results):
        """
        Return the metadata for a particular workflow run including time, number of operators, \
        user, and number of errors.

        :param dict flow_results: JSON object of Alpine flow results from download_results.
        :return: Run metadata.
        :rtype: dict
        :exception FlowResultsMalformedException: Workflow results does not contain the key ['flowMetaInfo'].
        """

        try:
            return flow_results['flowMetaInfo']
        except:
            raise FlowResultsMalformedException("Workflow result does not contain the key ['flowMetaInfo']")

    @staticmethod
    def get_start_time(flow_results):
        """
        Returns the start time of a particular workflow run.

        :param dict flow_results: JSON object of Alpine flow results from download_results.
        :return: String version of a datatime object.
        :rtype: string
        :exception FlowResultsMalformedException: Workflow results does not contain the start time.
        """

        try:
            return flow_results['flowMetaInfo']['startTime']
        except:
            raise FlowResultsMalformedException("Workflow result does not contain the key \
                                                ['flowMetaInfo']['startTime']")

    @staticmethod
    def get_end_time(flow_results):
        """
         Returns the end time of a particular workflow run.

         :param dict flow_results: JSON object of Alpine flow results from download_results.
         :return: String version of a datatime object.
         :rtype: string
         :exception FlowResultsMalformedException: Workflow results does not contain the end time.
         """

        try:
            return flow_results['flowMetaInfo']['endTime']
        except:
            raise FlowResultsMalformedException("Workflow result does not contain the key \
                                                ['flowMetaInfo']['endTime']")

    def get_all(self, workspace_id, per_page=100):
        """
        Return all workfiles in a workspace.

        :param int workspace_id: Id of workspace.
        :param int per_page: Number of workfiles to get in each call.
        :return: List of workfiles' metadata
        :rtype: list of dict
        :exception WorkspaceNotFoundException: The workspace does not exist.
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

    def get_data(self, workfile_id):
        """
        Return metadata for one workfile in a workspace.

        :param str workfile_id: Id of workfile.
        :return: One workfile's metadata
        :rtype: dict
        :exception WorkspaceNotFoundException: The workspace does not exist.
        :exception WorkfileNotFoundException: The workfile does not exist.
        """

        url = "{0}/workfiles/{1}".format(self.base_url, workfile_id)
        url = self._add_token_to_url(url)

        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")

        r = self.session.get(url, verify=False)
        workfile_response = r.json()

        try:
            if workfile_response['response']:
                self.logger.debug("Found workfile id: <{0}> in list...".format(workfile_id))
                return workfile_response
            else:
                raise WorkfileNotFoundException("Workfile id: <{0}> not found".format(workfile_id))
        except Exception:
            raise WorkfileNotFoundException("Workfile id: <{0}> not found".format(workfile_id))

    def get_id(self, workfile_name, workspace_id):
        """
        Return the ID number of a workfile in a workspace. Mostly used internally.

        :param string workfile_name: Name of workfile.
        :param string workspace_id: Id of workspace that contains the workfile.
        :return: ID number of workfile
        :rtype: int
        :exception WorkspaceNotFoundException: The workspace does not exist.
        :exception WorkfileNotFoundException: The workfile does not exist.
        """

        workfile_list = self.get_all(workspace_id)
        for workfile in workfile_list:
            if workfile['file_name'] == workfile_name:
                return workfile['id']
        # return None
        raise WorkfileNotFoundException("The workfile with name <{0}> is not found in workspace <{1}>"
                                        .format(workfile_name, workspace_id))

    def run(self, workfile_id, variables=None):
        # TODO: Does this work for workfiles only ...?
        """
        Run a workflow, optionally including a list of workflow variables. Returns a process_id which is needed by \
        other functions which query a run or download results.

        :param str workfile_id: ID of workfile.
        :param list variables: Workflow variables in the following format ...
        :return: ID number for the workflow run process.
        :rtype: str
        :exception WorkspaceNotFoundException: The workspace does not exist.
        :exception WorkfileNotFoundException: The workfile does not exist.
        """

        url = "{0}/workflows/{1}/run?saveResult=true".format(self.alpine_base_url, workfile_id)
        self.session.headers.update({"x-token": self.token})
        self.session.headers.update({"Content-Type": "application/json"})

        # Handle WFV:
        if variables is None:
            workflow_variables = None
        else:

            for variable in variables:
                if all(key in variable for key in ("name", "value")):
                    pass
                else:
                    raise WorkflowVariableException("Workflow variable item <{}> doesn't contain the " \
                                                    "expected keys 'name' and 'value'.".format(variable))

            workflow_variables = '{{"meta": {{"version": 1}}, "variables": {0}}}'\
                .format(variables)\
                .replace("\'", "\"")

        response = self.session.post(url, data=workflow_variables, timeout=30)
        self.session.headers.pop("Content-Type")
        self.logger.debug(response.content)

        if response.status_code == 200:
            process_id = response.json()['meta']['processId']

            self.logger.debug("Workflow {0} started with process {1}".format(workfile_id, process_id))
            return process_id
        else:
            raise RunFlowFailureException(
                "Run Workflow {0} failed with status code {1}".format(workfile_id, response.status_code))

    def query_status(self, process_id):
        """
        Return the status of a running workflow.

        :param str process_id: ID number of a particular workflow run.
        :return: State of workflow run. One of 'WORKING', 'FINISHED', or 'FAILED'.
        :rtype: str
        :exception RunFlowFailureException: Process ID not found.
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
            raise RunFlowFailureException("Workflow process ID <{}> not found".format(process_id))

    def download_results(self, workfile_id, process_id):
        """
        Download a workflow run result locally.

        :param str workfile_id: Id of workfile.
        :param ste process_id: ID number of a particular workflow run.
        :return: JSON object of workflow results.
        :rtype: dict
        :exception WorkspaceNotFoundException: The workspace does not exist.
        :exception WorkfileNotFoundException: The workfile does not exist.
        :exception ResultsNotFoundException: Results not found or does not match expected structure.
        """

        url = "{0}/workflows/{1}/results/{2}".format(self.alpine_base_url, workfile_id, process_id)
        response = self.session.get(url)
        self.logger.debug(response.content)
        if response.status_code == 200:
            if response.content == "\"\"":
                raise ResultsNotFoundException("Could not find run results for process id <{}>"
                                                .format(process_id))
            else:
                return json.loads(response.json())
        else:
            raise ResultsNotFoundException("Download results failed with status {0}: {1}"
                            .format(response.status_code, response.reason))

    def stop(self, process_id):
        """
        Attempt to stop a running workflow.

        :param str process_id: Process ID of the workflow.
        :return: Flow status. One of 'STOPPED' or 'STOP FAILED'.
        :rtype: str
        :exception StopFlowFailureException: Workflow run not found.
        """
        url = "{0}/processes/{1}/stop".format(self.alpine_base_url, process_id)
        response = self.session.post(url, timeout=60)
        self.logger.debug(response.text)
        if response.status_code == 200:
            if response.json()['status'] == "Flow stopped.\n":
                return "STOPPED"
            else:
                return "STOP FAILED"
        else:
            raise StopFlowFailureException("Workflow failed with status {0}: {1}"
                                           .format(response.status_code, response.reason))

    def wait_until_finished(self, process_id, verbose=False, query_time=10, timeout=3600):
        """
        Waits for a running workflow to finish.
        
        :param str process_id: Process ID of the workflow.
        :param bool verbose: Optionally print approximate run time.
        :param float query_time: Number of seconds between status queries.
        :param float timeout: Amount of time in seconds to wait for workflow to finish. Will stop if exceeded.
        :return: Workflow run status.
        :rtype: str
        :exception RunFlowTimeoutException: Workflow runtime has exceeded timeout.
        :exception RunFlowFailureException: Status of FAILURE is detected.
        """

        start = time.time()
        self.logger.debug("Waiting for process ID: {0} to complete...".format(process_id))
        wait_count = 0

        workflow_status = self.query_status(process_id)
        while workflow_status == "WORKING":  # loop while waiting for workflow to complete
            wait_count += 1
            wait_total = time.time() - start

            # self.logger.debug(
            #     "Workflow status: {0}, on query {1} sleeping for {2} seconds".format(workflow_status,
            #                                                                          wait_count,
            #                                                                          wait_total))

            if wait_total >= timeout:
                stop_status = self.stop(process_id)
                raise RunFlowTimeoutException(
                    "The Workflow with process ID: {0} has exceeded a runtime of {1} seconds. It now has status <{2}>."
                    .format(process_id, timeout, stop_status))

            if verbose:
                print("\rWorkflow in progress for ~{0:.2f} seconds.".format(wait_total)),

            time.sleep(query_time)

            if workflow_status == "FAILED":
                raise RunFlowFailureException("The workflow with process id: {0} failed.".format(process_id))
            workflow_status = self.query_status(process_id)
        return workflow_status

    def delete(self, workfile_id):
        """
        Delete a workfile from a workspace.

        :param workfile_id: Name of workfile to delete.
        :return: None
        :rtype: NoneType
        :exception WorkspaceNotFoundException: The workspace does not exist.
        :exception WorkfileNotFoundException: The workfile does not exist.
        """
        try:
            self.get_data(workfile_id)
            # Construct the URL
            url = "{0}/workfiles/{1}".format(self.base_url, workfile_id)
            url = self._add_token_to_url(url)
            self.logger.debug("We have constructed the URL and the URL is {0}...".format(url))

            # POSTing a HTTP DELETE
            self.logger.debug("Deleting the workfile with id: <{0}>".format(workfile_id))
            response = self.session.delete(url, verify=False)
            self.logger.debug(
                "Received response code {0} with reason {1}...".format(response.status_code, response.reason))
            if response.status_code == 200:
                self.logger.debug("Workfile successfully deleted.")
            else:
                raise InvalidResponseCodeException("Response Code Invalid, the expected Response Code is {0}, "
                                                   "the actual Response Code is {1}".format(200, response.status_code))
            return None
        except WorkfileNotFoundException as err:
            self.logger.debug("Workfile not found, error {}".format(err))


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
