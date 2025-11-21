"""
Results API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.models.results import MutationResult, DrugCandidateResult, ModificationResult
from app.schemas.results import (
    MutationResultResponse,
    DrugCandidateResultResponse,
    ModificationResultResponse,
    ProjectResultsResponse
)
from app.core.dependencies import get_user_or_create_default
import json

router = APIRouter(prefix="/projects", tags=["results"])


def _parse_json_field(field_value: str) -> dict:
    """Parse JSON field from database"""
    if not field_value:
        return {}
    try:
        return json.loads(field_value)
    except:
        return {}


@router.get("/{project_id}/results", response_model=ProjectResultsResponse)
async def get_project_results(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get complete project results - NO AUTH REQUIRED"""
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get mutations - use raw SQL to avoid created_at column issue
    from sqlalchemy import text
    mutations_query = text("""
        SELECT id, project_id, mutation_position, original_amino_acid, predicted_amino_acid,
               probability, effect, risk_level, genomic_level, probability_metrics,
               selective_pressure, structural_consequences, receptor_binding, immune_evasion,
               viral_fitness, pathogenicity, lineage_emergence
        FROM mutation_results
        WHERE project_id = :project_id
    """)
    mutations_rows = db.execute(mutations_query, {"project_id": project_id}).fetchall()
    mutations = []
    for row in mutations_rows:
        m = MutationResult()
        m.id = row[0]
        m.project_id = row[1]
        m.mutation_position = row[2]
        m.original_amino_acid = row[3]
        m.predicted_amino_acid = row[4]
        m.probability = row[5]
        m.effect = row[6]
        m.risk_level = row[7]
        m.genomic_level = row[8]
        m.probability_metrics = row[9]
        m.selective_pressure = row[10]
        m.structural_consequences = row[11]
        m.receptor_binding = row[12]
        m.immune_evasion = row[13]
        m.viral_fitness = row[14]
        m.pathogenicity = row[15]
        m.lineage_emergence = row[16]
        mutations.append(m)
    
    # Get drugs
    drugs_query = text("""
        SELECT id, project_id, drug_name, smiles, binding_affinity, ic50, logp,
               molecular_weight, formula, heavy_atoms, rank, score, molecular_identity,
               binding_metrics, interaction_map, structural_stability, physicochemical,
               adme, toxicology, comparative_scores, ensemble_analysis, resistance_vulnerability,
               chemical_diversity
        FROM drug_candidate_results
        WHERE project_id = :project_id
        ORDER BY rank
    """)
    drugs_rows = db.execute(drugs_query, {"project_id": project_id}).fetchall()
    drugs = []
    for row in drugs_rows:
        d = DrugCandidateResult()
        d.id = row[0]
        d.project_id = row[1]
        d.drug_name = row[2]
        d.smiles = row[3]
        d.binding_affinity = row[4]
        d.ic50 = row[5]
        d.logp = row[6]
        d.molecular_weight = row[7]
        d.formula = row[8]
        d.heavy_atoms = row[9]
        d.rank = row[10]
        d.score = row[11]
        d.molecular_identity = row[12]
        d.binding_metrics = row[13]
        d.interaction_map = row[14]
        d.structural_stability = row[15]
        d.physicochemical = row[16]
        d.adme = row[17]
        d.toxicology = row[18]
        d.comparative_scores = row[19]
        d.ensemble_analysis = row[20]
        d.resistance_vulnerability = row[21]
        d.chemical_diversity = row[22]
        drugs.append(d)
    
    # Get modifications
    mods_query = text("""
        SELECT id, project_id, base_formula, modified_formula, changes, improvements,
               confidence, modification_identity, structural_effects, physicochemical_changes,
               binding_affinity_effects, electronic_effects, stability_degradation,
               solubility_permeability, adme_shifts, toxicity_signatures, synthetic_feasibility,
               comparative_scoring
        FROM modification_results
        WHERE project_id = :project_id
    """)
    mods_rows = db.execute(mods_query, {"project_id": project_id}).fetchall()
    modifications = []
    for row in mods_rows:
        mod = ModificationResult()
        mod.id = row[0]
        mod.project_id = row[1]
        mod.base_formula = row[2]
        mod.modified_formula = row[3]
        mod.changes = row[4]
        mod.improvements = row[5]
        mod.confidence = row[6]
        mod.modification_identity = row[7]
        mod.structural_effects = row[8]
        mod.physicochemical_changes = row[9]
        mod.binding_affinity_effects = row[10]
        mod.electronic_effects = row[11]
        mod.stability_degradation = row[12]
        mod.solubility_permeability = row[13]
        mod.adme_shifts = row[14]
        mod.toxicity_signatures = row[15]
        mod.synthetic_feasibility = row[16]
        mod.comparative_scoring = row[17]
        modifications.append(mod)
    
    # Format mutations
    mutation_responses = []
    for m in mutations:
        # Handle missing created_at column gracefully
        created_at = getattr(m, 'created_at', None) or datetime.utcnow()
        mutation_data = MutationResultResponse(
            id=m.id,
            project_id=m.project_id,
            mutation_position=m.mutation_position,
            original_amino_acid=m.original_amino_acid,
            predicted_amino_acid=m.predicted_amino_acid,
            probability=m.probability,
            effect=m.effect,
            risk_level=m.risk_level,
            genomic_level=_parse_json_field(m.genomic_level),
            probability_metrics=_parse_json_field(m.probability_metrics),
            selective_pressure=_parse_json_field(m.selective_pressure),
            structural_consequences=_parse_json_field(m.structural_consequences),
            receptor_binding=_parse_json_field(m.receptor_binding),
            immune_evasion=_parse_json_field(m.immune_evasion),
            viral_fitness=_parse_json_field(m.viral_fitness),
            pathogenicity=_parse_json_field(m.pathogenicity),
            lineage_emergence=_parse_json_field(m.lineage_emergence),
            created_at=created_at
        )
        mutation_responses.append(mutation_data)
    
    # Format drugs
    drug_responses = []
    for d in drugs:
        # Handle missing created_at column gracefully
        created_at = getattr(d, 'created_at', None) or datetime.utcnow()
        drug_data = DrugCandidateResultResponse(
            id=d.id,
            project_id=d.project_id,
            drug_name=d.drug_name,
            smiles=d.smiles,
            binding_affinity=d.binding_affinity,
            ic50=d.ic50,
            logp=d.logp,
            molecular_weight=d.molecular_weight,
            formula=d.formula,
            heavy_atoms=d.heavy_atoms,
            rank=d.rank,
            score=d.score,
            molecular_identity=_parse_json_field(d.molecular_identity),
            binding_metrics=_parse_json_field(d.binding_metrics),
            interaction_map=_parse_json_field(d.interaction_map),
            structural_stability=_parse_json_field(d.structural_stability),
            physicochemical=_parse_json_field(d.physicochemical),
            adme=_parse_json_field(d.adme),
            toxicology=_parse_json_field(d.toxicology),
            comparative_scores=_parse_json_field(d.comparative_scores),
            ensemble_analysis=_parse_json_field(d.ensemble_analysis),
            resistance_vulnerability=_parse_json_field(d.resistance_vulnerability),
            chemical_diversity=_parse_json_field(d.chemical_diversity),
            created_at=created_at
        )
        drug_responses.append(drug_data)
    
    # Format modifications
    modification_responses = []
    for m in modifications:
        # Handle created_at - use current time if None (column doesn't exist in DB)
        created_at = getattr(m, 'created_at', None)
        if created_at is None:
            created_at = datetime.utcnow()
        mod_data = ModificationResultResponse(
            id=m.id,
            project_id=m.project_id,
            base_formula=m.base_formula,
            modified_formula=m.modified_formula,
            changes=m.changes,
            improvements=m.improvements,
            confidence=m.confidence,
            modification_identity=_parse_json_field(m.modification_identity),
            structural_effects=_parse_json_field(m.structural_effects),
            physicochemical_changes=_parse_json_field(m.physicochemical_changes),
            binding_affinity_effects=_parse_json_field(m.binding_affinity_effects),
            electronic_effects=_parse_json_field(m.electronic_effects),
            stability_degradation=_parse_json_field(m.stability_degradation),
            solubility_permeability=_parse_json_field(m.solubility_permeability),
            adme_shifts=_parse_json_field(m.adme_shifts),
            toxicity_signatures=_parse_json_field(m.toxicity_signatures),
            synthetic_feasibility=_parse_json_field(m.synthetic_feasibility),
            comparative_scoring=_parse_json_field(m.comparative_scoring),
            created_at=created_at
        )
        modification_responses.append(mod_data)
    
    # Get structure data from project's protein files
    structure_data = None
    protein_files = project.get_protein_files()
    if protein_files:
        # Find first PDB file
        pdb_file = None
        for file_path in protein_files:
            if file_path and file_path.endswith('.pdb'):
                pdb_file = file_path
                break
        
        if pdb_file:
            # Try to extract structure data from the PDB file
            from app.services.file_service import get_file_path
            import os
            full_path = get_file_path(pdb_file)
            if os.path.exists(full_path):
                # Parse PDB to get structure data
                from app.services.processing_service import ProcessingService
                processing_service = ProcessingService(db)
                pdb_data = processing_service._parse_pdb(full_path)
                if pdb_data:
                    structure_data = {
                        "residues_count": pdb_data.get("residues_count"),
                        "molecular_weight_kda": pdb_data.get("molecular_weight_kda"),
                        "pdb_file_path": pdb_file  # Relative path for frontend access
                    }
    
    return ProjectResultsResponse(
        project={
            "id": project.id,
            "title": project.title,
            "status": project.status,
            "deadliness_score": float(project.deadliness_score) if project.deadliness_score else None
        },
        mutations=mutation_responses,
        drugs=drug_responses,
        modifications=modification_responses,
        structure_data=structure_data
    )


