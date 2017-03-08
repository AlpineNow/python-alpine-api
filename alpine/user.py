import json
from .alpineobject import AlpineObject
from .exception import *


class User(AlpineObject):
    """
    A class for interacting with user accounts.
    """

    @property
    def applicationRole(self):
        return self.ApplicationRole()

    @property
    def adminRole(self):
        return self.AdminRole()

    def __init__(self, base_url, session, token):
        super(User, self).__init__(base_url, session, token)

    def create(self, username, password, first_name, last_name, email, title=None, dept=None,
               notes=None, admin_role=None, app_role=None, email_notification=False):
        """
        Create a user account with the specified parameters.

        :param str username: A unique name.
        :param str password: Password of the user being created.
        :param str first_name: First Name of the user being created.
        :param str last_name: Last Name of the user being created.
        :param str email: Email of the user being created.
        :param str title: User Title of the user being created.
        :param str dept: Department of the user being created.
        :param str notes: Note for the user being created.
        :param str admin_role: Administration role. Ref to User.AdminRole. By default user is not a Admin
        :param str app_role: Application role. Ref to User.ApplicationRole.
                             The default application role is User.ApplicationRole.BusinessUser
        :param bool email_notification: Option to subscribe to email notifications.

        :return: Created user information or error message.
        :rtype: dict

        Example::

            >>> user_info = session.create(username = 'demo_user', password = 'temp_password',
            >>>                            first_name = 'Demo', last_name = 'User',
            >>>                            email = 'demouser@alpinenow.com', title = 'Data Scientist',
            >>>                            dept = 'Product')

        """
        # Get correct values for admin and roles for url call:
        if admin_role is None:
            admin_role == self.adminRole.NonAdmin
            admin = False
        elif admin_role == self.adminRole.ApplicationAdministrator:
            admin = True
        else:
            admin = False
        if app_role is None:
            app_role = User.ApplicationRole.BusinessUser

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
                   "roles": admin_role,
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

    def delete(self, user_id):
        """
        Attempts to delete the given user. Will fail if the user does not exist.

        :param int user_id: ID number of user account to be deleted.
        :return: None
        :rtype: NoneType
        :exception UserNotFoundException: The username does not exist.

        Example::

            >>> session.user.delete(user_id = 51)
        """

        try:
            self.get(user_id)
            url = "{0}/users/{1}".format(self.base_url, user_id)
            url = self._add_token_to_url(url)
            self.session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
            self.logger.debug("Deleting User with id {0}".format(user_id))
            response = self.session.delete(url)
            self.logger.debug("Received response code {0} with reason {1}"
                              .format(response.status_code, response.reason))
            if response.status_code == 200:
                self.logger.debug("User successfully deleted.")
            else:
                raise InvalidResponseCodeException("Response Code Invalid, the expected Response Code is {0}, "
                                                   "the actual Response Code is {1}".format(200, response.status_code))
            return None
        except UserNotFoundException as err:
            self.logger.debug("User not found, error {0}".format(err))

    def update(self, user_id, first_name=None, last_name=None, email=None, title=None,
               dept=None, notes=None, admin_role=None, app_role=None, email_notification=None):
        """
        Only included fields will be updated.

        :param str user_id: ID number of the user to update.
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
        :exception UserNotFoundException: The username does not exist.

        Example::

            >>> updated_info = session.user.update(user_id = 51, title = "Senior Data Scientist")

        """

        url = "{0}/users/{1}".format(self.base_url, user_id)
        url = self._add_token_to_url(url)
        payload = self.get(user_id)

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

    def get_id(self, username):
        """
        Gets the ID number of the user. Will throw an exception if the user does not exist.

        :param str username: Unique user name
        :return: ID number of the user
        :rtype: int
        :exception UserNotFoundException: The username does not exist.

        Example

            >>> user_id = session.user.get_id(username = 'demo_user')
            >>> print(user_id)
            51

        """

        users_list = self.get_list()
        for user_info in users_list:
            if user_info['username'] == username:
                return user_info['id']
        # return None
        raise UserNotFoundException("User {0} not found".format(username))

    def get(self, user_id):
        """
        Get one user's metadata.

        :param str user_id: A unique user ID number.
        :return: Single user's metadata.
        :rtype: dict
        :exception UserNotFoundException: The User does not exist.

        Example::

            >>> session.user.get(user_id = 51)
        """
        url = "{0}/users/{1}".format(self.base_url, user_id)
        url = self._add_token_to_url(url)

        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")

        r = self.session.get(url, verify=False)
        user_response = r.json()

        try:
            if user_response['response']:
                self.logger.debug("Found user id: <{0}>".format(user_id))
                return user_response['response']
            else:
                raise UserNotFoundException("User id: <{0}> not found".format(user_id))
        except Exception as err:
            raise UserNotFoundException("User id: <{0}> not found".format(user_id))

    def get_list(self, per_page=100):
        """
        Get a list of all users' metadata.

        :param int per_page: How many users to return in each page.
        :return: A list of all the users' data.
        :rtype: list of dict

        Example::

            >>> all_users = session.user.get_list()
            >>> len(all_users)
            99

        """
        url = "{0}/users".format(self.base_url)
        url = self._add_token_to_url(url)
        page_current = 0
        users_list = None
        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")
        while True:
            payload = {"per_page": per_page, "page": page_current + 1}
            user_list_response = self.session.get(url, params=payload, verify=False).json()
            # user_list_response = self.session.get(url, data=json.dumps(payload), verify=False).json()
            page_total = user_list_response['pagination']['total']
            page_current = user_list_response['pagination']['page']
            if users_list:
                users_list.extend(user_list_response['response'])
            else:
                users_list = user_list_response['response']
            if page_total == page_current:
                break
        return users_list

    class ApplicationRole(object):
        """
        Convenience strings for user application roles.
        """
        AnalyticsDeveloper = "analytics_developer"
        DataAnalyst = "data_analyst"
        Collaborator = "collaborator"
        BusinessUser = "business_user"

    class AdminRole(object):
        """
        Convenience strings for user Administrator roles.
        """
        ApplicationAdministrator = "admin"
        DataAdministrator = "data_admin"
        NonAdmin = ""
