from typing import Optional, Dict, Any
from app.exceptions.base import KnownError

class WhatsAppIntegrationError(KnownError):
    def __init__(self, message: str = None, details: Optional[Dict[str, Any]] = None):
        if not message:
            message = "An error occurred during WhatsApp integration."
        super().__init__(
            message=message,
            status_code=500,
            error_code="WHATSAPP_INTEGRATION_ERROR",
            details=details
        )

class AIProcessingError(KnownError):
    def __init__(self, message: str = None, details: Optional[Dict[str, Any]] = None):
        if not message:
            message = "AI processing failed."
        super().__init__(
            message=message,
            status_code=500,
            error_code="AI_PROCESSING_ERROR",
            details=details
        )

class SMSIntegrationError(KnownError):
    def __init__(self, message: str = None, details: Optional[Dict[str, Any]] = None):
        if not message:
            message = "SMS integration failed."
        super().__init__(
            message=message,
            status_code=500,
            error_code="SMS_INTEGRATION_ERROR",
            details=details
        )
