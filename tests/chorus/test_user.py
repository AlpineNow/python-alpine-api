from chorusunittest import ChorusTestCase
from api.chorus.chorus import Chorus
from api.chorus.user import User
from api.exception import *


class TestUser(ChorusTestCase):

    def test_create_user(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        user_session = User(chorus_session)
        user_session.delete_user_if_exists("test1")
        user_info = user_session.create_user("test1", "test111", "test1", "test", "test1@alpinenow.com", "title", "dept",
                                     admin="admin", user_type="analytics_developer")
        self.assertEqual(user_info['username'], "test1")
        chorus_session.logout()
        login_info = chorus_session.login("test1", "test111")
        self.assertEqual(login_info['response']['user']['username'], "test1")
        chorus_session.logout()
        chorus_session.login(self.username, self.password)
        user_session = User(chorus_session)
        user_session.delete_user("test1")

    def test_delete_user(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        user_session = User(chorus_session)
        user_session.delete_user_if_exists("test2")
        user_info = user_session.create_user("test2", "password", "test2", "test2", "test2@alpinenow.com", "title", "dept")
        response = user_session.delete_user("test2")
        self.assertEqual(response.status_code, 200)
        # Verify the User is successfully deleted
        try:
            user_session.get_user_info("test2")
        except UserNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the User {0}".format("test2"))

    def test_update_user_info(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        user_session = User(chorus_session)
        user_session.delete_user_if_exists("test2")
        user_info = user_session.create_user("test2", "password", "test2", "test2", "test2@alpinenow.com", "title", "dept")
        updated_user_info = user_session.update_user_info("test2","test2_new", "test2_new", "test2new@alpinenow.com",
                                  "title_new", "dept_new", "notes_new", "admin", "data_analyst")
        user_info_new = user_session.get_user_info("test2")
        user_session.delete_user("test2")
        self.assertNotEquals(user_info, user_info_new)
        self.assertEqual(updated_user_info, user_info_new)

    def test_get_user_id(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        user_session = User(chorus_session)
        user_session.delete_user_if_exists("test1")
        user_info = user_session.create_user("test1", "password", "test1", "test", "test1@alpinenow.com", "title",
                                             "dept",
                                             admin="admin", user_type="analytics_developer")
        user_id = user_session.get_user_id("test1")
        self.assertEqual(user_id, user_info['id'])

    def test_get_user_info(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        user_session = User(chorus_session)
        user_info = user_session.get_user_info(self.username)
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['username'], self.username)

    def test_get_users_list(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        user_session = User(chorus_session)
        users_list1 = user_session.get_users_list(per_page=1)
        users_list2 = user_session.get_users_list(per_page=10)
        self.assertIsNotNone(users_list1)
        self.assertEqual(users_list1, users_list2)

