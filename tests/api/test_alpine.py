from alpineapi import Alpine
from alpineapi.exception import *

from alpineunittest import AlpineTestCase


class TestAlpine(AlpineTestCase):

    def test_login(self):
        alpine_session = Alpine(self.host, self.port)
        login_info = alpine_session.login(self.username, self.password)
        self.assertEqual(login_info['username'], self.username)

    def test_logout(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        logout_response = alpine_session.logout()
        self.assertEqual(logout_response.status_code, 200)

    def test_get_login_status(self):
        alpine_session = Alpine(self.host, self.port)
        login_info = alpine_session.login(self.username, self.password)
        current_login_info = alpine_session.get_status()
        self.assertEqual(login_info, current_login_info)

    def test_get_version(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        chorus_version_string = alpine_session.get_version()
        self.assertRegexpMatches(chorus_version_string, self.regex_alpine_version_string)

    def test_get_license_info(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        chorus_license_info = alpine_session.get_license()
        self.assertEqual(chorus_license_info['limit_api'], False)
        self.assertEqual(chorus_license_info['is_enabled_api'], True)
        self.assertEqual(chorus_license_info['expired'], False)
        self.assertEqual(chorus_license_info['correct_mac_address'], True)
        self.assertRegexpMatches(chorus_license_info['version'], self.regex_alpine_version_string)

    def test_setup_logging(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session._setup_logging()
        alpine_session.logger.info("Info")

    def test__add_token_to_url(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.token = "this_is_token_string"
        url = "http://base_url:port/api"
        url_with_token = "{0}?session_id={1}".format(url, alpine_session.token)
        self.assertEqual(alpine_session._add_token_to_url(url), url_with_token)


