from __future__ import absolute_import

from api.exception import *
from api.alpineobject import AlpineObject
from .user import User

import json


class Workspace(AlpineObject):
    """
    A collection of API wrappers and helper methods to interact with Alpine workspaces.

    """
    member = None

    def __init__(self, base_url, session, token):
        super(Workspace, self).__init__(base_url, session, token)
        self.member = self.Member(base_url, session, token)
        self.WorkspaceStage = self.WorkspaceStage()
        self.WorkspaceMemberRole = self.WorkspaceMemberRole()

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

    def delete(self, workspace_id):
        """
        Attempts to delete the given workspace. Will fail if the workspace does not exist.

        :param str workspace_name: Workspace to be deleted.
        :return: None
        :rtype: NoneType
        :exception WorkspaceNotFoundException: The workspace does not exist.
        """

        try:
            self.get(workspace_id)
            url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
            url = self._add_token_to_url(url)

            self.logger.debug("Deleting workspace with id {0}".format(workspace_id))
            response = self.session.delete(url)
            self.logger.debug("Received response code {0} with reason {1}"
                              .format(response.status_code, response.reason))
            if response.status_code == 200:
                self.logger.debug("Workspace successfully deleted.")
            else:
                raise InvalidResponseCodeException("Response Code Invalid, the expected Response Code is {0}, "
                                                   "the actual Response Code is {1}".format(200, response.status_code))
            return None
        except WorkspaceNotFoundException as err:
            self.logger.debug("Workspace not found, error {}".format(err))

    def get_list(self, user_id=None, active=None, per_page=50):
        """
        Get a list of metadata for each workspace. If username is provided, only workspaces that the user \
        is a member of will be returned.

        :param str user_id: Id of the user.
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

    def get(self, workspace_id):
        """
        Get the one workspace's metadata.

        :param str workspace_id: Unique workspace name.
        :return: Single workspace's data
        :rtype: dict
        :exception WorkspaceNotFoundException: The workspace does not exist.
        """

        url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)

        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")

        r = self.session.get(url, verify=False)
        workspace_response = r.json()
        try:
            if workspace_response['response']:
                self.logger.debug("Found workspace id: <{0}> in list...".format(workspace_id))
                return workspace_response['response']
            else:
                raise WorkspaceNotFoundException("Workspace id: <{0}> not found".format(workspace_id))
        except Exception as err:
            raise WorkspaceNotFoundException("Workspace id: <{0}> not found".format(workspace_id))

    def get_id(self, workspace_name, user_id=None):
        """
        Get the ID number of the workspace. Will throw an exception if the workspace doens't exist.

        :param str workspace_name: Unique workspace name.
        :return: ID number of the workspace.
        :rtype: int
        :exception WorkspaceNotFoundException: The workspace does not exist.
        """
        workspace_list = self.get_list(user_id)
        for workspace in workspace_list:
            if workspace['name'] == workspace_name:
                return workspace['id']
        # return None
        raise WorkspaceNotFoundException("The workspace with name <{0}> is not found for user <{1}>".format(
            workspace_name, user_id))

    def update(self, workspace_id, is_public=None, is_active=None, name=None,
               summary=None, stage=None, owner_id=None):
        # TODO: Can we combine with update_name??
        """

        :param workspace_id:
        :param is_public:
        :param is_active:
        :param name:
        :param summary:
        :param stage:
        :param owner_id:
        :return:
        """

        url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        payload = self.get(workspace_id)

        # get rid of fields that aren't required for PUT to reduce request size.
        pop_fields = ['complete_json',
                      'entity_type',
                      'id',
                      'image',
                      'is_deleted',
                      'workspace_stage'
                      ]

        # replace fields with updated ones from kwargs
        if is_public:
            payload["public"] = is_public
        if is_active:
            payload["archived"] = not is_active
        if name:
            payload["name"] = name
        if summary:
            payload["summary"] = summary
        if stage:
            payload["workspace_stage_id"] = stage
        if owner_id:
            payload["owner_id"] = owner_id

        for field in pop_fields:
            payload.pop(field)

        self.session.headers.update({"Content-Type": "application/json"})  # Set special header for this post
        response = self.session.put(url, data=json.dumps(payload), verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        self.session.headers.pop("Content-Type")  # Remove header, as it affects other tests
        return response.json()['response']

    class Member(AlpineObject):
        """
        A collection of API wrappers and helper methods to interact workspace members.
        """

        def __init__(self, base_url, session, token):
            super(Workspace.Member, self).__init__(base_url, session, token)

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
            """
            Placeholder

            :param workspace_id:
            :param user_id:
            :return:
            """
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
            """
            Internal
            :param workspace_id:
            :param members:
            :return:
            """
            url = "{0}/workspaces/{1}/members".format(self.base_url, workspace_id)
            url = self._add_token_to_url(url)
            payload = {"collection": {}, "members": members}
            self.session.headers.update({"Content-Type": "application/json"})
            response = self.session.post(url, data=json.dumps(payload), verify=False)
            self.session.headers.pop("Content-Type")
            self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
            return response.json()['response']

    class WorkspaceStage(object):
        def __init__(self):
            self.Define = 1
            self.Transform = 2
            self.Model = 3
            self.Deploy = 4
            self.Act = 5

    class WorkspaceMemberRole(object):
        def __init__(self):
            self.ProjectMember = "Project Member"
            self.BusinessOwner = "Business Owner"
            self.BusinessAnalyst = "Business Analyst"
            self.DataScienceManager = "Data Science Manager"
            self.DataScientist = "Data Scientist"
            self.DataEngineer = "Data Engineer"
            self.ApplicationEngineer = "Application Engineer"
            self.ProjectManager = "Project Manager"