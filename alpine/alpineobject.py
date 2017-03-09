from __future__ import unicode_literals
from __future__ import absolute_import

import json
import logging
import logging.config
import os


class AlpineObject(object):
    """
    Base Class of Alpine API objects

    """
    #
    # alpine alpine version string
    #
    _alpine_api_version = "v1"
    _min_alpine_version = "6.2"

    def __init__(self, base_url=None, session=None, token=None):
        self.base_url = base_url
        self.session = session
        self.token = token

        self._setup_logging()
        # Get loggers from the configuration files(logging.json) if exists
        # For detail, reference logging.json
        self.logger = logging.getLogger("debug")    # debug

    def _add_token_to_url(self, url):
        """
        Used internally to properly form  URLs.

        :param str url: An Alpine API URL
        :return: Formatted URL
        :rtype str:
        """
        return str("{0}?session_id={1}".format(url, self.token))

    @staticmethod
    def _setup_logging(default_configuration_setting_file='logging.json',
                       default_level=logging.INFO,
                       env_key='LOG_CFG'):
        """
        Sets internal values for logging through a file or an environmental variable

        :param str default_configuration_setting_file: Path to logging config file. Will be overwritten by
                                                       environment variable if it exists.
        :param default_level: See possible levels here: https://docs.python.org/2/library/logging.html#logging-levels
        :param str env_key: Name of environment variable with logging setting.
        :return: None
        """

        path = default_configuration_setting_file
        value = os.getenv(env_key, None)

        if value:
            path = value
        else:
            pass

        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = json.load(f)

            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level,
                                format="%(asctime)s %(name)s %(module)s[%(lineno)d] %(levelname)s: %(message)s")
