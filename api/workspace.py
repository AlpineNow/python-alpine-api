from __future__ import absolute_import

from api.exception import *
from api.alpineobject import AlpineObject
from .user import User

import json


class Workspace(AlpineObject):
    """
    A collection of API wrappers and helper methods to interact with Alpine workspaces, including creating, updating, \
    deleting,  and adding members.

    """

    def __init__(self, base_url, session, token):
        super(Workspace, self).__init__(base_url, session, token)

    def create(self, workspace_name, public=False, summary=None):
        """
        Will create a workspace. Will fail if the workspace_name is not unique.

        :param str workspace_name: Unique workspace name.
        :param bool public: Optionally allow the workspace to be viewable by non-members and non-admins.
        :param str summary: Description of new workspace.
        :return: Created workspace information or error message.
        :rtype: dict
        """
        url = "{0}/workspaces".format(self.base_url)
        url = self._add_token_to_url(url)
        str_public = "false"
        if public:
            str_public = "true"
        payload = {"name": workspace_name,
                   "public": str_public,
                   "summary": summary}
        response = self.session.post(url, data=payload, verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))

        try:
            return response.json()['response']
        except:
            return response.json()

    def get_data(self, workspace_name):
        """
        Get the one workspace's metadata.

        :param str workspace_name: Unique workspace name.
        :return: Single workspace's data
        :rtype: dict
        :exception WorkspaceNotFoundException: The workspace does not exist.
        """
        workspace_list = self.get_all()
        for workspace in workspace_list:
            if workspace['name'] == workspace_name:
                self.logger.debug("Found workspace {0} in list...".format(workspace_name))
                return workspace
        raise WorkspaceNotFoundException("Workspace {0} not found".format(workspace_name))

    def get_id(self, workspace_name):
        """
        Get the ID number of the workspace. Will throw an exception if the workspace doens't exist.

        :param str workspace_name: Unique workspace name.
        :return: ID number of the workspace.
        :rtype: int
        :exception WorkspaceNotFoundException: The workspace does not exist.
        """
        try:
            workspace_info = self.get_data(workspace_name)
        except WorkspaceNotFoundException as err:
            self.logger.error(err)
            raise
        return workspace_info['id']

    def get_members(self, workspace_name, per_page=100):
        """
        Gets metadata about all the users who are members of the workspace.

        :param str workspace_name:
        :param int int per_page:
        :return: A list of user data
        :rtype: list of dict
        :exception WorkspaceNotFoundException: The workspace does not exist.
        """
        workspace_id = self.get_id(workspace_name)
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

    def get_all(self, username=None, active=None, per_page=50):
        """
        Get a list of metadata for each workspace. If username is provided, only workspaces that the user \
        is a member of will be returned.

        :param str username: Alpine username.
        :param bool active: Optionally only return active workspaces. True will return only the active spaces.
        :param int per_page: How many workspaces to return in each page.

        :return: List of workspace metadata.
        :rtype: list of dict
        :exception UserNotFoundException: The username does not exist.
        """

        # Parse the active parameter:
        # Work-around for https://alpine.atlassian.net/browse/IBX-4398
        if active is True:
            active_state = "true"
        else:
            active_state = None

        # Get user_id.
        if username is not None:
            user_session = User(self.base_url, self.session, self.token)
            user_id = user_session.get_id(username)
        else:
            user_id = None

        workspace_list = None
        url = "{0}/workspaces".format(self.base_url)
        url = self._add_token_to_url(url)

        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")

        payload = {"user_id": user_id,
                   "active": active_state,
                   "per_page": per_page,
                   }

        page_current = 0
        while True:
            payload['page'] = page_current + 1

            r = self.session.get(url, params=payload, verify=False)
            workspace_list_response = r.json()

            page_total = workspace_list_response['pagination']['total']
            page_current = workspace_list_response['pagination']['page']

            if workspace_list:
                workspace_list.extend(workspace_list_response['response'])
            else:
                workspace_list = workspace_list_response['response']
            if page_total == page_current:
                break

        return workspace_list

    def update_name(self, workspace_name, new_workspace_name):
        """

        :param workspace_name:
        :param new_workspace_name:
        :return:
        """
        workspace_id = self.get_id(workspace_name)
        if workspace_id is None:
            raise WorkspaceNotFoundException("Workspace {0} was not found".format(workspace_name))
        url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        payload = self.get_data(workspace_name)

        # replace fields with updated ones from kwargs
        payload["name"] = new_workspace_name
        self.session.headers.update({"Content-Type": "application/json"})  # Set special header for this post
        response = self.session.put(url, data=json.dumps(payload), verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        self.session.headers.pop("Content-Type")  # Remove header, as it affects other tests
        return response.json()['response']

    def update_settings(self, workspace_name=None, is_public=None, is_active=None,
                                      summary=None, stage_id=None, owner_id=None):
        # TODO: Can we combine with update_name??
        """

        :param workspace_name:
        :param is_public:
        :param is_active:
        :param summary:
        :param stage_id:
        :param owner_id:
        :return:
        """
        workspace_id = self.get_id(workspace_name)
        if workspace_id is None:
            raise WorkspaceNotFoundException("Workspace {0} was not found".format(workspace_name))
        url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        payload = self.get_data(workspace_name)

        # get rid of fields that aren't required for PUT to reduce request size.
        pop_fields = ['complete_json',
                      'entity_type',
                      'id',
                      'image',
                      'is_deleted',
                      'workspace_stage'
                      ]
        for field in pop_fields:
            payload.pop(field)

        # replace fields with updated ones from kwargs
        if is_public:
            payload["public"] = is_public
        if is_active:
            payload["archived"] = not is_active
        if summary:
            payload["summary"] = summary
        if stage_id:
            payload["workspace_stage_id"] = stage_id
        if owner_id:
            payload["owner_id"] = owner_id
        self.session.headers.update({"Content-Type": "application/json"})  # Set special header for this post
        response = self.session.put(url, data=json.dumps(payload), verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        self.session.headers.pop("Content-Type")  # Remove header, as it affects other tests
        return response.json()['response']

    def update_membership(self, workspace_name, user_id, role):
        # TODO: Can this be used to delete members?
        """

        :param workspace_name:
        :param user_id:
        :param role:
        :return:
        """
        workspace_id = self.get_id(workspace_name)
        url = "{0}/workspaces/{1}/members".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        # Build payload with user ids and role
        members = []
        member_list = self.get_members(workspace_name)
        # If the user is not an member, add the user,
        # if the user is already a member of the workspace, update the user role
        for member in member_list:
            if member['id'] == user_id:
                continue
            else:
                members.append({"user_id": member['id'], "role": member['role']})
        members.append({"user_id": user_id, "role": role})
        payload = {"collection": {}, "members": members}
        self.session.headers.update({"Content-Type": "application/json"})
        response = self.session.post(url, data=json.dumps(payload), verify=False)
        self.session.headers.pop("Content-Type")
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        return response.json()['response']

    def add_member(self, workspace_name, username, role):
        """
        :param workspace_name:
        :param username:
        :param role:
        :return:
        """
        return self.update_membership(workspace_name, username, role)

    def remove_member(self, workspace_name, username):
        # TODO: ???

        return None

    def update_stage(self, workspace_name, stage):
        # TODO Doesn't seem to work.
        """

        :param workspace_name:
        :param stage: Define, Transform, Model, Deploy, Act
        :return:
        """
        workspace_id = self.get_id(workspace_name)
        url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        payload = {"stage": stage}
        response = self.session.put(url, data=payload, verify=False)
        return response.json()['response']

    def delete(self, workspace_name):
        """
        Attempts to delete the given workspace. Will fail if the workspace does not exist.

        :param str workspace_name: Workspace to be deleted.
        :return: None
        :rtype: NoneType
        :exception WorkspaceNotFoundException: The workspace does not exist.
        """

        try:
            workspace_id = self.get_id(workspace_name)
        except WorkspaceNotFoundException as err:
            self.logger.debug("Workspace not found, error {}".format(err))
        else:
            url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
            url = self._add_token_to_url(url)

            self.logger.debug("Deleting workspace {0} with id {1}".format(workspace_name, workspace_id))
            response = self.session.delete(url)
            self.logger.debug("Received response code {0} with reason {1}"
                              .format(response.status_code, response.reason))
            print("Workspace successfully deleted")
            return None
