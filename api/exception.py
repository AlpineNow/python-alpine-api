"""
Exception classes - Subclassing to check for specific errors
"""

class ChorusException(Exception):
    """
    General Chorus Exception
    """
    def __init__(self, reason, *args):
        super(ChorusException, self).__init__(reason, *args)
        self.reason = reason

    def __repr__(self):
        return 'ChorusException: %s' % self.reason

    def __str__(self):
        return 'ChorusException: %s' % self.reason


class ChorusSessionNotFoundException(ChorusException):
    """

        """
    pass


class UserNotFoundException(ChorusException):
    """

    """
    pass


class DataSourceNotFoundException(ChorusException):
    """

    """
    pass

class WorkspaceNotFoundException(ChorusException):
    """

    """
    pass


class WorkfileNotFoundException(ChorusException):
    """

    """
    pass


class JobNotFoundException(ChorusException):
    """

    """
    pass


class TaskNotFoundException(ChorusException):
    """

    """
    pass


class LoginFailureException(ChorusException):
    """

    """
    pass


class RunFlowFailureException(ChorusException):
    """

    """
    pass


class RunFlowTimeoutException(ChorusException):
    """

    """
    pass


class StopFlowFailureException(ChorusException):
    """

    """
    pass