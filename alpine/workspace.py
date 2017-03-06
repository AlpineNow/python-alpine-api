from __future__ import absolute_import

from .exception import *
from .alpineobject import AlpineObject
from .user import User

import json


class Workspace(AlpineObject):
    """
    A class for interacting with workspaces. Top-level methods deals with workspace properties. The subclass
    Members can be used to interact with member lists.

    """
    member = None

    @property
    def stage(self):
        return self.Stage()

    @property
    def memberRole(self):
        return self.MemberRole()

    def __init__(self, base_url, session, token):
        super(Workspace, self).__init__(base_url, session, token)
        self.member = self.Member(base_url, session, token)

    def create(self, workspace_name, public=False, summary=None):
        """
        Creates a workspace. Will fail if the workspace_name already exists.

        :param str workspace_name: Unique workspace name.
        :param bool public: Allow the workspace to be viewable by non-members and non-admins.
        :param str summary: Description of new workspace.
        :return: Created workspace information or error message.
        :rtype: dict

        Example::

            >>> session.workspace.create(workspace_name = "Public Data ETL", public = True)

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

        :param str workspace_id: ID number of the workspace to be deleted.
        :return: None
        :rtype: NoneType
        :exception WorkspaceNotFoundException: The workspace does not exist.

        Example::

            >>> session.workspace.delete(workspace_id = 1671)

        """

        try:
            self.get(workspace_id)
            url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
            url = self._add_token_to_url(url)

            self.logger.debug("Deleting workspace with ID: {0}".format(workspace_id))
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
            self.logger.debug("Workspace not found, error {0}".format(err))

    def get_list(self, user_id=None, active=None, per_page=50):
        """
        Get a list of metadata for each workspace. If username is provided, only workspaces that the user \
        is a member of will be returned.

        :param str user_id: ID number of the user.
        :param bool active: Optionally only return active workspaces. True will return only the active spaces.
        :param int per_page: How many workspaces to return in each page.

        :return: List of workspace metadata.
        :rtype: list of dict
        :exception UserNotFoundException: The username does not exist.

        Example::

            >>> my_workspaces = session.workspace.get_list(user_id = my_user_id)
            >>> len(my_workspaces)
            8

        """

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
        Get one workspace's metadata.

        :param str workspace_id: Unique workspace name.
        :return: Single workspace's data
        :rtype: dict
        :exception WorkspaceNotFoundException: The workspace does not exist.

        Example::

            >>> session.workspace.get(workspace_id = 1761)

        """

        url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)

        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")

        r = self.session.get(url, verify=False)
        workspace_response = r.json()
        try:
            if workspace_response['response']:
                self.logger.debug("Found workspace ID: <{0}> in list...".format(workspace_id))
                return workspace_response['response']
            else:
                raise WorkspaceNotFoundException("Workspace ID: <{0}> not found".format(workspace_id))
        except Exception as err:
            raise WorkspaceNotFoundException("Workspace ID: <{0}> not found".format(workspace_id))

    def get_id(self, workspace_name, user_id=None):
        """
        Get the ID number of the workspace. Will throw an exception if the workspace does not exist.

        :param str workspace_name: Unique workspace name.
        :param int user_id: ID number of a user.
        :return: ID number of the workspace.
        :rtype: int
        :exception WorkspaceNotFoundException: The workspace does not exist.

        Example::

            >>> session.workspace.get_id("Public Data ETL")
            1672

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
        """
        Update a workspace's metadata. Only included fields will be changed.

        :param int workspace_id: ID number of the workspace.
        :param bool is_public: Allow the workspace to be viewable by non-members and non-admins.
        :param bool is_active: Sets active vs. archived status.
        :param str name: New name for the workspace.
        :param str summary: New description of the workspace.
        :param int stage: Stage ID number. Use the Workspace.Stage object for convenience.
        :param int owner_id: ID number of the new workspace owner. Must also be a member of the workspace.
        :return: Updated workspace metadata
        :rtype: dict

        Example::

            >>> session.workspace.update(workspace_id = 1672, summary = "New focus of project is ML!",
            >>>                          stage = session.workspace.stage.Model)

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
        if is_public is not None:
            payload["public"] = is_public
            # payload["public"] = str(is_public).lower()
        if is_active is not None:
            payload["archived"] = not is_active
            # payload["archived"] = str(not is_active).lower()
        if name:
            payload["name"] = name
        if summary:
            payload["summary"] = summary
        if stage:
            payload["workspace_stage_id"] = stage
        if owner_id:
            is_member = False
            members = self.member.get_list(workspace_id)
            for member in members:
                if member['id'] == owner_id:
                    is_member = True
                    self.logger.debug("User with ID: <{0}> is a member of the workspace Id: <{1}>, OK to update owner"
                                      .format(owner_id, workspace_id))
                    payload["owner_id"] = owner_id
            if not is_member:
                raise WorkspaceMemberNotFoundException("The user with Id: <{0}> is not a member of workspace ID: <{1}> "
                                                       "Cannot assign as the new owner."
                                                       .format(owner_id, workspace_id)
                                                       )

        for field in pop_fields:
            payload.pop(field)

        self.session.headers.update({"Content-Type": "application/json"})  # Set special header for this post
        response = self.session.put(url, data=json.dumps(payload), verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        self.session.headers.pop("Content-Type")  # Remove header, as it affects other tests
        return response.json()['response']

    class Member(AlpineObject):
        """
        A class for interacting with workspace membership.
        """

        def __init__(self, base_url, session, token):
            super(Workspace.Member, self).__init__(base_url, session, token)

        def get_list(self, workspace_id, per_page=100):
            """
            Gets metadata about all the users who are members of the workspace.

            :param str workspace_id: ID number of the workspace.
            :param int int per_page: Maximum number to fetch with each API call.
            :return: A list of user data.
            :rtype: list of dict
            :exception WorkspaceNotFoundException: The workspace does not exist.

            Example::

                >>> session.workspace.member.get_list(workspace_id = 1672)

            """

            # Check that workspace exists.
            Workspace(self.base_url, self.session, self.token).get(workspace_id)

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

        def add(self, workspace_id, user_id, role=None):
            """
            Add a new user to the workspace member list.

            :param int workspace_id: ID number of the workspace.
            :param int user_id: ID number of member to add to the workspace.
            :param str role: Role for the user. Use Workspace.MemberRole for convenience.
            :return: Updated member list.
            :rtype: list of dict
            :exception WorkspaceNotFoundException: The workspace ID number does not exist.
            :exception UserNotFoundException: The user ID number does not exist.

            Example::

                >>> session.workspace.member.add(workspace_id = 1672, user_id = 7,
                >>>                              role = session.workspace.memberRole.DataScientist)

            """
            if role is None:
                role = Workspace.MemberRole.ProjectMember
            members = self.get_list(workspace_id)
            user_info = User(self.base_url, self.session, self.token).get(user_id)
            members.append(user_info)
            member_list = []
            for member in members:
                if member['id'] == user_id:
                    continue
                else:
                    member_list.append({"user_id": member['id'], "role": member['role']})
            member_list.append({"user_id": user_id, "role": role})

            return self.__update(workspace_id, member_list)

        def remove(self, workspace_id, user_id):
            """
            Remove a user from the workspace member list.

            :param int workspace_id: ID number of the workspace.
            :param int user_id: ID number of member to add to the workspace.
            :return: Updated member list.
            :rtype: list of dict
            :exception WorkspaceNotFoundException: The workspace Id number does not exist.
            :exception UserNotFoundException: The user Id number  does not exist.

            Example::

                >>> session.workspace.member.remove(workspace_id = 1672, user_id = 7)

            """
            # Check that user exists.
            User(self.base_url, self.session, self.token).get(user_id)

            members = self.get_list(workspace_id)
            new_members = []
            for member in members:
                if member['id'] == user_id:
                    self.logger.debug(
                        "Remove the user with ID: <{0}> from workspace with ID <{1}>".format(user_id, workspace_id)
                    )
                    continue
                else:
                    new_members.append({"user_id": member['id'], "role": member['role']})
            return self.__update(workspace_id, new_members)

        def update_role(self, workspace_id, user_id, new_role):
            """
            Update a user's role in a workspace. If the user is not a member of the workspace then no change will be
            made.

            :param int workspace_id: ID number of the workspace.
            :param int user_id: ID number of member to update.
            :param str new_role: New role for the user. Use Workspace.MemberRole for convenience.

            :return: Updated member list
            :rtype: list of dict
            :exception WorkspaceNotFoundException: The workspace does not exist.

            Example::

                >>> session.workspace.member.update(workspace_id = 1672, user_id = 7,
                >>>                                 new_role = session.workspace.memberRole.DataScientist)

            """
            members = self.get_list(workspace_id)
            updated_members = []

            # Update the membership list
            for member in members:
                if member['id'] == user_id:
                    updated_members.append({"user_id": member['id'], "role": new_role})
                else:
                    updated_members.append({"user_id": member['id'], "role": member["role"]})

            return self.__update(workspace_id, updated_members)

        def __update(self, workspace_id, members):
            """
            General update member method. Mostly for internal use. Used by add, remove, and update.

            :param int workspace_id: ID number of the workspace.
            :param list members: A formatted member list.
            :return: member list or error.
            """
            url = "{0}/workspaces/{1}/members".format(self.base_url, workspace_id)
            url = self._add_token_to_url(url)
            payload = {"collection": {}, "members": members}
            self.session.headers.update({"Content-Type": "application/json"})
            response = self.session.post(url, data=json.dumps(payload), verify=False)
            self.session.headers.pop("Content-Type")
            self.logger.debug("Received response code {0} with reason {1}...".
                              format(response.status_code, response.reason))

            try:
                return response.json()['response']
            except:
                return response.json()

    class Stage(object):
        """
        Convenience IDs for workspace stages.
        """
        Define = 1
        Transform = 2
        Model = 3
        Deploy = 4
        Act = 5

        def __init__(self):
            pass

        def __iter__(self):
            i = self.Define
            while i < self.Act:
                yield i
                i += 1

    class MemberRole(object):
        """
        Convenience strings for user workspace member roles.
        """
        ProjectMember = "Project Member"
        BusinessOwner = "Business Owner"
        BusinessAnalyst = "Business Analyst"
        DataScienceManager = "Data Science Manager"
        DataScientist = "Data Scientist"
        DataEngineer = "Data Engineer"
        ApplicationEngineer = "Application Engineer"
        ProjectManager = "Project Manager"
