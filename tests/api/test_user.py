from alpine import APIClient
from alpine.exception import *
from alpine.user import *
from alpine import *

from .alpineunittest import AlpineTestCase


class TestUser(AlpineTestCase):

    def setUp(self):
        super(TestUser, self).setUp()
        # Creating Alpine Client in setUp Function for tests
        global alpine_client
        global login_info
        alpine_client = APIClient(self.host, self.port,
                                  is_secure=self.is_secure,
                                  validate_certs=self.validate_certs,
                                  ca_certs=self.ca_certs)
        login_info = alpine_client.login(self.username, self.password)

    def test_create_user(self):
        try:
            user_id = alpine_client.user.get_id("apitest1")
            alpine_client.user.delete(user_id)
        except UserNotFoundException:
            pass
        user_info = alpine_client.user.create("apitest1", "test111", "test1", "test", "apitest1@alpinenow.com", "title",
                                               "dept", admin_role="admin", app_role=User.ApplicationRole.AnalyticsDeveloper)
        self.assertEqual(user_info['username'], "apitest1")
        alpine_client.logout()
        login_info = alpine_client.login("apitest1", "test111")
        self.assertEqual(login_info['username'], "apitest1")
        alpine_client.logout()
        alpine_client.login(self.username, self.password)
        alpine_client.user.delete(user_info['id'])

    def test_delete_user(self):
        try:
            user_id = alpine_client.user.get_id("apitest2")
            alpine_client.user.delete(user_id)
        except UserNotFoundException:
            pass

        user_info = alpine_client.user.create("apitest2", "password", "test2", "test2", "apitest2@alpinenow.com",
                                               "title", "dept", User.ApplicationRole.BusinessUser)
        alpine_client.user.delete(user_info['id'])
        # Verify the User is successfully deleted
        try:
            alpine_client.user.get(user_info['id'])
        except UserNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the User {0}".format("apitest2"))

    def test_update_user_info(self):
        try:
            user_id = alpine_client.user.get_id("apitest2")
            alpine_client.user.delete(user_id)
        except UserNotFoundException:
            pass

        user_info = alpine_client.user.create("apitest2", "password", "test2", "test2", "apitest2@alpinenow.com")
        updated_user_info = alpine_client.user.update(user_info['id'],"test2_new", "test2_new", "apitest2new@alpinenow.com",
                                  "title_new", "dept_new", "notes_new", "admin", User.ApplicationRole.DataAnalyst)
        user_info_new = alpine_client.user.get(user_info['id'])
        alpine_client.user.delete(user_info['id'])
        self.assertNotEquals(user_info, user_info_new)
        self.assertEqual(updated_user_info, user_info_new)

    def test_get_user_id(self):
        try:
            user_id = alpine_client.user.get_id("apitest1")
            alpine_client.user.delete(user_id)
        except UserNotFoundException:
            pass

        user_info = alpine_client.user.create("apitest1", "password", "test1", "test", "apitest1@alpinenow.com", "title",
                                             "dept", admin_role="admin", app_role=User.ApplicationRole.AnalyticsDeveloper)
        user_id = alpine_client.user.get_id("apitest1")
        self.assertEqual(user_id, user_info['id'])

    def test_get_user_info(self):
        user_id = alpine_client.user.get_id(self.username)
        user_info = alpine_client.user.get(user_id)
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['username'], self.username)

    def test_get_users_list(self):
        users_list1 = alpine_client.user.get_list(per_page=1)
        users_list2 = alpine_client.user.get_list(per_page=10)
        self.assertIsNotNone(users_list1)
        self.assertEqual(users_list1, users_list2)

