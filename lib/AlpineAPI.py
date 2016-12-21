import requests
from urlparse import urlparse
import json
"""
TODO List:
1. Continue to fill in functions
2. Determine any new functions
3. Add comments
4. Better error testing
5. Test cases
6. Better document
7. Fix our current docs
8. Rewrite current API guide to use these functions
9. Add https functionality
"""

"""
Style
1. Define payloads as dictionary objects then use json.dumps() to convert to string in the request.
2.
"""


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
        self.scheme, self.hostname = self._extract_url(alpine_url)
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
    def _extract_url(url):
        """
        Attempts to find the scheme (http or https) and hostname of any user-entered url.
        :param url:
        :return: (scheme, hostname)
        """
        o = urlparse(url)
        return o.scheme, o.netloc

    """Sessions"""

    def login(self, username, password):
        # Works with http only so far

        if self.hostname is None:
            print("Please set the Alpine URL via set_alpine_url()")
            raise Exception("No Alpine URL defined")

        # Attempt to login
        login_url = self.alpine_base_url + "/sessions?session_id=NULL"
        print(login_url)


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
        # Is there a way to do this without explicitly including the token in the url?
        url = self.alpine_base_url + "/sessions" + "?session_id=" + self.token
        response = self.alpine_session.delete(url)
        print("Received response code {0} with reason {1}".format(response.status_code, response.reason))
        return response

    def get_login_status(self):
        url = self.alpine_base_url + "/sessions"
        print("Checking to see if the user is still logged in....")
        response = self.alpine_session.get(url)
        print("Received response code {0} with reason {1}".format(response.status_code, response.reason))
        return response

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

    def get_license_info(self):
        url = self.alpine_base_url + "/license"
        response = self.alpine_session.get(url)
        return response.content

    """User functions"""

    def create_user(self):
        pass

    def _get_user_id(self, username, per_page=100):

        user_list = self.get_users_list(per_page)['response']
        for user in user_list:
            if user['username'] == username:
                return int(user['id'])

        print("No match found for username {}".format(username))
        print("Please check spelling or search more records")
        return None

    def delete_user(self):
        pass

    def update_user_info(self):
        pass

    def get_user_info(self, username):
        """
        :param username:
        :return:
        """
        user_id = self._get_user_id(username)
        url = self.alpine_base_url + "/users/" + str(user_id)
        user_info = self.alpine_session.get(url)
        return user_info.json()['response']

    def get_users_list(self, per_page=100):
        """
        :param per_page: how many users to retrieve per page
        :return:
        """
        url = self.alpine_base_url + "/users" + "?session_id=" + self.token
        payload = {"per_page": str(per_page)}
        user_list = self.alpine_session.get(url, data=json.dumps(payload)).json()
        return user_list

    def get_user_workspace_membership(self):
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

        payload = { "meta": {"version": 1}, "variables" : workflow_variables_list}

        run_url = self.alpine_base_url + "/alpinedatalabs/api/v1/json/workflows/" \
                  + str(wid) + "/run" + "?saveResult=true"

        run_response = self.alpine_session.post(run_url, data=json.dumps(payload), timeout=30)

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

    def stop_workflow(self, process_id):
        """
        Stops a workflow give the process_id
        :param process_id: process ID of workflow to stop
        :return:
        """
        # build the url string and update http headers with our token
        url = self.alpine_base_url + "/alpinedatalabs/api/v1/json/processes/" + str(process_id) + "/stop"
        resp = self.alpine_session.post(url)
        return resp.text

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

    """Data - do we need to be separate functions for DB, HD, JDBC Hive?"""

    def get_datasource_list(self):
        pass

    def get_datasource_info(self):
        pass

