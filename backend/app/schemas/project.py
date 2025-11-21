"""
Project Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    country: Optional[str] = None
    region: Optional[str] = None
    collection_timestamp: Optional[datetime] = None
    symptoms: Optional[str] = None
    clinical_severity: Optional[str] = None
    clinical_notes: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    status: str
    protein_files: Optional[List[str]] = []
    clinical_files: Optional[List[str]] = []
    assay_files: Optional[List[str]] = []
    mutations_count: int = 0
    drugs_count: int = 0
    modifications_count: int = 0
    deadliness_score: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int

