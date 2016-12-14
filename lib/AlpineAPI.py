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

    def set_alpine_url(self, url):
        self.alpine_base_url = url
        start_index = self.alpine_base_url.find("://") + 3
        host_info = self.alpine_base_url[start_index:]
        self.alpine_session.headers.update({"Host": host_info})

    def login(self, username, password):

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

    def run_workflow(self, wid):
        
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

