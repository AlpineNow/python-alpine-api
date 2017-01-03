from chorusunittest import ChorusTestCase
from api.chorus.chorus import Chorus
from api.chorus.user import User
from api.exception import *


class TestUser(ChorusTestCase):

    def test_create_user(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        user = User(chorus_session)
        user.delete_user_if_exists("test1")
        user_info = user.create_user("test1", "test111", "test1", "test", "test1@alpinenow.com", "title", "dept",
                                     admin="admin", user_type="analytics_developer")
        self.assertEqual(user_info['username'], "test1")
        chorus_session.logout()
        login_info = chorus_session.login("test1", "test111")
        self.assertEqual(login_info['response']['user']['username'], "test1")
        chorus_session.logout()
        chorus_session.login(self.username, self.password)
        user = User(chorus_session)
        user.delete_user("test1")

    def test_delete_user(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        user = User(chorus_session)
        user.delete_user_if_exists("test2")
        user_info = user.create_user("test2", "secret", "test2", "test2", "test2@alpinenow.com", "title", "dept")
        response = user.delete_user("test2")
        self.assertEqual(response.status_code, 200)
        # Verify the User is successfully deleted
        try:
            user.get_user_info("test2")
        except UserNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the User {0}".format("test2"))

    def test_update_user_info(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        user = User(chorus_session)
        user.delete_user_if_exists("test2")
        user_info = user.create_user("test2", "secret", "test2", "test2", "test2@alpinenow.com", "title", "dept")
        updated_user_info = user.update_user_info("test2","test2_new", "test2_new", "test2new@alpinenow.com",
                                  "title_new", "dept_new", "notes_new", "admin", "data_analyst")
        user_info_new = user.get_user_info("test2")
        user.delete_user("test2")
        self.assertNotEquals(user_info, user_info_new)
        self.assertEqual(updated_user_info, user_info_new)

    def test_get_user_id(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        user = User(chorus_session)
        user_id = user.get_user_id("chorusadmin")
        self.assertEqual(user_id, 1)

    def test_get_user_info(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        user = User(chorus_session)
        user_info = user.get_user_info("chorusadmin")
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['username'], "chorusadmin")

    def test_get_users_list(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        user = User(chorus_session)
        users_list1 = user.get_users_list(per_page=1)
        users_list2 = user.get_users_list(per_page=10)
        self.assertIsNotNone(users_list1)
        self.assertEqual(users_list1, users_list2)

