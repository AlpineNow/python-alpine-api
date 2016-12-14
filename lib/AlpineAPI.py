__author__ = "T.J. Bay"

import requests
import json

class Error(Exception):
    pass

class AlpineAPI(object):

    def __init__(self):
        self.alpine_session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections = 100, pool_maxsize=100)
        self.alpine_session.mount("http://", adapter)
        self.alpine_base_url = None
        self.token = None
        self.user_id = None

"""Helper Methods"""
    def set_alpine_url(self, url):
        self.alpine_base_url = url
        start_index = self.alpine_base_url.find("://") + 3
        host_info = self.alpine_base_url[start_index:]
        self.alpine_session.headers.update({"Host": host_info})

"""Sessions"""
    def login(self, username, password):
        # Works with http only

        if self.alpine_base_url is None:
            print("Please set the Alpine URL via set_alpine_url()")
            raise Exception("No Alpine URL defined")
    
        # Attempt to login
        login_url = self.alpine_base_url + "/sessions?session_id=NULL"
        print(login_url)

        body = {"username": username, "password": password}
        login_response = self.alpine_session.post(login_url, data=body)
    
        if login_response.status_code == 201:
            response = login_response.json()
            self.token = response['response']['session_id']
            self.user_id = response['response']['user']['id']
            print("Succesfully logged in")
        else:
            print("Login failed with status code: {}".format(login_response.status_code))

    def logout():
        pass

    def get_login_status():
        pass

"""Config"""
    def get_chorus_version(self):
        """
        Returns the chorus version as a
        :param token: security token for authentication
        :param chorus_address: address of the chorus host to get a version from
        :return: version as a string
        """
        url = self.alpine_base_url + "/VERSION"
        url = url + "?session_id=" + self.token

        response = self.alpine_session.get(url)
        print("The Alpine Chorus version is {0}".format(response.content))

        return response.content    

"""License"""
    def get_licence_info():
        pass

"""User functions"""
    def create_user():
        pass

    def get_user_id():
        pass

    def delete_user():
        pass

    def update_user_info():
        pass

    def get_user_info():
        pass

    def get_users_list():
        pass

"""Workspaces"""
    def get_workspaces_list():
        pass

    def create_new_workspace():
        pass

    def delete_workspace():
        pass

    def get_member_list_for_workspace():
        pass

    def update_workspace_membership():
        pass

    def get_workspace_details():
        pass

    def update_workspace_details():
        pass


"""Workfiles"""
    # def run_workflow_with_variables(wid, wf_var):
    #     alpine_session.headers.update({"x-token": session_id})
    #     run_url = alpine_base_url + "/alpinedatalabs/api/v1/json/workflows/" + str(workflow_id) + "/run" + "?saveResult=true"
    #     alpine_session.headers.update({"Content-Type": "application/json"})
    #     run_response = alpine_session.post(run_url, data=wf_var, timeout=1000)

    #     process_id = run_response.json()['meta']['processId']
    #     return process_id

    def run_workflow(self, wid):
        
        # Add workflow variables
        run_url = self.alpine_base_url + "/alpinedatalabs/api/v1/json/workflows/" + str(wid) + "/run"
        print run_url
        
        chorus_host = self.alpine_base_url.split("http://")[1]
        
        self.alpine_session.headers.update({"x-token": self.token})
        # self.alpine_session.headers.update({"Host": chorus_host})
        self.alpine_session.headers.update({"Content-Type": "application/json"})
        run_response = self.alpine_session.post(run_url, timeout=30)
        
        print run_response.content
            
        process_id = run_response.json()['meta']['processId']
        return process_id 

    def download_workflow_results():
        result_url = alpine_base_url + "/alpinedatalabs/api/v1/json/workflows/" + str(workflow_id) + "/results/" + str(process_id)
        response = alpine_session.get(result_url)
        return response

    def query_workflow_status():
        pass

    # def get_workflow_status(pid, sid):
        
    #     query_url = alpine_base_url + "/alpinedatalabs/api/v1/json/processes/" + str(pid) + "/query"
    #     alpine_session.headers.update({"x-token": sid})
    #     alpine_session.headers.update({"Content-Type": "application/json"})
        
    #     status_response = alpine_session.get(query_url, timeout=60)
        
    #     in_progress_states = ["IN_PROGRESS", "NODE_STARTED", "STARTED", "NODE_FINISHED"]
    #     if status_response.status_code == 200:
    #         try:
    #             if status_response.json()['meta']['state'] in in_progress_states:
    #                 return "WORKING"
    #         except ValueError:
    #             if status_response.text == 'Workflow not started or already stopped.\n' or resp.text == "invalid processId or workflow already stopped.\n":
    #                 return "FINISHED"
    #             else:
    #                 return "FAILED"
    #     else:
    #         raise Exception("Workflow failed with status {0}: {1}".format(status_response.status_code, status_response.reason))
            
    def stop_workflow():
        pass

    def run_workfile():
        pass

    def delete_workfile():
        pass

    def get_workfile_details():
        pass

    def update_workfile():
        pass

"""Job Scheduler"""
    def create_job():
        pass

    def delete_job():
        pass

    def get_job_information():
        pass

    def display_all_jobs():
        pass

    def get_latest_job_result():
        pass

    def run_job():
        pass

    def stop_job():
        pass

    def update_job():
        pass

    def create_job_task():
        pass

    def delete_job_task():
        pass

    def update_job_task():
        pass

"""Status"""
    def get_server_status():
        pass

"""Notebooks"""
    def run_notebook():
        pass

    def stop_notebook_container():
        pass

"""Data - does there need to be separate functions for DB, HD, JDBC Hive?""" 
    def get_datasource_list():
        pass

    def register_datasource_connection():
        pass

    def get_datasource_info():
        pass

    def delete_datasource_connection():
        pass


