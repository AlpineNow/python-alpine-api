from alpineapi.alpine import Alpine
from alpineapi.exception import *

from alpineunittest import AlpineTestCase


class TestUser(AlpineTestCase):

    def test_create_user(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            user_id = alpine_session.user.get_id("apitest1")
            alpine_session.user.delete(user_id)
        except UserNotFoundException:
            pass
        user_info = alpine_session.user.create("apitest1", "test111", "test1", "test", "apitest1@alpinenow.com", "title",
                                               "dept", admin_role="admin", app_role=alpine_session.user.applicationRole.AnalyticsDeveloper)
        self.assertEqual(user_info['username'], "apitest1")
        alpine_session.logout()
        login_info = alpine_session.login("apitest1", "test111")
        self.assertEqual(login_info['username'], "apitest1")
        alpine_session.logout()
        alpine_session.login(self.username, self.password)
        alpine_session.user.delete(user_info['id'])

    def test_delete_user(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            user_id = alpine_session.user.get_id("apitest2")
            alpine_session.user.delete(user_id)
        except UserNotFoundException:
            pass

        user_info = alpine_session.user.create("apitest2", "password", "test2", "test2", "apitest2@alpinenow.com", "title", "dept",alpine_session.user.applicationRole.BusinessUser)
        alpine_session.user.delete(user_info['id'])
        # Verify the User is successfully deleted
        try:
            alpine_session.user.get(user_info['id'])
        except UserNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the User {0}".format("apitest2"))

    def test_update_user_info(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            user_id = alpine_session.user.get_id("apitest2")
            alpine_session.user.delete(user_id)
        except UserNotFoundException:
            pass

        user_info = alpine_session.user.create("apitest2", "password", "test2", "test2", "apitest2@alpinenow.com", "title", "dept")
        updated_user_info = alpine_session.user.update(user_info['id'],"test2_new", "test2_new", "apitest2new@alpinenow.com",
                                  "title_new", "dept_new", "notes_new", "admin", alpine_session.user.applicationRole.DataAnalyst)
        user_info_new = alpine_session.user.get(user_info['id'])
        alpine_session.user.delete(user_info['id'])
        self.assertNotEquals(user_info, user_info_new)
        self.assertEqual(updated_user_info, user_info_new)

    def test_get_user_id(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        try:
            user_id = alpine_session.user.get_id("apitest1")
            alpine_session.user.delete(user_id)
        except UserNotFoundException:
            pass

        user_info = alpine_session.user.create("apitest1", "password", "test1", "test", "apitest1@alpinenow.com", "title",
                                             "dept", admin_role="admin", app_role=alpine_session.user.applicationRole.AnalyticsDeveloper)
        user_id = alpine_session.user.get_id("apitest1")
        self.assertEqual(user_id, user_info['id'])

    def test_get_user_info(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        user_id = alpine_session.user.get_id(self.username)
        user_info = alpine_session.user.get(user_id)
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['username'], self.username)

    def test_get_users_list(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        users_list1 = alpine_session.user.get_list(per_page=1)
        users_list2 = alpine_session.user.get_list(per_page=10)
        self.assertIsNotNone(users_list1)
        self.assertEqual(users_list1, users_list2)

