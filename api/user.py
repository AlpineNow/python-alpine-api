import json
from api import *
from api.exception import *
from api.alpineobject import AlpineObject


class User(AlpineObject):
    """
    A collection of functions to create, delete, query and update user accounts.
    """

    def __init__(self, base_url, session, token):
        super(User, self).__init__(base_url, session, token)

    def create_user(self, username, password, first_name, last_name, email, title="", dept="",
                    notes="Add Via API", admin_role="", app_role="analytics_developer", email_notification=False):
        # TODO: How to handle LDAP for password?
        """
        Create a user account with specified parameters.

        :param str username: A unique name.
        :param str password: Password of the user being created.
        :param str first_name: First Name of the user being created.
        :param str last_name: Last Name of the user being created.
        :param str email: Email of the user being created.
        :param str title: User Title of the user being created.
        :param str dept: Department of the user being created.
        :param str notes: Note for the user being created.
        :param str admin_role: Administration role. One of app_admin, data_admin or an empty string.
        :param str app_role: Application role. One of analytics_developer, data_analyst, \
                                collaborator or business_user.
        :param bool email_notification: Option to subscribe to email notifications.

        :return: Created user information or error message.
        :rtype: dict
        """
        # Get correct values for admin and roles for url call:
        admin = False
        roles = ""
        if admin_role == "app_admin":
            admin = True
        elif admin_role == "data_admin":
            roles = "data_admin"

        self.session.headers.update({"Content-Type": "application/json"})  # Set special header for this post
        url = "{0}/users".format(self.base_url)
        url = self._add_token_to_url(url)
        payload = {"username": username,
                   "password": password,
                   "first_name": first_name,
                   "last_name": last_name,
                   "email": email,
                   "title": title,
                   "notes": notes,
                   "dept": dept,
                   "admin": admin,
                   "roles": roles,
                   "user_type": app_role,
                   "subscribed_to_emails": email_notification
                   }
        response = self.session.post(url, data=json.dumps(payload), verify=False)
        self.logger.debug("Adding user, received response code {0} with reason {1}...".format(
            response.status_code, response.reason))
        # self.session.headers.pop("Content-Type")  # Remove header, as it affects other functions

        try:
            return response.json()['response']
        except KeyError:
            return response.json()

    def delete_user(self, user_name):
        """
        Attempts to delete the given user. Will fail if the user does not exist.

        :param str user_name: Username of account to be deleted.
        :return: None
        :rtype: NoneType
        :exception UserNotFoundException: The user_name does not exist.
        """

        try:
            pass
        except UserNotFoundException:
            self.logger.debug("User not found")
            return UserNotFoundException
        else:
            user_id = self.get_user_id(user_name)
            url = "{0}/users/{1}".format(self.base_url, user_id)
            url = self._add_token_to_url(url)
            self.session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
            self.logger.debug("Deleting User {0} with id {1}".format(user_name, user_id))
            response = self.session.delete(url)
            self.logger.debug("Received response code {0} with reason {1}"
                              .format(response.status_code, response.reason))
            print("User successfully deleted.")
            return None

    def update_user(self, user_name, first_name=None, last_name=None, email=None, title=None,
                         dept=None, notes=None, admin_role=None, app_role=None, email_notification=None):
        # TODO: Error checking!

        """
        Only included fields will be updated.

        :param str user_name: A unique username.
        :param str first_name: New first name of the user.
        :param str last_name: New last name of the user.
        :param str email: New email of the user.
        :param str title: New title of the user.
        :param str dept: New department of the user.
        :param str notes: New notes for the user.
        :param str admin_role: New Administration Role. One of app_admin, data_admin or an empty string
        :param str app_role: New Application Role. One of analytics_developer, data_analyst, \
                                collaborator or business_user.
        :param bool email_notification: Change option to subscribe to email notifications.

        :return: Updated user information.
        :rtype: dict
        :exception UserNotFoundException: The user_name does not exist.
        """

        user_id = self.get_user_id(user_name)
        # if user_id is None: # IS this necessary?
        #     raise UserNotFoundException("User {0} was not found".format(user_name))
        url = "{0}/users/{1}".format(self.base_url, user_id)
        url = self._add_token_to_url(url)
        payload = self.get_user_data(user_name)

        # get rid of fields that aren't required for PUT
        pop_fields = ['complete_json',
                      'entity_type',
                      'id',
                      'image',
                      'is_deleted',
                      'tags',
                      'username']
        for field in pop_fields:
            payload.pop(field)

        # replace fields with updated ones from kwargs
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if email:
            payload["email"] = email
        if title:
            payload["title"] = title
        if dept:
            payload["dept"] = dept
        if notes:
            payload["notes"] = notes
        if app_role:
            payload["user_type"] = app_role
        if email_notification is not None:
            payload["subscribed_to_emails"] = email_notification

        # Logic for setting admin status is slightly more complicated:
        if admin_role is None:
            pass
        elif admin_role == "app_admin":
            payload["admin"] = True
            payload["roles"] = ""
        elif admin_role == "data_admin":
            payload["admin"] = False
            payload["roles"] = "data_admin"
        else:
            payload["admin"] = False
            payload["roles"] = ""

        self.logger.debug("Updating the user information {0} to {1}".format(json.dumps(payload), url))
        self.session.headers.update({"Content-Type": "application/json"})  # Set special header for this post
        response = self.session.put(url, data=json.dumps(payload), verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        self.session.headers.pop("Content-Type")  # Remove header, as it affects other tests
        return response.json()['response']

    def get_user_id(self, user_name):
        """
        Gets the ID number of the user. Will throw an exception if the user does not exist.

        :param str user_name: Unique user name
        :return: ID number of the user
        :rtype: int
        :exception UserNotFoundException: The user_name does not exist.
        """

        try:
            user_info = self.get_user_data(user_name)
        except UserNotFoundException as err:
            self.logger.error(err)
            raise
        else:
            return int(user_info['id'])

    def get_user_data(self, user_name):
        """
        Get one user's metadata

        :param str user_name: A Unique user name.
        :return: Single user's data
        :rtype: dict
        :exception UserNotFoundException: The user_name does not exist.
        """
        users_list = self.get_all_users_data()
        for user_info in users_list:
            if user_info['username'] == user_name:
                return user_info
        raise UserNotFoundException("User {0} not found".format(user_name))

    def get_all_users_data(self, per_page=100):
        """
        Get a list of all users' metadata.

        :param int per_page: How many users to return in each page.
        :return: A list of all user's data (up to per_page).
        :rtype: list of dict
        """
        # TODO: what if there is more than 100 users
        url = "{0}/users".format(self.base_url)
        url = self._add_token_to_url(url)
        page_current = 0
        users_list = None
        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")
        while True:
            payload = {"per_page": per_page, "page": page_current + 1}
            user_list_response = self.session.get(url, data=json.dumps(payload), verify=False).json()
            page_total = user_list_response['pagination']['total']
            page_current = user_list_response['pagination']['page']
            if users_list:
                users_list.extend(user_list_response['response'])
            else:
                users_list = user_list_response['response']
            if page_total == page_current:
                break
        return users_list
