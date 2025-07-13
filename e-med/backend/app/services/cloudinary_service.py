import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import HTTPException, status
from typing import Optional
import os
from datetime import datetime

class CloudinaryService:
    def __init__(self):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET")
        )
    
    async def upload_prescription(self, file_data: bytes, filename: str, user_id: int) -> dict:
        """Upload prescription file to Cloudinary"""
        try:
            # Create unique folder for prescriptions
            folder = f"medidash/prescriptions/user_{user_id}"
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file_data,
                public_id=f"{folder}/{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                resource_type="auto",
                folder=folder,
                use_filename=True,
                unique_filename=True,
                overwrite=False,
                tags=["prescription", f"user_{user_id}"]
            )
            
            return {
                "url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "file_size": result.get("bytes"),
                "format": result.get("format"),
                "width": result.get("width"),
                "height": result.get("height")
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    async def delete_prescription(self, public_id: str) -> bool:
        """Delete prescription file from Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    async def get_prescription_url(self, public_id: str) -> Optional[str]:
        """Get prescription URL from Cloudinary"""
        try:
            result = cloudinary.api.resource(public_id)
            return result.get("secure_url")
        except Exception:
            return None

# Create global instance
cloudinary_service = CloudinaryService() 