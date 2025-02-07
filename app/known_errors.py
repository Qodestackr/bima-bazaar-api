class KnownError(Exception):
    """
    Base exception for errors we anticipate and want to return clean error responses.
    """
    def __init__(self, message: str, status_code: int = 400, error_code: str = "known_error"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)
