"""
Data Validation Script for Viro-AI
Validates folder structure, data quality, and checks for duplicates
"""

import os
import pandas as pd
import json
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_cleaner import DataCleaner

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALL_VIRUSES = [
    "Adenovirus", "CMV", "Dengue", "Ebola", "HBV", "HCV", 
    "HIV-1", "HSV-1", "Influenza", "Monkeypox", "Rabies", 
    "RSV", "SARS-CoV-2", "Zika"
]

def validate_folder_structure(virus, data_type):
    """Validate folder structure for a virus and data type"""
    cleaner = DataCleaner(BASE_DIR)
    paths = cleaner.ensure_folder_structure(virus, data_type)
    
    missing = []
    for name, path in paths.items():
        if not os.path.exists(path):
            missing.append(f"{name}: {path}")
    
    return len(missing) == 0, missing, paths

def check_duplicates_in_file(file_path, duplicate_columns):
    """Check for duplicates in a CSV file"""
    if not os.path.exists(file_path):
        return 0, 0
    
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return 0, 0
        
        if duplicate_columns and all(col in df.columns for col in duplicate_columns):
            duplicates = df.duplicated(subset=duplicate_columns).sum()
        else:
            duplicates = df.duplicated().sum()
        
        return len(df), duplicates
    except Exception as e:
        print(f"    [ERROR] Could not read {file_path}: {e}")
        return 0, 0

def validate_clinical_data(virus):
    """Validate clinical data for a virus"""
    print(f"\n  Validating clinical data for {virus}...")
    
    valid, missing, paths = validate_folder_structure(virus, "clinical")
    if not valid:
        print(f"    ✗ Missing folders: {missing}")
        return False
    
    issues = []
    
    # Check binding_efficacy.csv
    binding_file = os.path.join(paths['treatments'], "binding_efficacy.csv")
    total, duplicates = check_duplicates_in_file(
        binding_file, 
        ['virus', 'drug_id', 'protein']
    )
    if duplicates > 0:
        issues.append(f"binding_efficacy.csv: {duplicates} duplicates")
    if total > 0:
        print(f"    ✓ binding_efficacy.csv: {total} records, {duplicates} duplicates")
    
    # Check patient_outcomes.csv
    outcomes_file = os.path.join(paths['outcomes'], "patient_outcomes.csv")
    total, duplicates = check_duplicates_in_file(
        outcomes_file,
        ['patient_id']
    )
    if duplicates > 0:
        issues.append(f"patient_outcomes.csv: {duplicates} duplicates")
    if total > 0:
        print(f"    ✓ patient_outcomes.csv: {total} records, {duplicates} duplicates")
    
    # Check metadata
    metadata_file = os.path.join(paths['metadata'], "summary.json")
    if os.path.exists(metadata_file):
        print(f"    ✓ summary.json exists")
    else:
        issues.append("summary.json missing")
    
    if issues:
        print(f"    ⚠ Issues found: {', '.join(issues)}")
        return False
    
    return True

def validate_genomic_data(virus):
    """Validate genomic data for a virus"""
    print(f"\n  Validating genomic data for {virus}...")
    
    valid, missing, paths = validate_folder_structure(virus, "genomic")
    if not valid:
        print(f"    ✗ Missing folders: {missing}")
        return False
    
    issues = []
    
    # Check variants.csv
    variants_file = os.path.join(paths['variants'], "variants.csv")
    total, duplicates = check_duplicates_in_file(
        variants_file,
        ['mutation', 'position', 'virus']
    )
    if duplicates > 0:
        issues.append(f"variants.csv: {duplicates} duplicates")
    if total > 0:
        print(f"    ✓ variants.csv: {total} records, {duplicates} duplicates")
    
    # Check FASTA file
    fasta_file = os.path.join(paths['raw_sequence'], f"{virus}_all.fasta")
    if os.path.exists(fasta_file):
        file_size = os.path.getsize(fasta_file)
        print(f"    ✓ {virus}_all.fasta exists ({file_size:,} bytes)")
    else:
        issues.append("FASTA file missing")
    
    # Check statistics
    stats_file = os.path.join(paths['processed'], "sequence_statistics.json")
    if os.path.exists(stats_file):
        print(f"    ✓ sequence_statistics.json exists")
    else:
        issues.append("sequence_statistics.json missing")
    
    if issues:
        print(f"    ⚠ Issues found: {', '.join(issues)}")
        return False
    
    return True

