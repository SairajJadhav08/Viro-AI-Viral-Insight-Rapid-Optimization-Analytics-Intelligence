# clean_and_merge.py
"""
Data Cleaning and Preparation Pipeline for Viro-AI
Prepares drug-virus binding data for ML model training
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

# Try importing RDKit (may not be installed yet)
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, AllChem
    RDKIT_AVAILABLE = True
    print("[OK] RDKit available for SMILES validation")
except ImportError:
    RDKIT_AVAILABLE = False
    print("[WARNING] RDKit not installed - skipping SMILES validation")
    print("[INFO] Install with: pip install rdkit-pypi")

# === CONFIGURATION ===
DRUGS_FILE = "Viroai_DataBase/pharma/approved-drugs/antiviral_compounds.csv"
BIOACTIVITY_FILE = "Viroai_DataBase/clinical/bioactivity_reference.csv"
OUTPUT_DIR = "Viroai_DataBase/processed"

# Train/Val/Test split ratios (70-20-10 model)
TRAIN_RATIO = 0.70
VAL_RATIO = 0.20
TEST_RATIO = 0.10

# Random seed for reproducibility
RANDOM_SEED = 42

# === SMILES VALIDATION ===
def validate_smiles(smiles):
    """
    Validate SMILES string using RDKit.
    Returns True if valid, False otherwise.
    """
    if not RDKIT_AVAILABLE or pd.isna(smiles) or smiles == '':
        return False
    
    try:
        mol = Chem.MolFromSmiles(smiles)
        return mol is not None
    except:
        return False

def generate_morgan_fingerprint(smiles, radius=2, nBits=2048):
    """
    Generate Morgan fingerprint (ECFP4) for a molecule.
    Returns fingerprint as bit vector or None if invalid.
    """
    if not RDKIT_AVAILABLE:
        return None
    
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        
        # Generate Morgan fingerprint (ECFP4: radius=2, 2048 bits)
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=radius, nBits=nBits)
        return np.array(fp)
    except:
        return None

# === DATA LOADING ===
def load_datasets():
    """Load all datasets with error handling."""
    print("\n" + "="*70)
    print("LOADING DATASETS")
    print("="*70)
    
    datasets = {}
    
    # Load drugs
    try:
        drugs = pd.read_csv(DRUGS_FILE)
        print(f"[OK] Loaded {len(drugs)} compounds from {DRUGS_FILE}")
        datasets['drugs'] = drugs
    except Exception as e:
        print(f"[ERROR] Failed to load drugs: {e}")
        return None
    
    # Load bioactivity
    try:
        bioactivity = pd.read_csv(BIOACTIVITY_FILE)
        print(f"[OK] Loaded {len(bioactivity)} bioactivity pairs from {BIOACTIVITY_FILE}")
        datasets['bioactivity'] = bioactivity
    except Exception as e:
        print(f"[ERROR] Failed to load bioactivity: {e}")
        return None
    
    return datasets

# === DATA CLEANING ===
def clean_drug_data(df):
    """Clean and validate drug compound data."""
    print("\n[CLEAN] Processing drug data...")
    initial_count = len(df)
    
    # 1. Remove duplicates
    df = df.drop_duplicates(subset=['drug_id'], keep='first')
    print(f"  [OK] Removed {initial_count - len(df)} duplicate drugs")
    
    # 2. Check for missing critical fields
    missing_smiles = df['smiles'].isna().sum()
    missing_weight = df['mol_weight'].isna().sum()
    print(f"  [INFO] Missing SMILES: {missing_smiles}/{len(df)}")
    print(f"  [INFO] Missing molecular weight: {missing_weight}/{len(df)}")
    
    # 3. Validate SMILES if RDKit available
    if RDKIT_AVAILABLE and missing_smiles < len(df):
        print(f"  [VALIDATE] Checking SMILES validity...")
        df['smiles_valid'] = df['smiles'].apply(validate_smiles)
        invalid_count = (~df['smiles_valid']).sum()
        print(f"  [OK] Valid SMILES: {(df['smiles_valid']).sum()}/{len(df)}")
        
        if invalid_count > 0:
            print(f"  [WARNING] {invalid_count} compounds have invalid SMILES")
            # Keep invalid for now, will handle in model
    else:
        df['smiles_valid'] = True  # Assume valid if can't check
    
    # 4. Fill missing logP with median
    if df['logP'].isna().any():
        median_logP = df['logP'].median()
        df['logP'].fillna(median_logP, inplace=True)
        print(f"  [OK] Filled missing logP with median: {median_logP:.2f}")
    
    return df

def clean_bioactivity_data(df):
    """Clean and normalize bioactivity reference data."""
    print("\n[CLEAN] Processing bioactivity data...")
    initial_count = len(df)
    
    # 1. Remove duplicates (same drug-protein pair)
    df = df.drop_duplicates(subset=['drug_id', 'protein'], keep='first')
    print(f"  [OK] Removed {initial_count - len(df)} duplicate pairs")
    
    # 2. Remove entries with missing IC50
    df = df[df['ic50_nm'].notna()]
    print(f"  [OK] {len(df)} pairs with valid IC50 values")
    
    # 3. Convert IC50 to log scale (pIC50 = -log10(IC50 in M))
    # IC50 in nM -> convert to M -> take -log10
    df['pic50'] = -np.log10(df['ic50_nm'] * 1e-9)
    print(f"  [OK] Converted IC50 to pIC50 scale")
    print(f"       pIC50 range: {df['pic50'].min():.2f} - {df['pic50'].max():.2f}")
    
    # 4. Add binding class (strong/medium/weak binder)
    # pIC50 > 7 (IC50 < 100 nM) = strong
    # pIC50 5-7 (IC50 100nM - 10uM) = medium
    # pIC50 < 5 (IC50 > 10 uM) = weak
    df['binding_class'] = pd.cut(df['pic50'], 
                                   bins=[0, 5, 7, 15], 
                                   labels=['weak', 'medium', 'strong'])
    print(f"  [OK] Added binding classification")
    print(f"       Strong binders: {(df['binding_class']=='strong').sum()}")
    print(f"       Medium binders: {(df['binding_class']=='medium').sum()}")
    print(f"       Weak binders: {(df['binding_class']=='weak').sum()}")
    
    return df

# === DATA MERGING ===
def merge_datasets(drugs, bioactivity):
    """Merge drug properties with bioactivity measurements."""
    print("\n[MERGE] Combining datasets...")
    
    # Merge on drug_id
    merged = bioactivity.merge(
        drugs[['drug_id', 'smiles', 'mol_weight', 'logP', 'molecular_formula', 'smiles_valid']],
        on='drug_id',
        how='left'
    )
    
    print(f"  [OK] Merged dataset: {len(merged)} records")
    print(f"  [INFO] Columns: {list(merged.columns)}")
    
    # Check merge quality
    missing_smiles = merged['smiles'].isna().sum()
    if missing_smiles > 0:
        print(f"  [WARNING] {missing_smiles} records missing SMILES after merge")
    
    return merged

# === FEATURE ENGINEERING ===
def generate_features(df):
    """Generate molecular fingerprints and additional features."""
    print("\n[FEATURES] Generating molecular features...")
    
    if not RDKIT_AVAILABLE:
        print("  [SKIP] RDKit not available - will generate features during model training")
        return df
    
    # Generate Morgan fingerprints
    print(f"  [COMPUTE] Generating Morgan fingerprints (2048-bit)...")
    fingerprints = []
    valid_count = 0
    
    for idx, row in df.iterrows():
        fp = generate_morgan_fingerprint(row['smiles'])
        if fp is not None:
            fingerprints.append(fp)
            valid_count += 1
        else:
            fingerprints.append(np.zeros(2048))  # Zero vector for invalid
    
    print(f"  [OK] Generated {valid_count}/{len(df)} valid fingerprints")
    
    # Save fingerprints separately (binary format)
    fp_array = np.array(fingerprints)
    fp_file = os.path.join(OUTPUT_DIR, "drug_fingerprints.npy")
    np.save(fp_file, fp_array)
    print(f"  [SAVED] Fingerprints: {fp_file}")
    
    return df

# === TRAIN/VAL/TEST SPLIT ===
def create_splits(df):
    """Create stratified train/validation/test splits."""
    print("\n[SPLIT] Creating train/validation/test sets...")
    
    # Stratify by virus to ensure balanced representation
    np.random.seed(RANDOM_SEED)
    
    train_list = []
    val_list = []
    test_list = []
    
    # Split within each virus group
    for virus in df['virus'].unique():
        virus_data = df[df['virus'] == virus].copy()
        n = len(virus_data)
        
        # Shuffle
        virus_data = virus_data.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
        
        # Calculate split indices
        train_end = int(n * TRAIN_RATIO)
        val_end = train_end + int(n * VAL_RATIO)
        
        train_list.append(virus_data.iloc[:train_end])
        val_list.append(virus_data.iloc[train_end:val_end])
        test_list.append(virus_data.iloc[val_end:])
        
        print(f"  {virus}: {len(train_list[-1])} train, {len(val_list[-1])} val, {len(test_list[-1])} test")
    
    # Combine all viruses
    train_df = pd.concat(train_list, ignore_index=True)
    val_df = pd.concat(val_list, ignore_index=True)
    test_df = pd.concat(test_list, ignore_index=True)
    
    print(f"\n[OK] Total splits:")
    print(f"     Train: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"     Val:   {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
    print(f"     Test:  {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")
    
    return train_df, val_df, test_df

# === SAVE PROCESSED DATA ===
def save_datasets(train_df, val_df, test_df):
    """Save processed datasets to CSV files."""
    print("\n[SAVE] Writing processed datasets...")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Save splits
    train_file = os.path.join(OUTPUT_DIR, "train_data.csv")
    val_file = os.path.join(OUTPUT_DIR, "validation_data.csv")
    test_file = os.path.join(OUTPUT_DIR, "test_data.csv")
    
    train_df.to_csv(train_file, index=False)
    val_df.to_csv(val_file, index=False)
    test_df.to_csv(test_file, index=False)
    
    print(f"  [OK] {train_file}")
    print(f"  [OK] {val_file}")
    print(f"  [OK] {test_file}")
    
    # Generate dataset statistics
    stats = {
        'generation_date': datetime.now().isoformat(),
        'total_samples': len(train_df) + len(val_df) + len(test_df),
        'train_samples': len(train_df),
        'val_samples': len(val_df),
        'test_samples': len(test_df),
        'num_viruses': train_df['virus'].nunique(),
        'num_unique_drugs': train_df['drug_id'].nunique(),
        'ic50_range_nm': {
            'min': float(train_df['ic50_nm'].min()),
            'max': float(train_df['ic50_nm'].max()),
            'median': float(train_df['ic50_nm'].median())
        },
        'pic50_range': {
            'min': float(train_df['pic50'].min()),
            'max': float(train_df['pic50'].max()),
            'mean': float(train_df['pic50'].mean())
        },
        'virus_distribution': train_df['virus'].value_counts().to_dict(),
        'binding_class_distribution': train_df['binding_class'].value_counts().to_dict(),
        'rdkit_available': RDKIT_AVAILABLE
    }
    
    stats_file = os.path.join(OUTPUT_DIR, "dataset_statistics.json")
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"  [OK] {stats_file}")
    
    return stats

# === MAIN PIPELINE ===
def main():
    print("\n" + "="*70)
    print("VIRO-AI DATA CLEANING & PREPARATION PIPELINE")
    print("="*70)
    
    # Step 1: Load datasets
    datasets = load_datasets()
    if datasets is None:
        print("[ERROR] Failed to load datasets!")
        return False
    
    drugs = datasets['drugs']
    bioactivity = datasets['bioactivity']
    
    # Step 2: Clean individual datasets
    drugs_clean = clean_drug_data(drugs)
    bioactivity_clean = clean_bioactivity_data(bioactivity)
    
    # Step 3: Merge datasets
    merged_data = merge_datasets(drugs_clean, bioactivity_clean)
    
    # Step 4: Remove rows with missing SMILES (can't train without molecular structure)
    initial_len = len(merged_data)
    merged_data = merged_data[merged_data['smiles'].notna() & (merged_data['smiles'] != '')]
    print(f"\n[FILTER] Removed {initial_len - len(merged_data)} records with missing SMILES")
    print(f"[OK] Final dataset: {len(merged_data)} training samples")
    
    if len(merged_data) < 10:
        print("[ERROR] Too few samples after cleaning! Need at least 10 samples.")
        return False
    
    # Step 5: Generate features
    merged_data = generate_features(merged_data)
    
    # Step 6: Create train/val/test splits
    train_df, val_df, test_df = create_splits(merged_data)
    
    # Step 7: Save processed data
    stats = save_datasets(train_df, val_df, test_df)
    
    # Step 8: Display summary
    print("\n" + "="*70)
    print("DATA PREPARATION COMPLETE!")
    print("="*70)
    print(f"\nDataset Statistics:")
    print(f"  Total samples: {stats['total_samples']}")
    print(f"  Train: {stats['train_samples']} ({stats['train_samples']/stats['total_samples']*100:.1f}%)")
    print(f"  Val: {stats['val_samples']} ({stats['val_samples']/stats['total_samples']*100:.1f}%)")
    print(f"  Test: {stats['test_samples']} ({stats['test_samples']/stats['total_samples']*100:.1f}%)")
    print(f"\n  Unique drugs: {stats['num_unique_drugs']}")
    print(f"  Viruses: {stats['num_viruses']}")
    print(f"\n  IC50 range: {stats['ic50_range_nm']['min']:.2f} - {stats['ic50_range_nm']['max']:.2f} nM")
    print(f"  pIC50 range: {stats['pic50_range']['min']:.2f} - {stats['pic50_range']['max']:.2f}")
    print(f"\n  Virus distribution:")
    for virus, count in stats['virus_distribution'].items():
        print(f"    {virus}: {count}")
    
    print("\n[SUCCESS] Ready for model training!")
    print(f"[LOCATION] {OUTPUT_DIR}")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n[OK] Pipeline executed successfully!")
    else:
        print("\n[ERROR] Pipeline failed!")

