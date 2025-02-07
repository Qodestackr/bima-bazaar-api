from typing import Optional, Dict, Any

class KnownError(Exception):
    """
    Base exception for all known errors in the application.
    
    Attributes:
        message: A human-readable error message.
        status_code: The HTTP status code to return.
        error_code: A unique code identifying the error type.
        details: An optional dict providing additional context.
    """
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "error",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the error."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }
