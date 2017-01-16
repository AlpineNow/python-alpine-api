import json
import logging
import logging.config
import os

class ChorusObject(object):
    chorus_api_version = 1
    alpine_api_version = "v1"

    def __init__(self, base_url=None, session = None, token=None):
        self.base_url = base_url
        self.session = session
        self.token = token

        self.setup_logging()
        # Get loggers from the configuration files(logging.json) if exists
        # For detail, reference logging.json
        self.logger = logging.getLogger("debug")    # debug or api

    def _add_token_to_url(self, url):
        return unicode("{0}?session_id={1}".format(url, self.token))

    def setup_logging(self,
                      default_path='logging.json',
                      default_level=logging.INFO,
                      env_key='LOG_CFG'):

        """

        :param default_path:
        :param default_level:
        :param env_key:
        :return:

        """

        path = default_path
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
    def _post_session(self, payload, files = None, verify =False):
        pass

    def _get_session(self, payload, verify=False):
        pass
