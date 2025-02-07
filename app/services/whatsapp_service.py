import io
import logging
import os
import requests
from app.exceptions.base import KnownError

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    Service for integrating with the WhatsApp Business API to send policy documents.
    
    Features:
      - Compress PDF files for low-bandwidth delivery (simulation).
      - Send WhatsApp messages using a template that includes the policy PDF and quick link.
      - Raise a KnownError on failures to integrate seamlessly with global error handling.
    
    Environment Variables:
      WHATSAPP_API_ENDPOINT: The API endpoint for WhatsApp messages.
      WHATSAPP_API_TOKEN: Authentication token for WhatsApp API.
    """
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.WhatsAppService")
        self.api_endpoint = os.getenv("WHATSAPP_API_ENDPOINT", "https://api.whatsapp.com/v1/messages")
        self.api_token = os.getenv("WHATSAPP_API_TOKEN", "YOUR_WHATSAPP_API_TOKEN")
    
    def compress_pdf(self, pdf_bytes: bytes) -> bytes:
        """
        Compress a PDF file to reduce its size for low bandwidth conditions.
        
        This is a placeholder for actual compression logic. In a production system,
        integrate with a PDF compression library (e.g., PyPDF2 or pdfminer.six).
        
        Args:
            pdf_bytes: The original PDF file in bytes.
        
        Returns:
            The (simulated) compressed PDF file in bytes.
        """
        self.logger.info("Compressing PDF (simulation)")
        # Here we simply return the original bytes.
        return pdf_bytes
    
    def send_policy_document(self, whatsapp_number: str, pdf_bytes: bytes, policy_id: int) -> dict:
        """
        Send a policy document via the WhatsApp Business API.
        
        Steps:
          1. Compress the PDF.
          2. Generate a dummy URL for the PDF (in production, upload to a storage service).
          3. Construct a WhatsApp message payload that includes:
              - A document attachment (the PDF URL).
              - A quick link to view the policy details.
          4. Send the message via a POST request.
        
        Args:
            whatsapp_number: The recipient's WhatsApp number in international format.
            pdf_bytes: The policy PDF file in bytes.
            policy_id: The unique identifier for the policy (used for building links).
        
        Returns:
            A dictionary with the WhatsApp API's response.
        
        Raises:
            KnownError: If the API request fails.
        """
        # Compress the PDF file
        compressed_pdf = self.compress_pdf(pdf_bytes)
        
        # Simulate PDF hosting by generating a dummy URL
        pdf_url = f"https://bimabazaar.com/static/policies/{policy_id}.pdf"
        
        # Construct a quick link to view policy details
        policy_link = f"https://bimabazaar.com/policy/{policy_id}"
        
        # Build the WhatsApp message payload using a template
        payload = {
            "to": whatsapp_number,
            "type": "template",
            "template": {
                "namespace": "your_template_namespace",
                "name": "policy_document_delivery",
                "language": {"code": "en_US"},
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {"type": "document", "document": {"link": pdf_url}}
                        ]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": "Your policy document is attached."},
                            {"type": "text", "text": policy_link}
                        ]
                    }
                ]
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.api_endpoint, json=payload, headers=headers)
            response.raise_for_status()
            self.logger.info("WhatsApp message sent successfully", extra={"to": whatsapp_number})
            return response.json()
        except Exception as e:
            self.logger.error("Failed to send WhatsApp message: %s", str(e), exc_info=True)
            raise KnownError(
                message="Failed to send WhatsApp message",
                status_code=500,
                error_code="WHATSAPP_SEND_ERROR",
                details={"whatsapp_number": whatsapp_number}
            ) from e
