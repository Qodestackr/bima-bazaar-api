from typing import Optional, Dict, Any
from app.exceptions.base import KnownError

class UserNotFoundError(KnownError):
    def __init__(self, user_id: Optional[str] = None):
        message = f"User with id '{user_id}' not found." if user_id else "User not found."
        super().__init__(
            message=message,
            status_code=404,
            error_code="USER_NOT_FOUND",
            details={"user_id": user_id} if user_id else {}
        )

class UserEmailAlreadyExistsError(KnownError):
    def __init__(self, email: str, message: str = None):
        if not message:
            message = f"User email '{email}' already exists."
        super().__init__(
            message=message,
            status_code=422,
            error_code="USER_EMAIL_ALREADY_EXISTS",
            details={"email": email}
        )

class UserAuthenticationError(KnownError):
    def __init__(self, message: str = None, details: Optional[Dict[str, Any]] = None):
        if not message:
            message = "User authentication failed."
        super().__init__(
            message=message,
            status_code=401,
            error_code="USER_AUTHENTICATION_ERROR",
            details=details
        )
