"""
Script to measure actual ML processing time
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.project import Project
from app.services.processing_service import ProcessingService

def measure_processing_time():
    """Measure how long ML processing actually takes"""
    db = SessionLocal()
    try:
        # Create a test project or use existing one
        project = db.query(Project).filter(Project.id == 20).first()
        if not project:
            print("Project 20 not found")
            return
        
        print("=" * 70)
        print("ML PROCESSING TIME MEASUREMENT")
        print("=" * 70)
        print(f"\nProject: {project.title}")
        print(f"Sequence length: ~1273 (default SARS-CoV-2)")
        print(f"Drug candidates: 3 (default)")
        print(f"\nStarting timing...")
        
        # Create processing service
        processing_service = ProcessingService(db)
        
        # Measure file parsing time
        start_parse = time.time()
        parsed_data = processing_service._parse_project_files(project)
        parse_time = time.time() - start_parse
        print(f"\n[1] File Parsing: {parse_time:.2f} seconds")
        
        # Measure mutation prediction time
        start_mut = time.time()
        sequence = parsed_data.get("sequence", "")
        mutations = processing_service.ml_service.predict_mutations(
            sequence=sequence,
            protein_structure=parsed_data.get("protein_structure"),
            virus_name="SARS-CoV-2"
        )
        mut_time = time.time() - start_mut
        print(f"[2] Mutation Prediction ({len(mutations)} mutations): {mut_time:.2f} seconds")
        
        # Measure drug analysis time
        start_drug = time.time()
        drug_candidates = parsed_data.get("drug_candidates", [])
        analyzed_drugs = processing_service.ml_service.analyze_drug_candidates(
            drug_list=drug_candidates,
            target_protein="Spike Protein"
        )
        # Add binding affinity
        for drug in analyzed_drugs:
            if drug.get("smiles"):
                binding_affinity = processing_service.ml_service.predict_binding_affinity(
                    smiles=drug["smiles"],
                    virus_name="SARS-CoV-2"
                )
                drug["binding_affinity"] = binding_affinity
        drug_time = time.time() - start_drug
        print(f"[3] Drug Analysis ({len(analyzed_drugs)} drugs): {drug_time:.2f} seconds")
        
        # Measure modification time
        start_mod = time.time()
        if analyzed_drugs:
            top_drug = analyzed_drugs[0]
            modifications = processing_service.ml_service.suggest_modifications(
                base_compound={"name": top_drug.get("name", ""), "smiles": top_drug.get("smiles", "")}
            )
        else:
            modifications = []
        mod_time = time.time() - start_mod
        print(f"[4] Modification Generation ({len(modifications)} modifications): {mod_time:.2f} seconds")
        
        # Total time
        total_time = parse_time + mut_time + drug_time + mod_time
        print(f"\n" + "=" * 70)
        print("TOTAL PROCESSING TIME BREAKDOWN")
        print("=" * 70)
        print(f"File Parsing:        {parse_time:>6.2f} seconds ({parse_time/total_time*100:.1f}%)")
        print(f"Mutation Prediction: {mut_time:>6.2f} seconds ({mut_time/total_time*100:.1f}%)")
        print(f"Drug Analysis:       {drug_time:>6.2f} seconds ({drug_time/total_time*100:.1f}%)")
        print(f"Modifications:       {mod_time:>6.2f} seconds ({mod_time/total_time*100:.1f}%)")
        print(f"{'-' * 70}")
        print(f"TOTAL:               {total_time:>6.2f} seconds ({total_time/60:.2f} minutes)")
        print(f"\n[OK] Estimated time for new projects: {total_time:.1f} - {total_time*1.5:.1f} seconds")
        print(f"   (Actual time may vary based on file sizes and system load)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    measure_processing_time()

