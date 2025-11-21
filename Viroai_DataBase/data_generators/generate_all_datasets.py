"""
Master Dataset Generator for Viro-AI
Orchestrates generation of all datasets following the 70-20-10 model
"""

import os
import sys
from datetime import datetime

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from generate_clinical_data import generate_clinical_datasets
from generate_genomic_data import generate_genomic_datasets
from generate_pharma_data import generate_pharma_datasets
from generate_processed_data import generate_processed_datasets
from generate_migrations_data import generate_migrations_datasets

# All viruses in the system
ALL_VIRUSES = [
    "Adenovirus", "CMV", "Dengue", "Ebola", "HBV", "HCV", 
    "HIV-1", "HSV-1", "Influenza", "Monkeypox", "Rabies", 
    "RSV", "SARS-CoV-2", "Zika"
]

# 70-20-10 split ratios
TRAIN_RATIO = 0.70
VAL_RATIO = 0.20
TEST_RATIO = 0.10

def main():
    """Main orchestrator function"""
    print("\n" + "="*80)
    print("VIRO-AI COMPREHENSIVE DATASET GENERATOR")
    print("Following 70-20-10 Train-Validation-Test Model")
    print("="*80)
    print(f"\nGenerating datasets for {len(ALL_VIRUSES)} viruses:")
    for i, virus in enumerate(ALL_VIRUSES, 1):
        print(f"  {i}. {virus}")
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting data generation...")
    
    results = {
        'clinical': False,
        'genomic': False,
        'pharma': False,
        'processed': False,
        'migrations': False
    }
    
    try:
        # 1. Generate Clinical Data
        print("\n" + "="*80)
        print("STEP 1: Generating Clinical Data")
        print("="*80)
        results['clinical'] = generate_clinical_datasets(ALL_VIRUSES)
        
        # 2. Generate Genomic Data
        print("\n" + "="*80)
        print("STEP 2: Generating Genomic Data")
        print("="*80)
        results['genomic'] = generate_genomic_datasets(ALL_VIRUSES)
        
        # 3. Generate Pharma Data
        print("\n" + "="*80)
        print("STEP 3: Generating Pharmaceutical Data")
        print("="*80)
        results['pharma'] = generate_pharma_datasets(ALL_VIRUSES)
        
        # 4. Generate Migrations Data
        print("\n" + "="*80)
        print("STEP 4: Generating Migrations/Geographic Spread Data")
        print("="*80)
        results['migrations'] = generate_migrations_datasets(ALL_VIRUSES)
        
        # 5. Generate Processed Data (70-20-10 splits)
        print("\n" + "="*80)
        print("STEP 5: Generating Processed Data with 70-20-10 Splits")
        print("="*80)
        results['processed'] = generate_processed_datasets(ALL_VIRUSES, TRAIN_RATIO, VAL_RATIO, TEST_RATIO)
        
        # Summary
        print("\n" + "="*80)
        print("GENERATION SUMMARY")
        print("="*80)
        for data_type, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"  {data_type.upper():15} : {status}")
        
        all_success = all(results.values())
        if all_success:
            print("\n" + "="*80)
            print("✓ ALL DATASETS GENERATED SUCCESSFULLY!")
            print("="*80)
            return True
        else:
            print("\n" + "="*80)
            print("⚠ SOME DATASETS FAILED TO GENERATE")
            print("="*80)
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Fatal error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

