from chorusunittest import ChorusTestCase
from api.chorus.chorus import Chorus


class TestChorus(ChorusTestCase):

    def test_login(self):
        chorus_session = Chorus(self.host, self.port)
        login_info = chorus_session.login(self.username, self.password)
        self.assertEqual(login_info['response']['user']['username'], self.username)

    def test_logout(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        logout_response = chorus_session.logout()
        self.assertEqual(logout_response.status_code, 200)

    def test_get_chorus_version(self):
        self.fail()

    def test_get_login_status(self):
        chorus_session = Chorus(self.host, self.port)
        login_info = chorus_session.login(self.username, self.password)
        current_login_info = chorus_session.get_login_status()
        self.assertEqual(login_info['response']['user'], current_login_info['response']['user'])

    def test_get_chorus_version(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        chorus_version_string = chorus_session.get_chorus_version()
        self.assertRegexpMatches(chorus_version_string, self.regex_chorus_version_string)

    def test_get_license_info(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        chorus_license_info = chorus_session.get_license_info()
        self.assertEqual(chorus_license_info['response']['limit_api'], False)
        self.assertEqual(chorus_license_info['response']['is_enabled_api'], True)
        self.assertEqual(chorus_license_info['response']['expired'], False)
        self.assertEqual(chorus_license_info['response']['correct_mac_address'], True)
        self.assertRegexpMatches(chorus_license_info['response']['version'], self.regex_chorus_version_string)

    def test_setup_logging(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        chorus_session.setup_logging()
        chorus_session.logger

    def test__add_token_to_url(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.token = "this_is_token_string"
        url = "http://base_url:port/api"
        url_with_token = "{0}?session_id={1}".format(url, chorus_session.token)
        self.assertEqual(chorus_session._add_token_to_url(url), url_with_token)


