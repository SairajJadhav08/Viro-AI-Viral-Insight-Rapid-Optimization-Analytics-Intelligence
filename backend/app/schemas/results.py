"""
Results Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class MutationResultResponse(BaseModel):
    id: int
    project_id: int
    mutation_position: str
    original_amino_acid: str
    predicted_amino_acid: str
    probability: Optional[Decimal]
    effect: Optional[str]
    risk_level: Optional[str]
    genomic_level: Optional[Dict[str, Any]] = {}
    probability_metrics: Optional[Dict[str, Any]] = {}
    selective_pressure: Optional[Dict[str, Any]] = {}
    structural_consequences: Optional[Dict[str, Any]] = {}
    receptor_binding: Optional[Dict[str, Any]] = {}
    immune_evasion: Optional[Dict[str, Any]] = {}
    viral_fitness: Optional[Dict[str, Any]] = {}
    pathogenicity: Optional[Dict[str, Any]] = {}
    lineage_emergence: Optional[Dict[str, Any]] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class DrugCandidateResultResponse(BaseModel):
    id: int
    project_id: int
    drug_name: str
    smiles: Optional[str]
    binding_affinity: Optional[Decimal]
    ic50: Optional[str]
    logp: Optional[Decimal]
    molecular_weight: Optional[Decimal]
    formula: Optional[str]
    heavy_atoms: Optional[int]
    rank: int
    score: int
    molecular_identity: Optional[Dict[str, Any]] = {}
    binding_metrics: Optional[Dict[str, Any]] = {}
    interaction_map: Optional[Dict[str, Any]] = {}
    structural_stability: Optional[Dict[str, Any]] = {}
    physicochemical: Optional[Dict[str, Any]] = {}
    adme: Optional[Dict[str, Any]] = {}
    toxicology: Optional[Dict[str, Any]] = {}
    comparative_scores: Optional[Dict[str, Any]] = {}
    ensemble_analysis: Optional[Dict[str, Any]] = {}
    resistance_vulnerability: Optional[Dict[str, Any]] = {}
    chemical_diversity: Optional[Dict[str, Any]] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class ModificationResultResponse(BaseModel):
    id: int
    project_id: int
    base_formula: Optional[str]
    modified_formula: Optional[str]
    changes: Optional[str]
    improvements: Optional[str]
    confidence: Optional[Decimal]
    modification_identity: Optional[Dict[str, Any]] = {}
    structural_effects: Optional[Dict[str, Any]] = {}
    physicochemical_changes: Optional[Dict[str, Any]] = {}
    binding_affinity_effects: Optional[Dict[str, Any]] = {}
    electronic_effects: Optional[Dict[str, Any]] = {}
    stability_degradation: Optional[Dict[str, Any]] = {}
    solubility_permeability: Optional[Dict[str, Any]] = {}
    adme_shifts: Optional[Dict[str, Any]] = {}
    toxicity_signatures: Optional[Dict[str, Any]] = {}
    synthetic_feasibility: Optional[Dict[str, Any]] = {}
    comparative_scoring: Optional[Dict[str, Any]] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectResultsResponse(BaseModel):
    project: Dict[str, Any]
    mutations: list[MutationResultResponse]
    drugs: list[DrugCandidateResultResponse]
    modifications: list[ModificationResultResponse]
    structure_data: Optional[Dict[str, Any]] = None  # PDB structure data (residues_count, molecular_weight_kda, pdb_file_path)