def validate_pharma_data(virus):
    """Validate pharmaceutical data for a virus"""
    print(f"\n  Validating pharmaceutical data for {virus}...")
    
    valid, missing, paths = validate_folder_structure(virus, "pharma")
    if not valid:
        print(f"    ✗ Missing folders: {missing}")
        return False
    
    issues = []
    
    # Check binding data
    binding_file = os.path.join(paths['real_world_binding'], f"{virus}_binding.csv")
    total, duplicates = check_duplicates_in_file(
        binding_file,
        ['virus', 'drug_id', 'protein']
    )
    if duplicates > 0:
        issues.append(f"{virus}_binding.csv: {duplicates} duplicates")
    if total > 0:
        print(f"    ✓ {virus}_binding.csv: {total} records, {duplicates} duplicates")
    elif not os.path.exists(binding_file):
        issues.append(f"{virus}_binding.csv missing")
    
    if issues:
        print(f"    ⚠ Issues found: {', '.join(issues)}")
        return False
    
    return True

def validate_processed_data():
    """Validate processed data"""
    print(f"\n  Validating processed data...")
    
    processed_dir = os.path.join(BASE_DIR, "processed")
    if not os.path.exists(processed_dir):
        print(f"    ✗ Processed directory does not exist")
        return False
    
    issues = []
    
    # Check train/val/test files
    for split in ['train_data.csv', 'validation_data.csv', 'test_data.csv']:
        file_path = os.path.join(processed_dir, split)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total, duplicates = check_duplicates_in_file(file_path, None)
            if duplicates > 0:
                issues.append(f"{split}: {duplicates} duplicates")
            print(f"    ✓ {split}: {total} records, {duplicates} duplicates")
        else:
            issues.append(f"{split} missing")
    
    # Check statistics
    stats_file = os.path.join(processed_dir, "dataset_statistics.json")
    if os.path.exists(stats_file):
        print(f"    ✓ dataset_statistics.json exists")
    else:
        issues.append("dataset_statistics.json missing")
    
    if issues:
        print(f"    ⚠ Issues found: {', '.join(issues)}")
        return False
    
    return True

def validate_migrations_data(virus):
    """Validate migrations data for a virus"""
    print(f"\n  Validating migrations data for {virus}...")
    
    valid, missing, paths = validate_folder_structure(virus, "migrations")
    if not valid:
        print(f"    ✗ Missing folders: {missing}")
        return False
    
    issues = []
    
    # Check geographic spread
    geo_file = os.path.join(paths['base'], "geographic_spread.csv")
    total, duplicates = check_duplicates_in_file(
        geo_file,
        ['country', 'date', 'virus']
    )
    if duplicates > 0:
        issues.append(f"geographic_spread.csv: {duplicates} duplicates")
    if total > 0:
        print(f"    ✓ geographic_spread.csv: {total} records, {duplicates} duplicates")
    
    if issues:
        print(f"    ⚠ Issues found: {', '.join(issues)}")
        return False
    
    return True

def main():
    """Main validation function"""
    print("="*80)
    print("VIRO-AI DATA VALIDATION")
    print("="*80)
    
    results = {
        'clinical': 0,
        'genomic': 0,
        'pharma': 0,
        'processed': 0,
        'migrations': 0
    }
    
    total_viruses = len(ALL_VIRUSES)
    
    # Validate clinical data
    print("\n" + "="*80)
    print("VALIDATING CLINICAL DATA")
    print("="*80)
    for virus in ALL_VIRUSES:
        if validate_clinical_data(virus):
            results['clinical'] += 1
    
    # Validate genomic data
    print("\n" + "="*80)
    print("VALIDATING GENOMIC DATA")
    print("="*80)
    for virus in ALL_VIRUSES:
        if validate_genomic_data(virus):
            results['genomic'] += 1
    
    # Validate pharma data
    print("\n" + "="*80)
    print("VALIDATING PHARMACEUTICAL DATA")
    print("="*80)
    for virus in ALL_VIRUSES:
        if validate_pharma_data(virus):
            results['pharma'] += 1
    
    # Validate processed data
    print("\n" + "="*80)
    print("VALIDATING PROCESSED DATA")
    print("="*80)
    if validate_processed_data():
        results['processed'] = 1
    
    # Validate migrations data
    print("\n" + "="*80)
    print("VALIDATING MIGRATIONS DATA")
    print("="*80)
    for virus in ALL_VIRUSES:
        if validate_migrations_data(virus):
            results['migrations'] += 1
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print(f"Clinical Data:     {results['clinical']}/{total_viruses} viruses")
    print(f"Genomic Data:      {results['genomic']}/{total_viruses} viruses")
    print(f"Pharma Data:       {results['pharma']}/{total_viruses} viruses")
    print(f"Processed Data:    {'✓' if results['processed'] else '✗'}")
    print(f"Migrations Data:   {results['migrations']}/{total_viruses} viruses")
    
    all_valid = (
        results['clinical'] == total_viruses and
        results['genomic'] == total_viruses and
        results['pharma'] == total_viruses and
        results['processed'] == 1 and
        results['migrations'] == total_viruses
    )
    
    if all_valid:
        print("\n✓ ALL DATA VALIDATED SUCCESSFULLY!")
        return True
    else:
        print("\n⚠ SOME VALIDATION ISSUES FOUND")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

