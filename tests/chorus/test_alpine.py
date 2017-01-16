from api.alpine import Alpine
from chorusunittest import ChorusTestCase


class TestChorus(ChorusTestCase):

    def test_login(self):
        alpine_session = Alpine(self.host, self.port)
        login_info = alpine_session.login(self.username, self.password)
        self.assertEqual(login_info['response']['user']['username'], self.username)

    def test_logout(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        logout_response = alpine_session.logout()
        self.assertEqual(logout_response.status_code, 200)

    def test_get_chorus_version(self):
        self.fail()

    def test_get_login_status(self):
        alpine_session = Alpine(self.host, self.port)
        login_info = alpine_session.login(self.username, self.password)
        current_login_info = alpine_session.get_login_status()
        self.assertEqual(login_info['response']['user'], current_login_info['response']['user'])

    def test_get_chorus_version(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        chorus_version_string = alpine_session.get_chorus_version()
        self.assertRegexpMatches(chorus_version_string, self.regex_chorus_version_string)

    def test_get_license_info(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        chorus_license_info = alpine_session.get_license_info()
        self.assertEqual(chorus_license_info['response']['limit_api'], False)
        self.assertEqual(chorus_license_info['response']['is_enabled_api'], True)
        self.assertEqual(chorus_license_info['response']['expired'], False)
        self.assertEqual(chorus_license_info['response']['correct_mac_address'], True)
        self.assertRegexpMatches(chorus_license_info['response']['version'], self.regex_chorus_version_string)

    def test_setup_logging(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.setup_logging()
        alpine_session.logger.info("Info")

    def test__add_token_to_url(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.token = "this_is_token_string"
        url = "http://base_url:port/api"
        url_with_token = "{0}?session_id={1}".format(url, alpine_session.token)
        self.assertEqual(alpine_session._add_token_to_url(url), url_with_token)


