import os
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.whatsapp_service import WhatsAppService
from app.exceptions.base import KnownError

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

@router.post("/send-policy/{policy_id}")
async def send_policy_document(policy_id: int, whatsapp_number: str, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to send a policy document to a customer via WhatsApp.
    
    Parameters:
        policy_id: The ID of the policy whose document is to be sent.
        whatsapp_number: The recipient's WhatsApp number (in international format).
    
    Workflow:
        - Reads a policy PDF from storage (simulated here as a dummy file).
        - Uses WhatsAppService to compress (if needed) and send the document.
    
    Returns:
        The JSON response from the WhatsApp API.
    
    Raises:
        HTTPException: If reading the PDF or sending the message fails.
    """
    # In a real application, retrieve the actual PDF associated with the policy.
    try:
        with open("dummy_policy.pdf", "rb") as f:
            pdf_bytes = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read policy PDF: {str(e)}")
    
    service = WhatsAppService()
    try:
        result = service.send_policy_document(whatsapp_number, pdf_bytes, policy_id)
        return result
    except KnownError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.post("/callback")
async def whatsapp_callback(request: Request):
    """
    Endpoint to handle WhatsApp Business API callbacks for delivery confirmation.
    
    This endpoint receives JSON payloads from WhatsApp that indicate the delivery
    status of sent messages. In a production system, these callbacks would be used
    to update the delivery status in the database.
    
    Returns:
        A simple JSON acknowledgment.
    """
    callback_data = await request.json()
    # Log or process the callback data as needed.
    logging.info("Received WhatsApp callback: %s", callback_data)
    return {"status": "received"}
