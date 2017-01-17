import json
from api.exception import *
from api.alpineobject import AlpineObject


class Workspace(AlpineObject):

    def __init__(self, base_url, session, token):
        super(Workspace, self).__init__(base_url, session, token)

    def create_new_workspace(self, workspace_name, public=False, summary=None):
        """

        :param workspace_name:
        :param public:
        :param summary:
        :return:
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
        return response.json()['response']

    def get_workspace_info(self, workspace_name):
        """

        :param workspace_name:
        :return:
        """
        workspace_list = self.get_workspaces_list()
        for workspace in workspace_list:
            if workspace['name'] == workspace_name:
                self.logger.debug ("Found workspace {0} in list...".format(workspace_name))
                return workspace
        raise WorkspaceNotFoundException("Workspace {0} not found".format(workspace_name))

    def get_workspace_id(self, workspace_name):
        """

        :param workspace_name:
        :return:
        """
        workspace_info = self.get_workspace_info(workspace_name)
        return workspace_info['id']

    def get_member_list_for_workspace(self, workspace_name, per_page=100):
        """

        :param workspace_name:
        :param per_page:
        :return:
        """
        workspace_id = self.get_workspace_id(workspace_name)
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
                break;
        return member_list

    def get_workspaces_list(self, active=False, user_id=None, per_page=100,):
        """

        :param active:
        :param user_id:
        :param per_page:
        :return:
        """
        workspace_list = None
        url = "{0}/workspaces".format(self.base_url)
        url = self._add_token_to_url(url)
        if user_id:
            url = "{0}&user_id={1}".format(url, user_id)
        str_active = "false"
        if active:
            str_active = "true"
        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")
        page_current = 0
        while True:
            payload = {"active": str_active,
                       "per_page": per_page,
                       "page": page_current + 1,
                       }
            workspace_list_response = self.session.get(url, data=json.dumps(payload), verify=False).json()
            page_total = workspace_list_response['pagination']['total']
            page_current = workspace_list_response['pagination']['page']
            if workspace_list:
                workspace_list.extend(workspace_list_response['response'])
            else:
                workspace_list = workspace_list_response['response']
            if page_total == page_current:
                break;

#        url = url + "&page=1&per_page=1000&user_id={0}".format(user_id)
        return workspace_list

    def update_workspace_name(self, workspace_name, new_workspace_name):
        """

        :param workspace_name:
        :param new_workspace_name:
        :return:
        """
        workspace_id = self.get_workspace_id(workspace_name)
        if workspace_id is None:
            raise WorkspaceNotFoundException("Workspace {0} was not found".format(workspace_name))
        url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        payload = self.get_workspace_info(workspace_name)

        # replace fields with updated ones from kwargs
        payload["name"] = new_workspace_name
        self.session.headers.update({"Content-Type": "application/json"})  # Set special header for this post
        response = self.session.put(url, data=json.dumps(payload), verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        self.session.headers.pop("Content-Type")  # Remove header, as it affects other tests
        return response.json()['response']

    def update_workspace_details(self, workspace_name=None, is_public=None, is_active=None,
                                      summary=None, stage_id=None, owner_id=None, ):
        """

        :param workspace_name:
        :param is_public:
        :param is_active:
        :param summary:
        :param stage_id:
        :param owner_id:
        :return:
        """
        workspace_id = self.get_workspace_id(workspace_name)
        if workspace_id is None:
            raise WorkspaceNotFoundException("Workspace {0} was not found".format(workspace_name))
        url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        payload = self.get_workspace_info(workspace_name)

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

    def update_workspace_membership(self, workspace_name, user_id, role):
        """

        :param workspace_name:
        :param username:
        :param role:
        :return:
        """
        workspace_id = self.get_workspace_id(workspace_name)
        url = "{0}/workspaces/{1}/members".format(self.base_url,workspace_id)
        url = self._add_token_to_url(url)
        # Build payload with user ids and role
        members = []
        member_list = self.get_member_list_for_workspace(workspace_name)
        # If the user is not an member, add the user,
        # if the user is already a member of the workspace, update the user role
        for member in member_list:
            if member['id']== user_id:
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

    def add_workspace_member(self, workspace_name, username, role):
        """

        :param workspace_name:
        :param username:
        :param role:
        :return:
        """
        return self.update_workspace_membership(workspace_name, username, role)

    def update_workspace_stage(self, workspace_name, stage):
        """

        :param workspace_name:
        :param stage:
        :return:
        """
        workspace_id = self.get_workspace_id(workspace_name)
        url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        payload = {"stage": stage}
        response = self.session.put(url, data=payload, verify=False)
        return response.json()['response']

    def delete_workspace(self, workspace_name):
        """

        :param workspace_name:
        :return:
        """
        workspace_id = self.get_workspace_id(workspace_name)
        url = "{0}/workspaces/{1}".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)

        self.logger.debug("Deleting workspace {0} with id {1}".format(workspace_name, workspace_id))
        response = self.session.delete(url)
        self.logger.debug("Received response code {0} with reason {1}".format(response.status_code, response.reason))
        return response

    def delete_workspace_if_exists(self, workspace_name):
        """

        :param workspace_name:
        :return:
        """
        try:
            self.delete_workspace(workspace_name)
        except WorkspaceNotFoundException:
            self.logger.debug ("Workspace {0} not found, don't need to delete the Workspace".format(workspace_name))