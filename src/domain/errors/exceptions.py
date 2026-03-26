class UserLockedError(Exception): 
    """
    User is locked error (4xx status codes).

    Raised when the client made a mistake (bad request, not found, etc.)
    """
    pass 

class InvalidEmailOrPasswordError(Exception): 
    """
    Invalid email or password error (4xx status codes).

    Raised when the client made a mistake (bad request, not found, etc.)
    """
    pass

class ConcurrentModificationError(Exception): 
    """
    Concurrent modification error (4xx status codes).

    Raised when the client made a mistake (bad request, not found, etc.)
    """
    pass 

class InvalidProfileDataError(Exception):
    """
    Invalid profile data error (4xx status codes).

    Raised when the client made a mistake (bad request, not found, etc.)
    """
    pass