@router.get("/{project_id}/mutations", response_model=list[MutationResultResponse])
async def get_mutations(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get mutation results for a project - NO AUTH REQUIRED"""
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    mutations = db.query(MutationResult).filter(
        MutationResult.project_id == project_id
    ).all()
    
    return [
        MutationResultResponse(
            id=m.id,
            project_id=m.project_id,
            mutation_position=m.mutation_position,
            original_amino_acid=m.original_amino_acid,
            predicted_amino_acid=m.predicted_amino_acid,
            probability=m.probability,
            effect=m.effect,
            risk_level=m.risk_level,
            genomic_level=_parse_json_field(m.genomic_level),
            probability_metrics=_parse_json_field(m.probability_metrics),
            selective_pressure=_parse_json_field(m.selective_pressure),
            structural_consequences=_parse_json_field(m.structural_consequences),
            receptor_binding=_parse_json_field(m.receptor_binding),
            immune_evasion=_parse_json_field(m.immune_evasion),
            viral_fitness=_parse_json_field(m.viral_fitness),
            pathogenicity=_parse_json_field(m.pathogenicity),
            lineage_emergence=_parse_json_field(m.lineage_emergence),
            created_at=m.created_at
        )
        for m in mutations
    ]


@router.get("/{project_id}/drugs", response_model=list[DrugCandidateResultResponse])
async def get_drugs(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get drug candidate results for a project - NO AUTH REQUIRED"""
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    drugs = db.query(DrugCandidateResult).filter(
        DrugCandidateResult.project_id == project_id
    ).order_by(DrugCandidateResult.rank).all()
    
    return [
        DrugCandidateResultResponse(
            id=d.id,
            project_id=d.project_id,
            drug_name=d.drug_name,
            smiles=d.smiles,
            binding_affinity=d.binding_affinity,
            ic50=d.ic50,
            logp=d.logp,
            molecular_weight=d.molecular_weight,
            formula=d.formula,
            heavy_atoms=d.heavy_atoms,
            rank=d.rank,
            score=d.score,
            molecular_identity=_parse_json_field(d.molecular_identity),
            binding_metrics=_parse_json_field(d.binding_metrics),
            interaction_map=_parse_json_field(d.interaction_map),
            structural_stability=_parse_json_field(d.structural_stability),
            physicochemical=_parse_json_field(d.physicochemical),
            adme=_parse_json_field(d.adme),
            toxicology=_parse_json_field(d.toxicology),
            comparative_scores=_parse_json_field(d.comparative_scores),
            ensemble_analysis=_parse_json_field(d.ensemble_analysis),
            resistance_vulnerability=_parse_json_field(d.resistance_vulnerability),
            chemical_diversity=_parse_json_field(d.chemical_diversity),
            created_at=d.created_at
        )
        for d in drugs
    ]


@router.get("/{project_id}/modifications", response_model=list[ModificationResultResponse])
async def get_modifications(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get modification results for a project - NO AUTH REQUIRED"""
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    modifications = db.query(ModificationResult).filter(
        ModificationResult.project_id == project_id
    ).all()
    
    return [
        ModificationResultResponse(
            id=m.id,
            project_id=m.project_id,
            base_formula=m.base_formula,
            modified_formula=m.modified_formula,
            changes=m.changes,
            improvements=m.improvements,
            confidence=m.confidence,
            modification_identity=_parse_json_field(m.modification_identity),
            structural_effects=_parse_json_field(m.structural_effects),
            physicochemical_changes=_parse_json_field(m.physicochemical_changes),
            binding_affinity_effects=_parse_json_field(m.binding_affinity_effects),
            electronic_effects=_parse_json_field(m.electronic_effects),
            stability_degradation=_parse_json_field(m.stability_degradation),
            solubility_permeability=_parse_json_field(m.solubility_permeability),
            adme_shifts=_parse_json_field(m.adme_shifts),
            toxicity_signatures=_parse_json_field(m.toxicity_signatures),
            synthetic_feasibility=_parse_json_field(m.synthetic_feasibility),
            comparative_scoring=_parse_json_field(m.comparative_scoring),
            created_at=m.created_at
        )
        for m in modifications
    ]

