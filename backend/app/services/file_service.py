"""
File handling service for uploads and storage
"""
import os
import shutil
from typing import List, Optional
from fastapi import UploadFile
from app.config import settings
import aiofiles


async def save_uploaded_file(file: UploadFile, project_id: int, file_type: str) -> str:
    """
    Save an uploaded file to the project directory
    
    Args:
        file: Uploaded file
        project_id: Project ID
        file_type: Type of file (protein, clinical, assay)
    
    Returns:
        Relative file path
    """
    # Create project directory
    project_dir = os.path.join(settings.UPLOAD_DIR, "projects", str(project_id), file_type)
    os.makedirs(project_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
    filename = f"{file_type}_{len(os.listdir(project_dir))}{file_ext}"
    file_path = os.path.join(project_dir, filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Return relative path
    return os.path.join("projects", str(project_id), file_type, filename)


async def save_multiple_files(files: List[UploadFile], project_id: int, file_type: str) -> List[str]:
    """Save multiple uploaded files"""
    saved_paths = []
    for file in files:
        path = await save_uploaded_file(file, project_id, file_type)
        saved_paths.append(path)
    return saved_paths


def delete_project_files(project_id: int):
    """Delete all files for a project"""
    project_dir = os.path.join(settings.UPLOAD_DIR, "projects", str(project_id))
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)


def get_file_path(relative_path: str) -> str:
    """Get absolute file path from relative path"""
    return os.path.join(settings.UPLOAD_DIR, relative_path)


def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """Validate file type"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_types


ALLOWED_PROTEIN_EXTENSIONS = ['.pdb', '.fasta', '.fa']
ALLOWED_CLINICAL_EXTENSIONS = ['.csv', '.tsv']
ALLOWED_ASSAY_EXTENSIONS = ['.csv', '.tsv', '.xlsx']

