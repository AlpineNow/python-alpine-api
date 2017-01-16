import json
import logging
import logging.config
import os
import sys
import time
import json
import requests
from api.chorus import ChorusObject
from api.user import User
from api.datasource import DataSource
from api.workspace import Workspace
from api.workfile import Workfile
from api.job import Job
from api.touchpoint import TouchPoint


class Alpine(ChorusObject):
    user = None
    datasource = None
    workspace = None
    workfile = None
    job = None
    touchpoint = None

    def __init__(self, host=None, port=None, username=None, password=None,
                 is_secure=False, validate_certs=False, ca_certs=None,
                 token=None):

        super(Alpine, self).__init__(token=token)

        self.is_secure = is_secure

        if (is_secure):
            self.protocol = 'https'
        else:
            self.protocol = 'http'

        if not port:
            self.host = host
        if port == 80:
            self.host = host
        else:
            self.host = "{0}:{1}".format(host, port)

        self.session = requests.Session()  # instantiate a session for requests

        self.base_url = "{}://{}/api/".format(self.protocol, self.host)

        self.ca_certs = ca_certs
        self.validate_certs = validate_certs
        self.user_id=None
        if username and password:
            self.login(username, password)

    def login(self, username, password):
        """
        Logs into Chorus with provided username and password
        :param username: username to login with
        :param password: password to log in with
        :return: returns a token ID which should be used for other actions
        """
        # build the url string and body payload
        url= "{0}/sessions?session_id=NULL".format(self.base_url)
        #url = self.base_url + "/sessions?session_id=NULL"
        body = {"username": username, "password": password}
        #TODO login with cert.
        cert_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "../host_deploy/resource/ssl/certificates/test.crt")

        key_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),
                            "../host_deploy/resource/ssl/certificates/test.key")

        self.session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})

        if self.protocol == 'http':
            login_response = self.session.post(url, data=body)
        else:
            login_response = self.session.post(url, data=body,
                                               verify=self.validate_certs, cert=(cert_path, key_path),
                                               headers={'Connection':'close'})
        if login_response.status_code == 201:
            response = login_response.json()
            self.token = response['response']['session_id']
            self.user_id = response['response']['user']['id']
            self.logger.debug("Successfully logged in with username <{}>".format(username))
            self.logger.debug("Token ID is: {0}".format(self.token))
            self.user = User(self.base_url, self.session, self.token)
            self.datasource = DataSource(self.base_url, self.session, self.token)
            self.workspace = Workspace(self.base_url, self.session, self.token)
            self.workfile = Workfile(self.base_url, self.session, self.token)
            self.job = Job(self.base_url, self.session, self.token)
            self.touchpoint = TouchPoint(self.base_url, self.session, self.token)
        else:
            raise Exception("Login failed with status code: <{0}>".format(login_response.status_code))

        return login_response.json()

    def logout(self):
        """
        Logout the session
        :return: response of the logout session
        """
        # Is there a way to do this without explicitly including the token in the url?
        url = "{0}/sessions?session_id={1}".format(self.base_url, self.token)
        logout_response = self.session.delete(url)
        self.logger.debug("Received response code {0} with reason {1}".format(logout_response.status_code, logout_response.reason))
        self.user = None
        self.datasource = None
        self.workspace = None
        self.workfile = None
        self.user = None
        self.datasource = None
        return logout_response

    def get_login_status(self):
        """

        :return:

        """
        url = "{0}/sessions".format(self.base_url)
        self.logger.debug("Checking to see if the user is still logged in....")
        response = self.session.get(url)
        self.logger.debug("Received response code {0} with reason {1}".format(response.status_code, response.reason))
        return response.json()

    def get_chorus_version(self):
        """
        Returns the chorus version as a
        :return: version as a string
        """
        url = "{0}/VERSION".format(self.base_url)
        response = self.session.get(url)
        return response.content

    def get_license_info(self):
        """

        :return:

        """
        url = self.base_url + "/license"
        response = self.session.get(url)
        return response.json()

    def clone(self):
        return self
