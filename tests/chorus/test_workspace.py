from api.alpine import Alpine
from api.workspace import Workspace

from api.exception import *
from chorusunittest import ChorusTestCase


class TestWorkspace(ChorusTestCase):

    def test_create_new_workspace(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.workspace.delete_workspace_if_exists(workspace_name="test_workspace1")
        workspace_info = alpine_session.workspace.create_new_workspace(workspace_name="test_workspace1", public=True, summary="Summary")
        self.assertEqual(workspace_info['name'],"test_workspace1")
        self.assertEqual(workspace_info['public'], True)
        self.assertEqual(workspace_info['summary'], "Summary")

    def test_get_workspace_details(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.workspace.delete_workspace_if_exists(workspace_name="test_workspace2")
        workspace_info_created = alpine_session.workspace.create_new_workspace(workspace_name="test_workspace2")
        workspace_info= alpine_session.workspace.get_workspace_info("test_workspace2")
        self.assertEqual(workspace_info_created, workspace_info)

    def test_get_workspace_id(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.workspace.delete_workspace_if_exists(workspace_name="test_workspace3")
        workspace_info_created = alpine_session.workspace.create_new_workspace(workspace_name="test_workspace3")
        workspace_id = alpine_session.workspace.get_workspace_id(workspace_name="test_workspace3")
        self.assertEqual(workspace_id,workspace_info_created['id'])

    def test_get_member_list_for_workspace(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.workspace.delete_workspace_if_exists(workspace_name="test_workspace4")
        workspace_info_created = alpine_session.workspace.create_new_workspace(workspace_name="test_workspace4")
        member_list = alpine_session.workspace.get_member_list_for_workspace(workspace_name="test_workspace4")
        self.assertEqual(workspace_info_created["members_count"], member_list.__len__())
        fail = True
        for member in member_list:
            if member['username'] == self.username:
                fail = False
                pass
        if fail:
            self.fail("failed to find owner {0} in member_list {1}".format(self.username, member_list))

    def test_get_workspaces_list(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        user_id = alpine_session.user.get_user_id(self.username)
        workspace_list1 = alpine_session.workspace.get_workspaces_list(active=True, user_id=user_id, per_page=10)
        workspace_list2 = alpine_session.workspace.get_workspaces_list(active=True, user_id=user_id, per_page=100)
        self.assertEqual(workspace_list1,workspace_list2)
        workspace_list_all = alpine_session.workspace.get_workspaces_list(active=True,per_page=10)
        workspace_number= 0
        for ws in workspace_list_all:
            member_list = alpine_session.workspace.get_member_list_for_workspace(ws['name'])
            contain_member = False
            for member in member_list:
                if member['username'] == self.username:
                    contain_member = True
                    print ws['name']
                    break;
            if contain_member:
                workspace_number = workspace_number + 1
        self.assertEqual(workspace_number, workspace_list1.__len__())

    def test_update_workspace_details(self):
        test_workspace_name = "test_workspace0"
        test_workspace_summary1 = "Summary 1"
        test_workspace_summary2 = "Summary 2"
        test_workspace_is_public1 = False
        test_workspace_is_public2 = True
        test_workspace_is_public1 = False
        test_workspace_is_public2 = True
        test_workspace_stage2 = 2


        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.workspace.delete_workspace_if_exists(workspace_name=test_workspace_name)
        alpine_session.workspace.create_new_workspace(workspace_name=test_workspace_name, public=test_workspace_is_public1,
                                       summary=test_workspace_summary1)
        workspace_info = alpine_session.workspace.update_workspace_details(test_workspace_name, test_workspace_is_public2,
                                                            is_active=True, summary=test_workspace_summary2,
                                                            stage_id=test_workspace_stage2)
        self.assertEqual(workspace_info['summary'], test_workspace_summary2)
        self.assertEqual(workspace_info['public'], test_workspace_is_public2)
        self.assertEqual(workspace_info['workspace_stage']['id'], test_workspace_stage2)

    def test_update_workspace_membership(self):
        test_workspace_name = "test_workspace0"
        new_role = "Business Analyst"
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.workspace.delete_workspace_if_exists(workspace_name=test_workspace_name)
        alpine_session.workspace.create_new_workspace(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        user_id = alpine_session.user.get_user_id("demoadmin")
        member_list = alpine_session.workspace.update_workspace_membership(test_workspace_name, user_id, new_role)
        fail = True
        for member in member_list:
            if member['username'] == self.username:
                if member['role'] == new_role:
                    fail = False
                    break
        if fail:
            self.fail("User {0} Role is not update to {1}".format(self.username, member_list))

        alpine_session.workspace.delete_workspace(test_workspace_name)

    def test_add_workspace_member(self):
        test_workspace_name = "test_workspace0"
        new_role = "Business Analyst"
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.user.delete_user_if_exists("test_user1")
        user_info = alpine_session.user.create_user("test_user1", "password", "firstName", "lastName", "testuser1@alpine.test",
                         "QA", "Developement")
        alpine_session.workspace.delete_workspace_if_exists(workspace_name=test_workspace_name)
        alpine_session.workspace.create_new_workspace(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        member_list = alpine_session.workspace.update_workspace_membership(test_workspace_name, user_info['id'], new_role)
        fail = True
        for member in member_list:
            if member['username'] == "test_user1":
                if member['role'] == new_role:
                    fail = False
                    break
        if fail:
            self.fail("User {0} Role is not update to {1}".format(self.username, member_list))

        alpine_session.workspace.delete_workspace(test_workspace_name)

    def test_update_workspace_stage(self):
        test_workspace_name = "test_workspace1"
        stages = ["Define", "Transform", "Model", "Deploy", "Act"]
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.workspace.delete_workspace_if_exists(workspace_name=test_workspace_name)
        alpine_session.workspace.create_new_workspace(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        for i in range(1, len(stages)):
            workspace_info = alpine_session.workspace.update_workspace_details(test_workspace_name, stage_id=i)
            self.assertEqual(workspace_info['workspace_stage']['name'], stages[i-1])

    def test_update_workspace_name(self):
        test_workspace_name = "test_workspace1"
        test_workspace_name_new = "test_workspace1_new"
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.workspace.delete_workspace_if_exists(workspace_name=test_workspace_name)
        alpine_session.workspace.delete_workspace_if_exists(workspace_name=test_workspace_name_new)
        alpine_session.workspace.create_new_workspace(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        workspace_info = alpine_session.workspace.update_workspace_name(test_workspace_name, test_workspace_name_new)
        self.assertEqual(workspace_info['name'], test_workspace_name_new)
        alpine_session.workspace.delete_workspace_if_exists(workspace_name=test_workspace_name_new)

    def test_update_workspace_owner(self):
        test_workspace_name = "test_workspace0"
        new_user = "new_user1"
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.user.delete_user_if_exists(new_user)
        new_user_info = alpine_session.user.create_user(new_user, "password", "firstName", "lastName", "testuser1@alpine.test",
                         "QA", "Developement")
        alpine_session.workspace.delete_workspace_if_exists(workspace_name=test_workspace_name)
        alpine_session.workspace.create_new_workspace(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        alpine_session.workspace.add_workspace_member(test_workspace_name, new_user_info['id'], "Data Engineer")
        workspace_info = alpine_session.workspace.update_workspace_details(workspace_name=test_workspace_name, owner_id=new_user_info['id'])
        self.assertEqual(workspace_info['owner'], new_user_info)
        alpine_session.workspace.delete_workspace(test_workspace_name)
        alpine_session.user.delete_user(new_user)

    def test_delete_workspace(self):
        test_workspace_name = "test_workspace0"
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.workspace.delete_workspace_if_exists(workspace_name=test_workspace_name)
        alpine_session.workspace.create_new_workspace(workspace_name=test_workspace_name, public=True,
                                                        summary="Summary")
        response = alpine_session.workspace.delete_workspace(workspace_name=test_workspace_name)
        self.assertEqual(response.status_code, 200)
        # Verify the alpine_session.workspace is successfully deleted
        try:
            alpine_session.workspace.get_workspace_info(workspace_name=test_workspace_name)
        except WorkspaceNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the alpine_session.workspace {0}".format(test_workspace_name))
