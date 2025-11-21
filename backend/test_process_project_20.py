"""
Test script to manually process project 20 and see what happens
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.project import Project
from app.services.processing_service import ProcessingService
import traceback

def test_process_project():
    db = SessionLocal()
    try:
        # Get project 20
        project = db.query(Project).filter(Project.id == 20).first()
        if not project:
            print("Project 20 not found!")
            return
        
        print("=" * 70)
        print("PROJECT 20 STATUS BEFORE PROCESSING")
        print("=" * 70)
        print(f"ID: {project.id}")
        print(f"Title: {project.title}")
        print(f"Status: {project.status}")
        print(f"Created: {project.created_at}")
        print(f"Updated: {project.updated_at}")
        print(f"Mutations: {project.mutations_count}")
        print(f"Drugs: {project.drugs_count}")
        print(f"Modifications: {project.modifications_count}")
        print(f"Deadliness Score: {project.deadliness_score}")
        
        print("\n" + "=" * 70)
        print("ATTEMPTING TO PROCESS PROJECT...")
        print("=" * 70)
        
        # Create processing service
        processing_service = ProcessingService(db)
        
        # Process the project
        result = processing_service.process_project(20, fast_mode=False)
        
        print("\n" + "=" * 70)
        print("PROCESSING RESULT")
        print("=" * 70)
        print(f"Result: {result}")
        
        # Refresh project from database
        db.refresh(project)
        
        print("\n" + "=" * 70)
        print("PROJECT 20 STATUS AFTER PROCESSING")
        print("=" * 70)
        print(f"Status: {project.status}")
        print(f"Updated: {project.updated_at}")
        print(f"Mutations: {project.mutations_count}")
        print(f"Drugs: {project.drugs_count}")
        print(f"Modifications: {project.modifications_count}")
        print(f"Deadliness Score: {project.deadliness_score}")
        
        # Check results in database
        from app.models.results import MutationResult, DrugCandidateResult, ModificationResult
        mut_count = db.query(MutationResult).filter(MutationResult.project_id == 20).count()
        drug_count = db.query(DrugCandidateResult).filter(DrugCandidateResult.project_id == 20).count()
        mod_count = db.query(ModificationResult).filter(ModificationResult.project_id == 20).count()
        
        print("\n" + "=" * 70)
        print("RESULTS IN DATABASE")
        print("=" * 70)
        print(f"Mutations in DB: {mut_count}")
        print(f"Drugs in DB: {drug_count}")
        print(f"Modifications in DB: {mod_count}")
        
        if project.status == "Completed":
            print("\n✅ SUCCESS: Project processed successfully!")
        elif project.status == "Failed":
            print("\n❌ FAILED: Project processing failed. Check errors above.")
        else:
            print(f"\n⚠️  WARNING: Project status is still '{project.status}'")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_process_project()

