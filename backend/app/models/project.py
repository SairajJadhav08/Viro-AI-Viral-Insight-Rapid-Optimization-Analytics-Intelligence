"""
Project SQLAlchemy model
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import json


class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="Pending")  # Pending, Processing, Completed, Failed
    
    # Geolocation
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    country = Column(String(100))
    region = Column(String(100))
    
    # Clinical data
    collection_timestamp = Column(TIMESTAMP)
    symptoms = Column(Text)
    clinical_severity = Column(String(50))
    clinical_notes = Column(Text)
    
    # File paths (JSON arrays stored as text)
    protein_files = Column(Text)
    clinical_files = Column(Text)
    assay_files = Column(Text)
    
    # Result counts
    mutations_count = Column(Integer, default=0)
    drugs_count = Column(Integer, default=0)
    modifications_count = Column(Integer, default=0)
    
    # Deadliness score
    deadliness_score = Column(DECIMAL(5, 2))
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="projects")
    mutation_results = relationship("MutationResult", back_populates="project", cascade="all, delete-orphan")
    drug_results = relationship("DrugCandidateResult", back_populates="project", cascade="all, delete-orphan")
    modification_results = relationship("ModificationResult", back_populates="project", cascade="all, delete-orphan")
    
    def get_protein_files(self):
        """Parse protein_files JSON"""
        if self.protein_files:
            try:
                return json.loads(self.protein_files)
            except:
                return []
        return []
    
    def set_protein_files(self, files_list):
        """Set protein_files as JSON"""
        self.protein_files = json.dumps(files_list) if files_list else None
    
    def get_clinical_files(self):
        """Parse clinical_files JSON"""
        if self.clinical_files:
            try:
                return json.loads(self.clinical_files)
            except:
                return []
        return []
    
    def set_clinical_files(self, files_list):
        """Set clinical_files as JSON"""
        self.clinical_files = json.dumps(files_list) if files_list else None
    
    def get_assay_files(self):
        """Parse assay_files JSON"""
        if self.assay_files:
            try:
                return json.loads(self.assay_files)
            except:
                return []
        return []
    
    def set_assay_files(self, files_list):
        """Set assay_files as JSON"""
        self.assay_files = json.dumps(files_list) if files_list else None

