from alpine import APIClient
from alpine.exception import *

from .alpineunittest import AlpineTestCase


class TestAlpine(AlpineTestCase):

    def setUp(self):
        super(TestAlpine, self).setUp()
        # Creating Alpine Client in setUp Function for tests
        global alpine_client
        global login_info
        alpine_client = APIClient(self.host, self.port,
                                  is_secure=self.is_secure,
                                  validate_certs=self.validate_certs,
                                  ca_certs=self.ca_certs)
        login_info = alpine_client.login(self.username, self.password)

    def tearDown(self):
        pass

    def test_login(self):
        self.assertEqual(login_info['username'], self.username)

    def test_logout(self):
        logout_response = alpine_client.logout()
        self.assertEqual(logout_response.status_code, 200)

    def test_get_login_status(self):
        current_login_info = alpine_client.get_status()
        del current_login_info["complete_json"]
        self.assertEqual(login_info, current_login_info)

    def test_get_version(self):
        chorus_version_string = alpine_client.get_version()
        self.assertRegexpMatches(chorus_version_string, self.regex_alpine_version_string)

    def test_get_license_info(self):
        chorus_license_info = alpine_client.get_license()
        self.assertEqual(chorus_license_info['limit_api'], False)
        self.assertEqual(chorus_license_info['is_enabled_api'], True)
        self.assertEqual(chorus_license_info['expired'], False)
        self.assertEqual(chorus_license_info['correct_mac_address'], True)
        self.assertRegexpMatches(chorus_license_info['version'], self.regex_alpine_version_string)

    def test_setup_logging(self):
        alpine_client._setup_logging()
        alpine_client.logger.info("Info")

    def test__add_token_to_url(self):
        alpine_client.token = "this_is_token_string"
        url = "http://base_url:port/api"
        url_with_token = "{0}?session_id={1}".format(url, alpine_client.token)
        self.assertEqual(alpine_client._add_token_to_url(url), url_with_token)


