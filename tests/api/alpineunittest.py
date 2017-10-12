import os.path
from unittest import TestCase
try:
    # For Python 3.3 and later
    from unittest.mock import patch
except ImportError:
    from mock import patch
try:
    # For Python 3.0 and later
    from urllib.parse import urlparse
    from urllib.parse import urljoin
except ImportError:
    # Fall back to Python 2.7
    from urlparse import urlparse
    from urlparse import urljoin
from alpine import APIClient


class AlpineTestCase(TestCase):

    def setUp(self):
        self.host = "10.0.0.205"
        self.port = "8080"
        self.regex_alpine_version_string = "6.3.*"
        self.username = "demoadmin"
        self.password = "4*DemoAdmin"

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        print("Test Class setup")

    @classmethod
    def tearDownClass(cls):
        print("Test Class teardown")

    def fake_urlopen(request):
        """
        A stub urlopen() implementation that load json responses from
        the filesystem.
        """
        # Map path from url to a file
        parsed_url = urlparse(request.get_full_url())
        resource_file = os.path.normpath('resources%s' % parsed_url.path)
        try:
            return open(resource_file, mode='rb')
        except IOError:
            return open('resources/404.json', mode='rb')

