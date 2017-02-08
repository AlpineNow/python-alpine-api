from api.alpine import Alpine
from api.user import User
from api.exception import *
from alpineunittest import AlpineTestCase


class TestUser(AlpineTestCase):

    def test_create_user(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.user.delete("test1")
        user_info = alpine_session.user.create("test1", "test111", "test1", "test", "test1@alpinenow.com", "title",
                                               "dept", admin_role="admin", app_role="analytics_developer")
        self.assertEqual(user_info['username'], "test1")
        alpine_session.logout()
        login_info = alpine_session.login("test1", "test111")
        self.assertEqual(login_info['response']['user']['username'], "test1")
        alpine_session.logout()
        alpine_session.login(self.username, self.password)
        alpine_session.user.delete("test1")

    def test_delete_user(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.user.delete("test2")
        user_info = alpine_session.user.create("test2", "password", "test2", "test2", "test2@alpinenow.com", "title", "dept")
        alpine_session.user.delete("test2")
        # Verify the User is successfully deleted
        try:
            alpine_session.user.get_data("test2")
        except UserNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the User {0}".format("test2"))

    def test_update_user_info(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.user.delete("test2")
        user_info = alpine_session.user.create("test2", "password", "test2", "test2", "test2@alpinenow.com", "title", "dept")
        updated_user_info = alpine_session.user.update("test2","test2_new", "test2_new", "test2new@alpinenow.com",
                                  "title_new", "dept_new", "notes_new", "admin", "data_analyst")
        user_info_new = alpine_session.user.get_data("test2")
        alpine_session.user.delete("test2")
        self.assertNotEquals(user_info, user_info_new)
        self.assertEqual(updated_user_info, user_info_new)

    def test_get_user_id(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.user.delete("test1")
        user_info = alpine_session.user.create("test1", "password", "test1", "test", "test1@alpinenow.com", "title",
                                             "dept", admin_role="admin", app_role="analytics_developer")
        user_id = alpine_session.user.get_id("test1")
        self.assertEqual(user_id, user_info['id'])

    def test_get_user_info(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        user_info = alpine_session.user.get_data(self.username)
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['username'], self.username)

    def test_get_users_list(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        users_list1 = alpine_session.user.get_all(per_page=1)
        users_list2 = alpine_session.user.get_all(per_page=10)
        self.assertIsNotNone(users_list1)
        self.assertEqual(users_list1, users_list2)

