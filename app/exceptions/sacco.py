from typing import Optional, Dict, Any
from app.exceptions.base import KnownError

class SaccoNotFoundError(KnownError):
    def __init__(self, sacco_name: Optional[str] = None):
        message = f"SACCO '{sacco_name}' not found." if sacco_name else "SACCO not found."
        super().__init__(
            message=message,
            status_code=404,
            error_code="SACCO_NOT_FOUND",
            details={"sacco_name": sacco_name} if sacco_name else {}
        )

class DuplicateSaccoError(KnownError):
    def __init__(self, sacco_name: str, message: str = None):
        if not message:
            message = f"SACCO '{sacco_name}' already exists."
        super().__init__(
            message=message,
            status_code=422,
            error_code="DUPLICATE_SACCO",
            details={"sacco_name": sacco_name}
        )
