class GitHubApiError(Exception):
    """
    Raised when an error occurs with the API
    """
    pass

class InvalidToken(GitHubApiError):
    """
    Raised when an invalid token is rejected by Github API
    """
    pass