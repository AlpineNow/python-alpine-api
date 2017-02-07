import os
import sys

import requests

from api.alpineobject import AlpineObject
from api.job import Job
from api.user import User
from api.workfile import Workfile
from api.workspace import Workspace
from future.datasource import DataSource
from future.touchpoint import TouchPoint


class Alpine(AlpineObject):
    """
    The main entry point for the Alpine API. Most of the API calls require a logged-in user.
    """

    user = None
    datasource = None
    workspace = None
    workfile = None
    job = None
    touchpoint = None

    def __init__(self, host=None, port=None, username=None, password=None,
                 is_secure=False, validate_certs=False, ca_certs=None,
                 token=None, logging_level='WARN'):
        # TODO: Implement logging_level variable?
        """
        Sets internal values for Alpine API session and performs login to check that parameters are set correctly
        while username and password are not null

        :param string host: hostname or ip address of the Alpine server
        :param string port: port number for Alpine
        :param string username: username to login with
        :param string password: password to login with
        :param bool is_secure:
        :param bool validate_certs:
        :param ??? ca_certs:
        :param string token: Alpine API authentication token
        :param string logging_level: https://docs.python.org/2/howto/logging.html#logging-levels (Not implemented!)
        :return: None
        """

        super(Alpine, self).__init__(token=token)

        self.is_secure = is_secure

        if is_secure:
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

        self.base_url = "{}://{}/api".format(self.protocol, self.host)

        self.ca_certs = ca_certs
        self.validate_certs = validate_certs
        self.user_id = None
        if username and password:
            self.login(username, password)

    def login(self, username, password):
        """
        Logs into Alpine with provided username and password.

        :param string username: username to login with
        :param string password: password to login with
        :return: returns a Alpine API authentication token to be used for other actions
        :rtype: string
        """
        # build the url string and body payload
        url = "{0}/sessions?session_id=NULL".format(self.base_url)
        # url = self.base_url + "/sessions?session_id=NULL"
        body = {"username": username, "password": password}
        # TODO login with cert.
        cert_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "../host_deploy/resource/ssl/certificates/test.crt")

        key_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),
                                "../host_deploy/resource/ssl/certificates/test.key")

        self.session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})

        if self.protocol == 'http':
            login_response = self.session.post(url, data=body)
        else:
            login_response = self.session.post(url, data=body,
                                               verify=self.validate_certs, cert=(cert_path, key_path),
                                               headers={'Connection' : 'close'})
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
        Attempts of logout current user.

        :return: None
        :rtype: NoneType
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

        # parse status codes here:
        status = logout_response.status_code
        if logout_response.status_code == 200:
            print("Logout successful.")
            return None
        elif logout_response.status_code == 401:
            print("No user is logged-in.")
            return None
        else:
            print("Unknown status code: {}".format(status))
            return None

    def get_status(self):
        """
        Returns information about the currently logged-in user. Or, if no user if logged-in, returns an empty dict.

        :return: Current login status.
        :rtype: dict
        """
        url = "{0}/sessions".format(self.base_url)
        self.logger.debug("Checking to see if the user is still logged in....")
        response = self.session.get(url)
        self.logger.debug("Received response code {0} with reason {1}".format(response.status_code, response.reason))

        try:
            return response.json()
        except:
            print("Not logged in.")
            return {}

    def get_version(self):
        """
        Returns the Alpine version.

        :return: Alpine version.
        :rtype: str
        """
        url = "{0}/VERSION".format(self.base_url)
        response = self.session.get(url)
        return response.content.strip()

    def get_license(self):
        """
        Get the the current license information for Alpine.

        :return: Summary of Alpine license information - expiration, user limits, add-ons.
        :rtype: dict
        """
        url = self.base_url + "/license"
        response = self.session.get(url)
        return response.json()
