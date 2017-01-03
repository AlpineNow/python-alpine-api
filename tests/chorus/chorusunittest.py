from unittest import TestCase
from api.exception import *


class ChorusTestCase(TestCase):
    def setUp(self):
        self.host = "10.10.0.204"
        self.port = "8080"
        self.regex_chorus_version_string = "6.2.*"
        self.username = "chorusadmin"
        self.password = "secret"

    def tearDown(self):
        pass

