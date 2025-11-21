"""
Project API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectListResponse
from app.core.dependencies import get_user_or_create_default
from app.services.file_service import save_multiple_files, delete_project_files, validate_file_type, ALLOWED_PROTEIN_EXTENSIONS, ALLOWED_CLINICAL_EXTENSIONS, ALLOWED_ASSAY_EXTENSIONS
from app.services.processing_service import ProcessingService
from fastapi.background import BackgroundTasks
import json

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    country: Optional[str] = Form(None),
    region: Optional[str] = Form(None),
    collection_timestamp: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
    clinical_severity: Optional[str] = Form(None),
    clinical_notes: Optional[str] = Form(None),
    protein_files: Optional[List[UploadFile]] = File(None),
    clinical_files: Optional[List[UploadFile]] = File(None),
    assay_files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    """Create a new project with file uploads - NO AUTH REQUIRED"""
    from datetime import datetime
    
    # Get or create default user
    current_user = get_user_or_create_default(db)
    
    # Parse collection_timestamp if provided
    parsed_timestamp = None
    if collection_timestamp:
        try:
            # Try parsing ISO format
            parsed_timestamp = datetime.fromisoformat(collection_timestamp.replace('Z', '+00:00'))
        except:
            try:
                # Try parsing common formats
                for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                    try:
                        parsed_timestamp = datetime.strptime(collection_timestamp, fmt)
                        break
                    except:
                        continue
            except:
                parsed_timestamp = None
    
    try:
        # Create project
        project = Project(
            user_id=current_user.id,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            country=country,
            region=region,
            collection_timestamp=parsed_timestamp,
            symptoms=symptoms,
            clinical_severity=clinical_severity,
            clinical_notes=clinical_notes,
            status="Pending"
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
    except Exception as e:
        db.rollback()
        print(f"Error creating project: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )
    
    # Save uploaded files (if any)
    saved_protein_files = []
    saved_clinical_files = []
    saved_assay_files = []
    
    try:
        if protein_files:
            for file in protein_files:
                if file and file.filename:
                    if not validate_file_type(file.filename, ALLOWED_PROTEIN_EXTENSIONS):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid file type for protein file: {file.filename}"
                        )
                    path = await save_multiple_files([file], project.id, "protein")
                    saved_protein_files.extend(path)
        
        if clinical_files:
            for file in clinical_files:
                if file and file.filename:
                    if not validate_file_type(file.filename, ALLOWED_CLINICAL_EXTENSIONS):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid file type for clinical file: {file.filename}"
                        )
                    path = await save_multiple_files([file], project.id, "clinical")
                    saved_clinical_files.extend(path)
        
        if assay_files:
            for file in assay_files:
                if file and file.filename:
                    if not validate_file_type(file.filename, ALLOWED_ASSAY_EXTENSIONS):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid file type for assay file: {file.filename}"
                        )
                    path = await save_multiple_files([file], project.id, "assay")
                    saved_assay_files.extend(path)
    except HTTPException:
        raise
    except Exception as e:
        # Log error but don't fail project creation if file handling fails
        print(f"Warning: File handling error: {e}")
    
    # Update project with file paths
    project.set_protein_files(saved_protein_files)
    project.set_clinical_files(saved_clinical_files)
    project.set_assay_files(saved_assay_files)
    db.commit()
    
    # Start background processing
    background_tasks.add_task(process_project_background, project.id)
    
    # Parse file fields from JSON strings before validation
    import json
    project_dict = {
        "id": project.id,
        "user_id": project.user_id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "latitude": float(project.latitude) if project.latitude else None,
        "longitude": float(project.longitude) if project.longitude else None,
        "country": project.country,
        "region": project.region,
        "collection_timestamp": project.collection_timestamp,
        "symptoms": project.symptoms,
        "clinical_severity": project.clinical_severity,
        "clinical_notes": project.clinical_notes,
        "protein_files": json.loads(project.protein_files) if project.protein_files else [],
        "clinical_files": json.loads(project.clinical_files) if project.clinical_files else [],
        "assay_files": json.loads(project.assay_files) if project.assay_files else [],
        "mutations_count": project.mutations_count,
        "drugs_count": project.drugs_count,
        "modifications_count": project.modifications_count,
        "deadliness_score": float(project.deadliness_score) if project.deadliness_score else None,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }
    project_response = ProjectResponse.model_validate(project_dict)
    return project_response


def process_project_background(project_id: int):
    """Background task to process project - ALWAYS uses REAL ML MODULES"""
    from app.database import SessionLocal
    import time
    db = SessionLocal()
    try:
        processing_service = ProcessingService(db)
        # Always uses real ML modules (fast_mode removed)
        print(f"[Processing] Starting REAL ML processing for project {project_id}...")
        processing_service.process_project(project_id)
        print(f"[Processing] Project {project_id} processed successfully with REAL ML modules")
    except Exception as e:
        print(f"[Processing] Background processing error: {e}")
        import traceback
        traceback.print_exc()
        # Update project status to Failed
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = "Failed"
            db.commit()
    finally:
        db.close()


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """List all projects - NO AUTH REQUIRED"""
    import json
    skip = (page - 1) * page_size
    
    # Query all projects (no user filter)
    query = db.query(Project)
    total = query.count()
    projects = query.order_by(Project.created_at.desc()).offset(skip).limit(page_size).all()
    
    # Parse file fields from JSON strings before validation
    project_items = []
    for p in projects:
        project_dict = {
            "id": p.id,
            "user_id": p.user_id,
            "title": p.title,
            "description": p.description,
            "status": p.status,
            "latitude": float(p.latitude) if p.latitude else None,
            "longitude": float(p.longitude) if p.longitude else None,
            "country": p.country,
            "region": p.region,
            "collection_timestamp": p.collection_timestamp,
            "symptoms": p.symptoms,
            "clinical_severity": p.clinical_severity,
            "clinical_notes": p.clinical_notes,
            "protein_files": json.loads(p.protein_files) if p.protein_files else [],
            "clinical_files": json.loads(p.clinical_files) if p.clinical_files else [],
            "assay_files": json.loads(p.assay_files) if p.assay_files else [],
            "mutations_count": p.mutations_count,
            "drugs_count": p.drugs_count,
            "modifications_count": p.modifications_count,
            "deadliness_score": float(p.deadliness_score) if p.deadliness_score else None,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }
        project_items.append(ProjectResponse.model_validate(project_dict))
    
    return ProjectListResponse(
        items=project_items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get project by ID - NO AUTH REQUIRED"""
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Parse file fields from JSON strings before validation
    import json
    project_dict = {
        "id": project.id,
        "user_id": project.user_id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "latitude": float(project.latitude) if project.latitude else None,
        "longitude": float(project.longitude) if project.longitude else None,
        "country": project.country,
        "region": project.region,
        "collection_timestamp": project.collection_timestamp,
        "symptoms": project.symptoms,
        "clinical_severity": project.clinical_severity,
        "clinical_notes": project.clinical_notes,
        "protein_files": json.loads(project.protein_files) if project.protein_files else [],
        "clinical_files": json.loads(project.clinical_files) if project.clinical_files else [],
        "assay_files": json.loads(project.assay_files) if project.assay_files else [],
        "mutations_count": project.mutations_count,
        "drugs_count": project.drugs_count,
        "modifications_count": project.modifications_count,
        "deadliness_score": float(project.deadliness_score) if project.deadliness_score else None,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }
    project_response = ProjectResponse.model_validate(project_dict)
    return project_response


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update project - NO AUTH REQUIRED"""
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update fields
    for field, value in update.dict(exclude_unset=True).items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    # Parse file fields from JSON strings before validation
    import json
    project_dict = {
        "id": project.id,
        "user_id": project.user_id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "latitude": float(project.latitude) if project.latitude else None,
        "longitude": float(project.longitude) if project.longitude else None,
        "country": project.country,
        "region": project.region,
        "collection_timestamp": project.collection_timestamp,
        "symptoms": project.symptoms,
        "clinical_severity": project.clinical_severity,
        "clinical_notes": project.clinical_notes,
        "protein_files": json.loads(project.protein_files) if project.protein_files else [],
        "clinical_files": json.loads(project.clinical_files) if project.clinical_files else [],
        "assay_files": json.loads(project.assay_files) if project.assay_files else [],
        "mutations_count": project.mutations_count,
        "drugs_count": project.drugs_count,
        "modifications_count": project.modifications_count,
        "deadliness_score": float(project.deadliness_score) if project.deadliness_score else None,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }
    project_response = ProjectResponse.model_validate(project_dict)
    return project_response


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Delete project - NO AUTH REQUIRED"""
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Delete associated files first
    try:
        delete_project_files(project_id)
    except Exception as e:
        print(f"Warning: Error deleting files for project {project_id}: {e}")
    
    # Manually delete related results using raw SQL to avoid cascade issues with created_at column
    try:
        # Delete mutations (using raw SQL to avoid created_at column issue)
        db.execute(text("DELETE FROM mutation_results WHERE project_id = :project_id"), {"project_id": project_id})
        
        # Delete drugs
        db.execute(text("DELETE FROM drug_candidate_results WHERE project_id = :project_id"), {"project_id": project_id})
        
        # Delete modifications
        db.execute(text("DELETE FROM modification_results WHERE project_id = :project_id"), {"project_id": project_id})
        
        # Now delete the project (using raw SQL to avoid ORM cascade issues)
        db.execute(text("DELETE FROM projects WHERE id = :project_id"), {"project_id": project_id})
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error deleting project {project_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )
    
    return None


@router.get("/{project_id}/status")
async def get_project_status(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get project processing status - NO AUTH REQUIRED"""
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return {
        "project_id": project.id,
        "status": project.status,
        "mutations_count": project.mutations_count,
        "drugs_count": project.drugs_count,
        "modifications_count": project.modifications_count
    }


@router.get("/{project_id}/pdb/{file_path:path}")
async def get_pdb_file(
    project_id: int,
    file_path: str,
    db: Session = Depends(get_db)
):
    """Get PDB file content - NO AUTH REQUIRED"""
    from fastapi.responses import FileResponse
    from app.services.file_service import get_file_path
    import os
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Verify file belongs to project
    protein_files = project.get_protein_files()
    if file_path not in protein_files:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="File does not belong to this project"
        )
    
    # Get full file path
    full_path = get_file_path(file_path)
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDB file not found"
        )
    
    # Return file
    return FileResponse(
        full_path,
        media_type="chemical/x-pdb",
        filename=os.path.basename(file_path)
    )

