from fastapi import UploadFile
from pathlib import Path
import shutil
import uuid
from typing import Dict, Any
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_uploaded_file(self, file: UploadFile, claim_id: str) -> Dict[str, Any]:
        try:
            file_extension = Path(file.filename).suffix
            unique_filename = f"{claim_id}_{uuid.uuid4().hex[:8]}{file_extension}"
            
            file_path = self.upload_dir / unique_filename
            
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File saved: {file_path}")
            
            return {
                "success": True,
                "file_path": str(file_path),
                "filename": file.filename,
                "unique_filename": unique_filename,
                "file_url": f"/uploads/{unique_filename}"
            }
            
        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def save_multiple_files(self, files: list[UploadFile], claim_id: str) -> list[Dict[str, Any]]:
        results = []
        for file in files:
            result = await self.save_uploaded_file(file, claim_id)
            results.append(result)
        return results
    
    def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
        
        if file.content_type not in allowed_types:
            return {
                "valid": False,
                "error": f"File type {file.content_type} not allowed. Allowed: {allowed_types}"
            }
        
        return {"valid": True}


storage_service = StorageService()
