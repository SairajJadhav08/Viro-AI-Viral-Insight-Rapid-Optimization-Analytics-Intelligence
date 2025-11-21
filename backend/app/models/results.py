"""
Results SQLAlchemy models (Mutation, Drug, Modification)
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, CHAR, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import json


class MutationResult(Base):
    """Mutation result model with 9-section analysis"""
    __tablename__ = "mutation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Basic mutation info
    mutation_position = Column(String(50), nullable=False)
    original_amino_acid = Column(CHAR(1), nullable=False)
    predicted_amino_acid = Column(CHAR(1), nullable=False)
    probability = Column(DECIMAL(5, 2))
    effect = Column(Text)
    risk_level = Column(String(50))  # Low, Medium, High
    
    # 9-section detailed analysis (JSON stored as text)
    genomic_level = Column(Text)
    probability_metrics = Column(Text)
    selective_pressure = Column(Text)
    structural_consequences = Column(Text)
    receptor_binding = Column(Text)
    immune_evasion = Column(Text)
    viral_fitness = Column(Text)
    pathogenicity = Column(Text)
    lineage_emergence = Column(Text)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="mutation_results")
    
    def get_genomic_level(self):
        """Parse genomic_level JSON"""
        if self.genomic_level:
            try:
                return json.loads(self.genomic_level)
            except:
                return {}
        return {}
    
    def set_genomic_level(self, data):
        """Set genomic_level as JSON"""
        self.genomic_level = json.dumps(data) if data else None


class DrugCandidateResult(Base):
    """Drug candidate result model with 11-section analysis"""
    __tablename__ = "drug_candidate_results"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Basic drug info
    drug_name = Column(String(255), nullable=False)
    smiles = Column(Text)
    binding_affinity = Column(DECIMAL(10, 2))
    ic50 = Column(String(50))
    logp = Column(DECIMAL(10, 2))
    molecular_weight = Column(DECIMAL(10, 2))
    formula = Column(String(255))
    heavy_atoms = Column(Integer)
    rank = Column(Integer)
    score = Column(Integer)
    
    # 11-section detailed analysis (JSON stored as text)
    molecular_identity = Column(Text)
    binding_metrics = Column(Text)
    interaction_map = Column(Text)
    structural_stability = Column(Text)
    physicochemical = Column(Text)
    adme = Column(Text)
    toxicology = Column(Text)
    comparative_scores = Column(Text)
    ensemble_analysis = Column(Text)
    resistance_vulnerability = Column(Text)
    chemical_diversity = Column(Text)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="drug_results")


class ModificationResult(Base):
    """Modification result model with 11-section analysis"""
    __tablename__ = "modification_results"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Basic modification info
    base_formula = Column(String(255))
    modified_formula = Column(String(255))
    changes = Column(Text)
    improvements = Column(Text)
    confidence = Column(DECIMAL(5, 2))
    
    # 11-section detailed analysis (JSON stored as text)
    modification_identity = Column(Text)
    structural_effects = Column(Text)
    physicochemical_changes = Column(Text)
    binding_affinity_effects = Column(Text)
    electronic_effects = Column(Text)
    stability_degradation = Column(Text)
    solubility_permeability = Column(Text)
    adme_shifts = Column(Text)
    toxicity_signatures = Column(Text)
    synthetic_feasibility = Column(Text)
    comparative_scoring = Column(Text)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="modification_results")

