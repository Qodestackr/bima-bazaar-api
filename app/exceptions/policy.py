from typing import Optional, Dict, Any
from app.exceptions.base import KnownError

class PolicyNotFoundException(KnownError):
    def __init__(self, policy_id: Optional[int] = None):
        message = f"Policy with id {policy_id} not found" if policy_id else "Policy not found"
        super().__init__(
            message=message,
            status_code=404,
            error_code="POLICY_NOT_FOUND",
            details={"policy_id": policy_id} if policy_id else {}
        )

class PolicyValidationError(KnownError):
    def __init__(self, message: str, validation_errors: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="POLICY_VALIDATION_ERROR",
            details={"validation_errors": validation_errors} if validation_errors else {}
        )

class DatabaseOperationError(KnownError):
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_OPERATION_ERROR",
            details={"operation": operation} if operation else {}
        )

class PolicyBusinessRuleError(KnownError):
    def __init__(self, message: str, rule_name: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BUSINESS_RULE_VIOLATION",
            details={"rule_name": rule_name} if rule_name else {}
        )

class PremiumCalculationError(KnownError):
    def __init__(self, message: str, calculation_details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="PREMIUM_CALCULATION_ERROR",
            details={"calculation_details": calculation_details} if calculation_details else {}
        )
