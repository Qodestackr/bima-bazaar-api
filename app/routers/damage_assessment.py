import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.damage import DamageAssessmentOut
from app.services.damage_assessment_service import DamageAssessmentService

router = APIRouter(prefix="/damage-assessment", tags=["damage-assessment"])

@router.post("/", response_model=DamageAssessmentOut)
async def assess_damage(file: UploadFile = File(...)):
    """
    Upload an image for damage assessment.
    Saves the image locally, then returns an estimated repair cost,
    recommendations, and a URL to the stored image.
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. JPEG or PNG required.")
    
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
    # Save file locally
    upload_dir = "uploads/damage_assessment"
    os.makedirs(upload_dir, exist_ok=True)
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    try:
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Process the image for damage assessment
    service = DamageAssessmentService()
    try:
        assessment_result = await service.assess_damage(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Construct the image URL (assuming static hosting for 'uploads')
    image_url = f"/static/damage_assessment/{unique_filename}"
    response_data = {
        **assessment_result,
        "image_url": image_url
    }
    return response_data
