from __future__ import absolute_import

from api.exception import *
from api.alpineobject import AlpineObject
from .user import User

import json


class WorkspaceMember(AlpineObject):
    """
    A collection of API wrappers and helper methods to interact workspace members.

    """

    def __init__(self, base_url, session, token):
        super(WorkspaceMember, self).__init__(base_url, session, token)

    def get_list(self, workspace_id, per_page=100):
        """
        Gets metadata about all the users who are members of the workspace.

        :param str workspace_id:
        :param int int per_page:
        :return: A list of user data
        :rtype: list of dict
        :exception WorkspaceNotFoundException: The workspace does not exist.
        """

        url = "{0}/workspaces/{1}/members".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        member_list = None
        page_current = 0
        while True:
            payload = {"per_page": per_page,
                       "page": page_current + 1,
                       }
            member_list_response = self.session.get(url, data=json.dumps(payload), verify=False).json()
            page_total = member_list_response['pagination']['total']
            page_current = member_list_response['pagination']['page']
            if member_list:
                member_list.extend(member_list_response['response'])
            else:
                member_list = member_list_response['response']
            if page_total == page_current:
                break
        return member_list

    def add(self, workspace_id, user_id, role):
        """
        :param workspace_id:
        :param user_id:
        :param role:
        :return:
        """
        members = self.get_list(workspace_id)
        user_info = User(self.base_url, self.session, self.token).get(user_id)
        members.append(user_info)
        member_list =[]
        for member in members:
            if member['id'] == user_id:
                continue
            else:
                member_list.append({"user_id": member['id'], "role": member['role']})
        member_list.append({"user_id": user_id, "role": role})

        return self.__update(workspace_id, member_list)

    def remove(self, workspace_id, user_id):
        members = self.get_list(workspace_id)
        for member in members:
            if member['id'] == user_id:
                self.logger.info(
                    "Remove The user with id: <{0}> from workspace with id <{1}>".format(user_id, workspace_id))
                continue
            else:
                members.append({"user_id": member['id'], "role": member['role']})
        return self.__update(workspace_id, members)

    def update(self, workspace_id, user_id, new_role):
        """
        :param workspace_id:
        :param user_id:
        :param role:
        :return:
        """
        members = self.get_list(workspace_id)
        user_info = User(self.base_url, self.session, self.token).get(user_id)
        members.append(user_info)
        member_list =[]
        for member in members:
            if member['id'] == user_id:
                continue
            else:
                member_list.append({"user_id": member['id'], "role": member['role']})
        member_list.append({"user_id": user_id, "role": new_role})

        return self.__update(workspace_id, member_list)

    def __update(self, workspace_id, members):
        url = "{0}/workspaces/{1}/members".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        payload = {"collection": {}, "members": members}
        self.session.headers.update({"Content-Type": "application/json"})
        response = self.session.post(url, data=json.dumps(payload), verify=False)
        self.session.headers.pop("Content-Type")
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        return response.json()['response']
