from chorus import *
from urlparse import urljoin
from urlparse import urlparse

from api.exception import *
import time


class TouchPoint(ChorusObject):

    def __init__(self, chorus_session=None):
        super(TouchPoint, self).__init__()
        if chorus_session:
            self.base_url = chorus_session.base_url
            self.session = chorus_session.session
            self.token = chorus_session.token
        else:
            raise ChorusSessionNotFoundException()


    def add_touchpoint(self, touchpoint_name, workfile_id, workspace_id, touchpoint_description):
        pass

    def delete_touchpoint(self, touchpoint_name, workspace_id):
        pass

    def publish_touchpoint(self, workspace_id, touchpoint_name):
        pass

    def unpublish_touchpoint(self, workspace_id, touchpoint_name):
        pass

    def run_touchpoint(self, workspace_id, touchpoint_name, output_table, parameter_list=None):
        pass

    def stop_touchpoint(self, workspace_id, touchpoint_name):
        pass

    def get_touchpoint_list(self, workspace_id=None):
        pass

    def get_touchpoint_info(self, touchpoint_name):
        pass

    def get_touchpoint_id(self, touchpoint_name):
        pass

    def add_touchpoint_parameter(self, workspace_id, touchpoint_name, variable_name, data_type,
                             variable_label, variable_desc, options, required_val, use_default):
        pass

    def get_touchpoint_parameters(self, workspace_id, touchpoint_name):
        pass

