from alpine.apiclient import APIClient
from alpine.exception import *

from .alpineunittest import AlpineTestCase


class TestWorkspace(AlpineTestCase):

    def test_create_new_workspace(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            workspace_id = alpine_session.workspace.get_id("test_workspace1")
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info = alpine_session.workspace.create(workspace_name="test_workspace1", public=True, summary="Summary")
        self.assertEqual(workspace_info['name'],"test_workspace1")
        self.assertEqual(workspace_info['public'], True)
        self.assertEqual(workspace_info['summary'], "Summary")

    def test_get_workspace_details(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            workspace_id = alpine_session.workspace.get_id("test_workspace2")
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info_created = alpine_session.workspace.create(workspace_name="test_workspace2")
        workspace_info = alpine_session.workspace.get(workspace_info_created['id'])
        self.assertEqual(workspace_info_created, workspace_info)

    def test_get_workspace_id(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            workspace_id = alpine_session.workspace.get_id("test_workspace3")
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info_created = alpine_session.workspace.create(workspace_name="test_workspace3")
        workspace_id = alpine_session.workspace.get_id(workspace_name="test_workspace3")
        self.assertEqual(workspace_id, workspace_info_created['id'])

    def test_get_member_list_for_workspace(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            workspace_id = alpine_session.workspace.get_id("test_workspace4")
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info_created = alpine_session.workspace.create(workspace_name="test_workspace4")
        member_list = alpine_session.workspace.member.get_list(workspace_info_created['id'])
        self.assertEqual(workspace_info_created["members_count"], member_list.__len__())
        fail = True
        for member in member_list:
            if member['username'] == self.username:
                fail = False
                pass
        if fail:
            self.fail("failed to find owner {0} in member_list {1}".format(self.username, member_list))

    def test_get_workspaces_list(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        # user_id = alpine_session.user.get_id(self.username)
        # workspace_list1 = alpine_session.workspace.get_list(active=True, user_id=user_id, per_page=10)
        # workspace_list2 = alpine_session.workspace.get_list(active=True, user_id=user_id, per_page=100)
        user_id = alpine_session.user.get_id(self.username)
        workspace_list1 = alpine_session.workspace.get_list(active=True, user_id=user_id, per_page=10)
        workspace_list2 = alpine_session.workspace.get_list(active=True, user_id=user_id, per_page=100)
        self.assertEqual(workspace_list1, workspace_list2)
        workspace_list_all = alpine_session.workspace.get_list(active=True, per_page=10)
        workspace_number= 0
        for ws in workspace_list_all:
            member_list = alpine_session.workspace.member.get_list(ws['id'])
            contain_member = False
            for member in member_list:
                if member['username'] == self.username:
                    contain_member = True
                    print(ws['name'])
                    break
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


        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            workspace_id = alpine_session.workspace.get_id(test_workspace_name)
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info = alpine_session.workspace.create(workspace_name=test_workspace_name, public=test_workspace_is_public1,
                                       summary=test_workspace_summary1)
        workspace_info = alpine_session.workspace.update(workspace_info['id'], test_workspace_is_public2,
                                                         is_active=True, summary=test_workspace_summary2,
                                                         stage=test_workspace_stage2)
        self.assertEqual(workspace_info['summary'], test_workspace_summary2)
        self.assertEqual(workspace_info['public'], test_workspace_is_public2)
        self.assertEqual(workspace_info['workspace_stage']['id'], test_workspace_stage2)

    def test_update_workspace_membership(self):
        test_workspace_name = "test_workspace0"
        new_role = "Business Analyst"
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            workspace_id = alpine_session.workspace.get_id(test_workspace_name)
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info = alpine_session.workspace.create(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        user_id = alpine_session.user.get_id(self.username)
        member_list = alpine_session.workspace.member.update_role(workspace_info['id'], user_id, new_role)
        fail = True
        for member in member_list:
            if member['username'] == self.username:
                if member['role'] == new_role:
                    fail = False
                    break
        if fail:
            self.fail("User {0} Role is not update to {1}".format(self.username, member_list))

        alpine_session.workspace.delete(workspace_info['id'])

    def test_add_workspace_member(self):
        test_workspace_name = "test_workspace0"
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        new_role = alpine_session.workspace.memberRole.BusinessOwner
        try:
            user_id = alpine_session.user.get_id("test_user1")
            alpine_session.user.delete(user_id)
        except UserNotFoundException:
            pass
        user_info = alpine_session.user.create("test_user1", "password", "firstName", "lastName", "testuser1@alpine.test",
                         "QA", "Developement")

        try:
            workspace_id = alpine_session.workspace.get_id(test_workspace_name)
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info = alpine_session.workspace.create(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        member_list = alpine_session.workspace.member.add(workspace_info['id'], user_info['id'], alpine_session.workspace.memberRole.BusinessOwner)
        fail = True
        for member in member_list:
            if member['username'] == "test_user1":
                if member['role'] == new_role:
                    fail = False
                    break
        if fail:
            self.fail("User {0} Role is not update to {1}".format(self.username, member_list))

        alpine_session.workspace.delete(workspace_info['id'])

    def test_update_workspace_stage(self):
        test_workspace_name = "test_workspace1"
        # stages = ["Define", "Transform", "Model", "Deploy", "Act"]
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        stages = alpine_session.workspace.stage

        try:
            workspace_id = alpine_session.workspace.get_id(test_workspace_name)
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass

        workspace_info = alpine_session.workspace.create(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        for stage in stages:
            workspace_info = alpine_session.workspace.update(workspace_info['id'], stage=stage)
            self.assertEqual(workspace_info['workspace_stage']['id'], stage)

    def test_update_workspace_name(self):
        test_workspace_name = "test_workspace1"
        test_workspace_name_new = "test_workspace1_new"
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            workspace_id = alpine_session.workspace.get_id(test_workspace_name)
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        try:
            workspace_id = alpine_session.workspace.get_id(test_workspace_name_new)
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info = alpine_session.workspace.create(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        workspace_info = alpine_session.workspace.update(workspace_info['id'], name=test_workspace_name_new)
        self.assertEqual(workspace_info['name'], test_workspace_name_new)
        alpine_session.workspace.delete(workspace_info['id'])

    def test_update_workspace_owner(self):
        test_workspace_name = "test_workspace0"
        new_user = "new_user1"
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            user_id = alpine_session.user.get_id(new_user)
            alpine_session.user.delete(user_id)
        except UserNotFoundException:
            pass
        new_user_info = alpine_session.user.create(new_user, "password", "firstName", "lastName", "testuser1@alpine.test",
                         "QA", "Developement")

        try:
            workspace_id = alpine_session.workspace.get_id(test_workspace_name)
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info = alpine_session.workspace.create(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        alpine_session.workspace.member.add(workspace_info['id'], new_user_info['id'], "Data Engineer")
        workspace_info = alpine_session.workspace.update(workspace_info['id'], owner_id=new_user_info['id'])
        self.assertEqual(workspace_info['owner'], new_user_info)
        alpine_session.workspace.delete(workspace_info['id'])
        alpine_session.user.delete(new_user_info['id'])

    def test_update_workspace_owner_not_a_member(self):
        test_workspace_name = "test_workspace0"
        new_user = "new_user1"
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            user_id = alpine_session.user.get_id(new_user)
            alpine_session.user.delete(user_id)
        except UserNotFoundException:
            pass
        new_user_info = alpine_session.user.create(new_user, "password", "firstName", "lastName", "testuser1@alpine.test",
                         "QA", "Developement")

        try:
            workspace_id = alpine_session.workspace.get_id(test_workspace_name)
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info = alpine_session.workspace.create(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        try:
            workspace_info = alpine_session.workspace.update(workspace_info['id'], owner_id=new_user_info['id'])
        except WorkspaceMemberNotFoundException:
            pass
        alpine_session.workspace.delete(workspace_info['id'])
        alpine_session.user.delete(new_user_info['id'])

    def test_update_workspace_privacy(self):
        test_workspace_name = "test_workspace1"
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            workspace_id = alpine_session.workspace.get_id(test_workspace_name)
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass

        workspace_info = alpine_session.workspace.create(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        self.assertEqual(workspace_info['public'], True)
        for public in [False, True]:
            workspace_info = alpine_session.workspace.update(workspace_info['id'], is_public=public)
            self.assertEqual(workspace_info['public'], public)

    def test_update_workspace_status(self):
        test_workspace_name = "test_workspace1"
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            workspace_id = alpine_session.workspace.get_id(test_workspace_name)
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass

        workspace_info = alpine_session.workspace.create(workspace_name=test_workspace_name, public=True,
                                       summary="Summary")
        self.assertEqual(workspace_info['archived'], False)

        for is_active in [True, False]:
            workspace_info = alpine_session.workspace.update(workspace_info['id'], is_active = is_active)
            self.assertEqual(workspace_info['archived'], not is_active)

    def test_delete_workspace(self):
        test_workspace_name = "test_workspace0"
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            workspace_id = alpine_session.workspace.get_id(test_workspace_name)
            alpine_session.workspace.delete(workspace_id)
        except WorkspaceNotFoundException:
            pass
        workspace_info = alpine_session.workspace.create(workspace_name=test_workspace_name, public=True,
                                                        summary="Summary")
        alpine_session.workspace.delete(workspace_info['id'])
        # Verify the alpine_session.workspace is successfully deleted
        try:
            alpine_session.workspace.get(workspace_info['id'])
        except WorkspaceNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the alpine_session.workspace {0}".format(test_workspace_name))
        alpine_session.workspace.delete(workspace_info['id'])

