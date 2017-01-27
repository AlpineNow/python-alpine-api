import json
import logging
import logging.config
import os

class AlpineObject(object):
    """
    Base Class of Alpine API objects

    """
    #
    # api version string
    #
    _chorus_api_version = 1
    #
    # alpine api version string
    #
    _alpine_api_version = "v1"

    def __init__(self, base_url=None, session = None, token=None):
        self.base_url = base_url
        self.session = session
        self.token = token

        self._setup_logging()
        # Get loggers from the configuration files(logging.json) if exists
        # For detail, reference logging.json
        self.logger = logging.getLogger("debug")    # debug or api

    def _add_token_to_url(self, url):
        """
        For internal use only

        :param url: nothing
        :return: nothing
        """
        return unicode("{0}?session_id={1}".format(url, self.token))

    def _setup_logging(self,
                      default_configuration_setting_file='logging.json',
                      default_level=logging.INFO,
                      env_key='LOG_CFG'):
        """
        Sets internal values for logging

        :param default_configuration_setting_file: the default file for logging configuration. Could be overwrite by environment variable if exists
        :param default_level: default logging level
        :param env_key: Environment Variable to read for configuration setting file
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
