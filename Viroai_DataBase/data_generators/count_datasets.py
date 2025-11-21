"""
Quick dataset counter - shows before/after dataset counts
"""

import os
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALL_VIRUSES = [
    "Adenovirus", "CMV", "Dengue", "Ebola", "HBV", "HCV", 
    "HIV-1", "HSV-1", "Influenza", "Monkeypox", "Rabies", 
    "RSV", "SARS-CoV-2", "Zika"
]

def count_files(directory, extensions=None):
    """Count files in directory"""
    if not os.path.exists(directory):
        return 0
    if extensions is None:
        extensions = ['.csv', '.json', '.fasta']
    count = 0
    for ext in extensions:
        count += len(list(Path(directory).rglob(f'*{ext}')))
    return count

def count_datasets():
    """Count current datasets"""
    print("="*70)
    print("CURRENT DATASET COUNT (BEFORE)")
    print("="*70)
    
    # Clinical
    clinical_files = 0
    clinical_viruses = 0
    for virus in ALL_VIRUSES:
        virus_dir = os.path.join(BASE_DIR, "clinical", virus)
        if os.path.exists(virus_dir):
            clinical_viruses += 1
            clinical_files += count_files(virus_dir)
    
    # Genomic
    genomic_files = 0
    genomic_viruses = 0
    for virus in ALL_VIRUSES:
        virus_dir = os.path.join(BASE_DIR, "genomic", virus)
        if os.path.exists(virus_dir):
            genomic_viruses += 1
            genomic_files += count_files(virus_dir)
    
    # Pharma
    pharma_dir = os.path.join(BASE_DIR, "pharma")
    pharma_files = count_files(pharma_dir)
    
    # Processed
    processed_dir = os.path.join(BASE_DIR, "processed")
    processed_files = count_files(processed_dir)
    
    # Migrations
    migrations_files = 0
    migrations_viruses = 0
    for virus in ALL_VIRUSES:
        virus_dir = os.path.join(BASE_DIR, "migrations", virus)
        if os.path.exists(virus_dir):
            migrations_viruses += 1
            migrations_files += count_files(virus_dir, ['.csv', '.json'])
    
    total_before = clinical_files + genomic_files + pharma_files + processed_files + migrations_files
    
    print(f"\nClinical Data:")
    print(f"  Viruses with data: {clinical_viruses}/14")
    print(f"  Files: {clinical_files}")
    print(f"  Expected per virus: 5 files (metadata, outcomes x2, treatments x2)")
    
    print(f"\nGenomic Data:")
    print(f"  Viruses with data: {genomic_viruses}/14")
    print(f"  Files: {genomic_files}")
    print(f"  Expected per virus: 4 files (FASTA, variants CSV, variants JSON, stats JSON)")
    
    print(f"\nPharmaceutical Data:")
    print(f"  Files: {pharma_files}")
    print(f"  Expected: 1 base file + 14 virus-specific files = 15+ files")
    
    print(f"\nProcessed Data:")
    print(f"  Files: {processed_files}")
    print(f"  Expected: 4 files (train, val, test, statistics)")
    
    print(f"\nMigrations Data:")
    print(f"  Viruses with data: {migrations_viruses}/14")
    print(f"  Files: {migrations_files}")
    print(f"  Expected per virus: 4 files (geographic, paths, trends, summary)")
    
    print(f"\n{'='*70}")
    print(f"TOTAL FILES (BEFORE): {total_before}")
    print(f"{'='*70}")
    
    # Calculate expected after
    print("\n" + "="*70)
    print("EXPECTED DATASET COUNT (AFTER GENERATION)")
    print("="*70)
    
    expected_clinical = 14 * 5  # 5 files per virus
    expected_genomic = 14 * 4   # 4 files per virus
    expected_pharma = 15 + 14   # Base + virus-specific
    expected_processed = 4       # train, val, test, stats
    expected_migrations = 14 * 4 # 4 files per virus
    
    total_after = expected_clinical + expected_genomic + expected_pharma + expected_processed + expected_migrations
    
    print(f"\nClinical Data: {expected_clinical} files (14 viruses × 5 files)")
    print(f"Genomic Data: {expected_genomic} files (14 viruses × 4 files)")
    print(f"Pharmaceutical Data: {expected_pharma} files")
    print(f"Processed Data: {expected_processed} files")
    print(f"Migrations Data: {expected_migrations} files (14 viruses × 4 files)")
    
    print(f"\n{'='*70}")
    print(f"TOTAL FILES (AFTER): {total_after}")
    print(f"INCREASE: +{total_after - total_before} files")
    print(f"{'='*70}")
    
    # Record counts
    print(f"\nExpected Records:")
    print(f"  Clinical: ~2,800 records (200 per virus)")
    print(f"  Genomic: ~1,400-2,800 sequences + ~2,100 variants")
    print(f"  Pharma: ~1,400 binding records (100 per virus)")
    print(f"  Processed: ~1,000-2,000 records (70-20-10 split)")
    print(f"  Migrations: ~2,100 geographic + ~700 migration paths")
    
    return total_before, total_after

if __name__ == "__main__":
    count_datasets()

