import time
import json
from urlparse import urljoin
from urlparse import urlparse
from api.alpineobject import AlpineObject
from api.exception import *
from .workspace import Workspace


class WorkflowProcess(AlpineObject):
    """
    A collection of API wrappers and helper methods to interact with Alpine Workflows, including running workflows \
    with or without workflow variables, ...
    """

    def __init__(self, base_url, session, token):
        super(WorkflowProcess, self).__init__(base_url, session, token)
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

    def run(self, workflow_id, variables=None):
        # TODO: Does this work for workfiles only ...?
        """
        Run a workflow, optionally including a list of workflow variables. Returns a process_id which is needed by \
        other functions which query a run or download results.

        :param str workflow_id: ID of workflow.
        :param list variables: Workflow variables in the following format ...
        :return: ID number for the workflow run process.
        :rtype: str
        :exception WorkspaceNotFoundException: The workspace does not exist.
        :exception WorkfileNotFoundException: The workfile does not exist.
        """

        url = "{0}/workflows/{1}/run?saveResult=true".format(self.alpine_base_url, workflow_id)
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

            self.logger.debug("Workflow {0} started with process {1}".format(workflow_id, process_id))
            return process_id
        else:
            raise RunFlowFailureException(
                "Run Workflow {0} failed with status code {1}".format(workflow_id, response.status_code))

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

    def download_results(self, workflow_id, process_id, operator_name=None):
        """
        Download a workflow run result locally for the whole workflow or a particular operator.

        :param str workflow_id: Id of workflow.
        :param ste process_id: ID number of a particular workflow run.
        :param ste operator_name: The name of the operator that would return in results.

        :return: JSON object of workflow results.
        :rtype: dict
        :exception WorkspaceNotFoundException: The workspace does not exist.
        :exception WorkfileNotFoundException: The workflow does not exist.
        :exception ResultsNotFoundException: Results not found or does not match expected structure.
        """

        url = "{0}/workflows/{1}/results/{2}".format(self.alpine_base_url, workflow_id, process_id)
        response = self.session.get(url)
        self.logger.debug(response.content)
        if response.status_code == 200:
            if response.content == "\"\"":
                raise ResultsNotFoundException("Could not find run results for process id <{}>"
                                                .format(process_id))
        else:
            raise ResultsNotFoundException("Download results failed with status {0}: {1}"
                            .format(response.status_code, response.reason))
        results = json.loads(response.json())

        if operator_name:
            return self.find_operator(operator_name, results)
        else:
            return results

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
