import requests
from urlparse import urlparse


class AlpineAPI(object):
    def __init__(self, alpine_url, username, password):
        """
        Sets internal values for API version number, scheme, hostname, user_id, token
        Performs login to check that parameters are set correctly
        :param alpine_url:
        :param username:
        :param password:
        """
        self.version = 0.1

        self.alpine_session = requests.Session()
        # adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        # self.alpine_session.mount("http://", adapter)
        # Do some url parsing here:
        self.scheme, self.hostname = self._extract_base_url(alpine_url)
        self.alpine_base_url = self.scheme + "://" + self.hostname
        self.alpine_session.headers.update({"Host": self.hostname})

        self.user_id = username
        # Don't save password

        self.token = None

        # Login and error_checking here, don't save the password,
        self.login(self.user_id, password)
        self.alpine_session.headers.update({"x-token": self.token})
        self.alpine_session.headers.update({"Content-Type": "application/json"})

    """Helper Methods"""

    @staticmethod
    def _extract_base_url(url):
        """
        Attempts to find the scheme (http or https) and hostname of any user-entered url.
        :param url:
        :return: (scheme, hostname)
        """
        o = urlparse(url)
        return o.scheme, o.hostname

    """Sessions"""

    def login(self, username, password):
        # Works with http only so far

        if self.hostname is None:
            print("Please set the Alpine URL via set_alpine_url()")
            raise Exception("No Alpine URL defined")

        # Attempt to login
        login_url = self.alpine_base_url + "/sessions?session_id=NULL"
        print("Logging into: {}".format(login_url))

        body = {"username": self.user_id, "password": password}
        login_response = self.alpine_session.post(login_url, data=body)

        if login_response.status_code == 201:
            response = login_response.json()
            self.token = response['response']['session_id']
            self.user_id = response['response']['user']['id']
            print("Successfully logged in with username <{}>".format(username))
        else:
            print("Login failed with status code: <{}>".format(login_response.status_code))

    def logout(self):
        pass

    def get_login_status(self):
        pass

    """Config"""

    def get_chorus_version(self):
        """
        Returns the chorus version as a
        :return: version as a string
        """
        url = self.alpine_base_url + "/VERSION"
        response = self.alpine_session.get(url)
        return response.content

    """License"""

    def get_licence_info(self):
        pass

    """User functions"""

    def create_user(self):
        pass

    def get_user_id(self):
        pass

    def delete_user(self):
        pass

    def update_user_info(self):
        pass

    def get_user_info(self):
        pass

    def get_users_list(self):
        pass

    """Workspaces"""

    def get_workspaces_list(self):
        pass

    def create_new_workspace(self):
        pass

    def delete_workspace(self):
        pass

    def get_member_list_for_workspace(self):
        pass

    def update_workspace_membership(self):
        pass

    def get_workspace_details(self):
        pass

    def update_workspace_details(self):
        pass

    """Workfiles"""

    def run_workflow(self, wid, workflow_variables_list=None):
        """
        Run a workflow with optional workflow variables. Any workflow variables must be defined in the workflow.
        See format details below.
        :param wid:
        :param workflow_variables_list: a list of dicts of workflow variables e.g. [{"name":"@lambda", "value":"0.5"}]
        :return:
        """

        # Format workflow variables
        start = '{"meta":{"version":1}, "variables":'
        workflow_variables_formatted = start + str(workflow_variables_list).replace("\'", "\"") + '}'

        run_url = self.alpine_base_url + "/alpinedatalabs/api/v1/json/workflows/" \
                  + str(wid) + "/run" + "?saveResult=true"

        run_response = self.alpine_session.post(run_url, data=workflow_variables_formatted, timeout=30)

        print run_response.content

        process_id = run_response.json()['meta']['processId']
        return process_id

    def query_workflow_status(self, pid):
        query_url = self.alpine_base_url + "/alpinedatalabs/api/v1/json/processes/" + str(pid) + "/query"
        query_response = self.alpine_session.get(query_url, timeout=60)

        print(query_response.text)

        in_progress_states = ["IN_PROGRESS", "NODE_STARTED", "STARTED", "NODE_FINISHED"]
        if query_response.status_code == 200:
            try:
                if query_response.json()['meta']['state'] in in_progress_states:
                    return "WORKING"
            except ValueError:
                if query_response.text == 'Workflow not started or already stopped.\n' or \
                                query_response.text == "invalid processId or workflow already stopped.\n":
                    return "FINISHED"
                else:
                    return "FAILED"
        else:
            raise Exception("Workflow failed with status {0}: {1}"
                            .format(query_response.status_code, query_response.reason))

    def download_workflow_results(self, workflow_id, process_id):
        result_url = self.alpine_base_url + "/alpinedatalabs/api/v1/json/workflows/" \
                     + str(workflow_id) + "/results/" + str(process_id)
        response = self.alpine_session.get(result_url)
        return response

    def stop_workflow(self):
        pass

    def run_workfile(self):
        pass

    def delete_workfile(self):
        pass

    def get_workfile_details(self):
        pass

    def update_workfile(self):
        pass

    """Job Scheduler"""

    def create_job(self):
        pass

    def delete_job(self):
        pass

    def get_job_information(self):
        pass

    def display_all_jobs(self):
        pass

    def get_latest_job_result(self):
        pass

    def run_job(self):
        pass

    def stop_job(self):
        pass

    def update_job(self):
        pass

    def create_job_task(self):
        pass

    def delete_job_task(self):
        pass

    def update_job_task(self):
        pass

    """Status"""

    def get_server_status(self):
        pass

    """Notebooks"""

    def run_notebook(self):
        pass

    def stop_notebook_container(self):
        pass

    """Data - does there need to be separate functions for DB, HD, JDBC Hive?"""

    def get_datasource_list(self):
        pass

    def register_datasource_connection(self):
        pass

    def get_datasource_info(self):
        pass

    def delete_datasource_connection(self):
        pass
