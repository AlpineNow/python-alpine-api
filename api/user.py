import json
from api import *
from api.exception import *
from api.alpineobject import AlpineObject


class User(AlpineObject):
    """
    A collection of functions to deal with user accounts.

    """
    def __init__(self, base_url, session, token):
        super(User, self).__init__(base_url, session, token)

    def create_user(self, username, password, first_name, last_name, email, title="", dept="",
                    notes="Add Via API", admin_role="", app_role="analytics_developer", emails = False):
        # TODO: What happens when we have incompatible roles?
        # TODO: How to handle LDAP for password?

        """
        Create a user account with specified parameters.

        :param string username: A unique name.
        :param string password: Password of the user being created.
        :param string first_name: First Name of the user being created.
        :param string last_name: Last Name of the user being created.
        :param string email: Email of the user being created.
        :param string title: User Title of the user being created.
        :param string dept: Department of the user being created.
        :param string notes: Note for the user being created.
        :param string admin_role: Administration role. One of app_admin, data_admin or an empty string.
        :param string app_role: Application role. One of analytics_developer, data_analyst, collaborator or business_user.
        :param bool emails: Option of subscribe to emails.

        :return: API response
        :rtype: dict
        """

        # Get correct settings for admin and roles for url call:
        admin = False
        roles = ""
        if admin_role == "app_admin":
            admin = True
        elif admin_role == "data_admin":
            roles  = "data_admin"

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
                   "subscribed_to_emails": emails
                   }
        response = self.session.post(url, data=json.dumps(payload), verify=False)
        self.logger.debug("Adding user, received response code {0} with reason {1}...".format(
            response.status_code, response.reason))
        # self.session.headers.pop("Content-Type")  # Remove header, as it affects other functions
        return response.json()

    def delete_user(self, user_name):
        """
        Delete the user with no error checking.

        :param user_name: (string, required) Username of account to be deleted
        :return: Response of the delete action.
        """

        # Deal with statuses: 200 = success, 403 = not admin, 404 = not found

        user_id = self.get_user_id(user_name)
        url = "{0}/users/{1}".format(self.base_url, user_id)
        url = self._add_token_to_url(url)
        self.session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        self.logger.debug("Deleting User {0} with id {1}".format(user_name, user_id))
        response = self.session.delete(url)
        self.logger.debug("Received response code {0} with reason {1}".format(response.status_code, response.reason))
        return response

    def delete_user_if_exists(self, user_name):
        # TODO: Does this require admin?
        """
        Delete the User if the user exists or skip without throwing any error if user doesn't exists

        :param user_name: Username of the user to be deleted

        :return: Response of the delete action.

        """
        try:
            return self.delete_user(user_name)
        except UserNotFoundException:
            self.logger.debug("User not found, so we don't need to delete the user")

    def update_user_data(self, user_name, first_name=None, last_name=None, email=None,
                         title=None, dept=None, notes=None, admin=None, user_type=None):
        """
        Updating for user information

        :param user_name: Username of the user to be updated
        :param first_name: Updated First Name of the user
        :param last_name: Updated Last Name of the user
        :param email: Updated Email of the user
        :param title: Updated Title of the user
        :param dept: Updated Department of the user
        :param notes: Updated Notes of the user
        :param admin: Updated Admin of the user
        :param user_type: Updated User Type of the user

        :return: Information of the updated user
        :rtype: dict
        """
        user_id = self.get_user_id(user_name)
        if user_id is None:
            raise UserNotFoundException("User {0} was not found".format(user_name))
        url = "{0}/users/{1}".format(self.base_url, user_id)
        url = self._add_token_to_url(url)
        payload = self.get_user_data(user_name)

        # get rid of fields that aren't required for PUT
        pop_fields = ['complete_json',
                      'entity_type',
                      'id',
                      'image',
                      'is_deleted',
                      'subscribed_to_emails',
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
        if admin:
            payload["admin"] = admin
        if user_type:
            payload["user_type"] = user_type

        self.logger.debug("Updating the user information {0} to {1}".format(json.dumps(payload), url))
        self.session.headers.update({"Content-Type": "application/json"})  # Set special header for this post
        response = self.session.put(url, data=json.dumps(payload), verify=False)
        self.logger.debug("Received response code {0} with reason {1}...".format(response.status_code, response.reason))
        self.session.headers.pop("Content-Type")  # Remove header, as it affects other tests
        return response.json()['response']

    def get_user_id(self, user_name):
        """
        Gets the ID number of the user.

        :param string user_name: User name of the user to query on
        :return: ID number  of the user
        :rtype: int
        """
        user_info = self.get_user_data(user_name)
        if user_info:
                return int(user_info['id'])

    def get_user_data(self, user_name):
        """
        Get one user's metadata

        :param string user_name: The unique user name
        :return: User data
        :rtype: dict
        """
        users_list = self.get_users_list()
        for user_info in users_list:
            if user_info['username'] == user_name:
                return user_info
        raise UserNotFoundException("User {0} Not Found".format(user_name))

    def get_users_data_list(self, per_page=100):
        """
        Get a list of all users' metadata.

        :param int per_page: How many users to return in each page
        :return: A list of user data
        :rtype: list of dict
        """
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
