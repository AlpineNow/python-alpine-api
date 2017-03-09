"""
Exception classes - Subclassing to check for specific errors
"""


class AlpineException(Exception):
    """
    General Alpine Exception
    """
    def __init__(self, reason, *args):
        super(AlpineException, self).__init__(reason, *args)
        self.reason = reason

    def __repr__(self):
        return 'AlpineException: %s' % self.reason

    def __str__(self):
        return 'AlpineException: %s' % self.reason


class AlpineSessionNotFoundException(AlpineException):
    """

    """
    pass


class UserNotFoundException(AlpineException):
    """

    """
    pass


class DataSourceNotFoundException(AlpineException):
    """

    """
    pass


class DataSourceTypeNotFoundException(AlpineException):
    """

    """
    pass


class WorkspaceNotFoundException(AlpineException):
    """

    """
    pass


class WorkspaceMemberNotFoundException(AlpineException):
    """

    """
    pass


class WorkfileNotFoundException(AlpineException):
    """

    """
    pass


class JobNotFoundException(AlpineException):
    """

    """
    pass


class TaskNotFoundException(AlpineException):
    """

    """
    pass


class RunJobFailureException(AlpineException):
    """

    """
    pass


class LoginFailureException(AlpineException):
    """

    """
    pass


class RunFlowFailureException(AlpineException):
    """

    """
    pass


class RunFlowTimeoutException(AlpineException):
    """

    """
    pass


class StopFlowFailureException(AlpineException):
    """

    """
    pass


class ResultsNotFoundException(AlpineException):
    """

    """
    pass


class FlowResultsMalformedException(AlpineException):
    """

    """
    pass


class WorkflowVariableException(AlpineException):
    """

    """
    pass


class InvalidResponseCodeException(AlpineException):
    """

    """
    pass
