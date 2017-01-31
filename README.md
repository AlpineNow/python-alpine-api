# python-alpine-api
Python SDK for Chorus

Internal notes for contributors:

Doc style guide:
d
def get_user_data(self, user_name):
~~~ddd
    """
    Get one user's metadata

    :param str user_name: A Unique user name.
    :return: Single user's data
    :rtype: dict
    :exception UserNotFoundException: The user_name does not exist.
    """
~~~
ddddd

