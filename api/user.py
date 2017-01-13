import json

from api.exception import *
from chorus import ChorusObject


class User(ChorusObject):

    def __init__(self, chorus_session=None):
        super(User, self).__init__()
        if chorus_session:
            self.base_url = chorus_session.base_url
            self.session = chorus_session.session
            self.token = chorus_session.token
        else:
            raise ChorusSessionNotFoundException()

    def create_user(self, username, password, first_name, last_name, email, title, dept,
                    notes ="Add Via API", admin="admin", user_type="analytics_developer"):
        """

        :param username:
        :param password:
        :param first_name:
        :param last_name:
        :param email:
        :param title:
        :param dept:
        :param notes:
        :param admin:
        :param user_type:
        :return:
        """
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
                   "user_type": user_type,
                   }
        response = self.session.post(url, data=json.dumps(payload), verify=False)
        self.logger.debug("Adding user, received response code {0} with reason {1}...".format(
            response.status_code, response.reason))
        #self.session.headers.pop("Content-Type")  # Remove header, as it affects other functions
        return response.json()['response']

    def delete_user(self, user_name):
        """

        :param user_name:
        :return:
        """
        user_id = self.get_user_id(user_name)
        url = "{0}/users/{1}".format(self.base_url, user_id)
        url = self._add_token_to_url(url)
        self.session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        self.logger.debug("Deleting User {0} with id {1}".format(user_name, user_id))
        response = self.session.delete(url)
        self.logger.debug("Received response code {0} with reason {1}".format(response.status_code, response.reason))
        return response

    def delete_user_if_exists(self, user_name):
        """

        :param user_name:
        :return:
        """
        try:
            self.delete_user(user_name)
        except UserNotFoundException:
            self.logger.debug ("User not found, so we don't need to delete the user")

    def update_user_info(self, user_name, first_name=None, last_name=None, email=None,
                         title=None, dept=None, notes=None, admin=None, user_type=None):
        """

        :param user_name:
        :param first_name:
        :param last_name:
        :param email:
        :param title:
        :param dept:
        :param notes:
        :param admin:
        :param user_type:
        :return:
        """
        user_id = self.get_user_id(user_name)
        if user_id is None:
            raise UserNotFoundException("User {0} was not found".format(user_name))
        url = "{0}/users/{1}".format(self.base_url,user_id)
        url = self._add_token_to_url(url)
        payload = self.get_user_info(user_name)

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
            payload["first_name"]= first_name
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

        :param user_name:
        :return:
        """
        user = self.get_user_info(user_name)
        if user:
                return int(user['id'])

    def get_user_info(self, user_name):
        """

        :param user_name:
        :return:
        """
        users_list = self.get_users_list()
        for user in users_list:
            if user['username'] == user_name:
                return user
        raise UserNotFoundException("User {0} does Not Found".format(user_name))

    def get_users_list(self, per_page=100):
        """

        :param per_page:
        :return:
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
                break;
        return users_list
