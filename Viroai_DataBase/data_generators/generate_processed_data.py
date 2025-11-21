"""
Processed Data Generator for Viro-AI
Generates processed datasets with 70-20-10 train-validation-test splits
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import random
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_cleaner import DataCleaner

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")
CLINICAL_DIR = os.path.join(BASE_DIR, "clinical")
PHARMA_DIR = os.path.join(BASE_DIR, "pharma")

# 70-20-10 split ratios
TRAIN_RATIO = 0.70
VAL_RATIO = 0.20
TEST_RATIO = 0.10

def load_clinical_binding_data(virus):
    """Load binding efficacy data from clinical folder"""
    binding_file = os.path.join(CLINICAL_DIR, virus, "treatments", "binding_efficacy.csv")
    if os.path.exists(binding_file):
        return pd.read_csv(binding_file)
    return pd.DataFrame()

def load_pharma_binding_data(virus):
    """Load binding data from pharma folder"""
    binding_file = os.path.join(PHARMA_DIR, "real_world_binding", f"{virus}_binding.csv")
    if os.path.exists(binding_file):
        return pd.read_csv(binding_file)
    return pd.DataFrame()

def load_drug_data():
    """Load drug database"""
    drugs_file = os.path.join(PHARMA_DIR, "approved-drugs", "antiviral_compounds.csv")
    if os.path.exists(drugs_file):
        return pd.read_csv(drugs_file)
    return pd.DataFrame()

def merge_and_prepare_data(viruses):
    """Merge all data sources and prepare for ML training"""
    all_data = []
    
    drugs_df = load_drug_data()
    
    for virus in viruses:
        # Load binding data from clinical
        clinical_data = load_clinical_binding_data(virus)
        
        # Load binding data from pharma
        pharma_data = load_pharma_binding_data(virus)
        
        # Combine binding data
        if not clinical_data.empty and not pharma_data.empty:
            # Merge on common columns
            combined = pd.concat([clinical_data, pharma_data], ignore_index=True)
        elif not clinical_data.empty:
            combined = clinical_data
        elif not pharma_data.empty:
            combined = pharma_data
        else:
            # Generate synthetic data if no data exists
            combined = generate_synthetic_binding_data(virus, drugs_df, num_samples=50)
        
        # Add virus column if not present
        if 'virus' not in combined.columns:
            combined['virus'] = virus
        
        # Ensure required columns exist
        required_cols = ['virus', 'drug_id', 'ic50_nm']
        missing_cols = [col for col in required_cols if col not in combined.columns]
        
        if missing_cols:
            print(f"  Warning: {virus} missing columns: {missing_cols}")
            continue
        
        # Calculate pIC50 if not present
        if 'pic50' not in combined.columns and 'ic50_nm' in combined.columns:
            combined['pic50'] = -np.log10(combined['ic50_nm'] * 1e-9)
        
        # Add binding class if not present
        if 'binding_class' not in combined.columns and 'pic50' in combined.columns:
            combined['binding_class'] = pd.cut(
                combined['pic50'],
                bins=[0, 5, 7, 15],
                labels=['weak', 'medium', 'strong']
            )
        
        # Merge with drug properties
        if not drugs_df.empty and 'drug_id' in combined.columns:
            combined = combined.merge(
                drugs_df[['drug_id', 'smiles', 'mol_weight', 'logP', 'molecular_formula']],
                on='drug_id',
                how='left'
            )
        
        all_data.append(combined)
    
    if not all_data:
        print("  Error: No data to process!")
        return pd.DataFrame()
    
    # Combine all viruses
    merged_data = pd.concat(all_data, ignore_index=True)
    
    # Remove rows with missing critical data
    initial_len = len(merged_data)
    merged_data = merged_data[
        merged_data['ic50_nm'].notna() & 
        (merged_data['ic50_nm'] > 0) &
        merged_data['virus'].notna()
    ]
    
    if len(merged_data) < initial_len:
        print(f"  Removed {initial_len - len(merged_data)} rows with missing data")
    
    return merged_data

def generate_synthetic_binding_data(virus, drugs_df, num_samples=50):
    """Generate synthetic binding data if real data is missing"""
    data = []
    
    if drugs_df.empty:
        return pd.DataFrame()
    
    # Sample drugs
    sample_drugs = drugs_df.sample(min(num_samples, len(drugs_df)))
    
    for _, drug in sample_drugs.iterrows():
        # Generate realistic IC50
        ic50 = np.random.lognormal(mean=5, sigma=1)
        ic50 = max(0.5, min(ic50, 50000))
        
        data.append({
            'virus': virus,
            'drug_id': drug['drug_id'],
            'drug_name': drug['name'],
            'protein': 'Unknown',
            'ic50_nm': round(ic50, 2),
            'pic50': round(-np.log10(ic50 * 1e-9), 3)
        })
    
    return pd.DataFrame(data)

def create_stratified_splits(df, train_ratio, val_ratio, test_ratio):
    """Create stratified train/validation/test splits by virus"""
    np.random.seed(42)
    random.seed(42)
    
    train_list = []
    val_list = []
    test_list = []
    
    # Split within each virus group to ensure balanced representation
    for virus in df['virus'].unique():
        virus_data = df[df['virus'] == virus].copy()
        n = len(virus_data)
        
        if n < 3:
            # Too few samples, put all in train
            train_list.append(virus_data)
            continue
        
        # Shuffle
        virus_data = virus_data.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Calculate split indices
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        
        train_list.append(virus_data.iloc[:train_end])
        val_list.append(virus_data.iloc[train_end:val_end])
        test_list.append(virus_data.iloc[val_end:])
    
    # Combine all viruses
    train_df = pd.concat(train_list, ignore_index=True) if train_list else pd.DataFrame()
    val_df = pd.concat(val_list, ignore_index=True) if val_list else pd.DataFrame()
    test_df = pd.concat(test_list, ignore_index=True) if test_list else pd.DataFrame()
    
    return train_df, val_df, test_df

def generate_statistics(train_df, val_df, test_df):
    """Generate dataset statistics"""
    total_samples = len(train_df) + len(val_df) + len(test_df)
    
    if total_samples == 0:
        return {}
    
    stats = {
        'generation_date': datetime.now().isoformat(),
        'total_samples': total_samples,
        'train_samples': len(train_df),
        'val_samples': len(val_df),
        'test_samples': len(test_df),
        'train_ratio': round(len(train_df) / total_samples, 3) if total_samples > 0 else 0,
        'val_ratio': round(len(val_df) / total_samples, 3) if total_samples > 0 else 0,
        'test_ratio': round(len(test_df) / total_samples, 3) if total_samples > 0 else 0,
        'num_viruses': train_df['virus'].nunique() if not train_df.empty else 0,
        'num_unique_drugs': train_df['drug_id'].nunique() if not train_df.empty else 0
    }
    
    if not train_df.empty:
        if 'ic50_nm' in train_df.columns:
            stats['ic50_range_nm'] = {
                'min': float(train_df['ic50_nm'].min()),
                'max': float(train_df['ic50_nm'].max()),
                'median': float(train_df['ic50_nm'].median()),
                'mean': float(train_df['ic50_nm'].mean())
            }
        
        if 'pic50' in train_df.columns:
            stats['pic50_range'] = {
                'min': float(train_df['pic50'].min()),
                'max': float(train_df['pic50'].max()),
                'mean': float(train_df['pic50'].mean()),
                'median': float(train_df['pic50'].median())
            }
        
        if 'virus' in train_df.columns:
            stats['virus_distribution'] = train_df['virus'].value_counts().to_dict()
        
        if 'binding_class' in train_df.columns:
            stats['binding_class_distribution'] = train_df['binding_class'].value_counts().to_dict()
    
    return stats

def generate_processed_datasets(viruses, train_ratio=0.70, val_ratio=0.20, test_ratio=0.10):
    """Generate processed datasets with 70-20-10 splits"""
    # Initialize data cleaner
    cleaner = DataCleaner(BASE_DIR)
    
    # Ensure correct folder structure (processed doesn't need virus parameter)
    paths = {'base': PROCESSED_DIR}
    os.makedirs(paths['base'], exist_ok=True)
    
    print(f"\nGenerating processed data with {int(train_ratio*100)}-{int(val_ratio*100)}-{int(test_ratio*10)} splits...")
    
    # Merge and prepare all data
    print("  Merging data from clinical and pharma sources...")
    merged_data = merge_and_prepare_data(viruses)
    
    if merged_data.empty:
        print("  ✗ No data to process!")
        return False
    
    print(f"  Total merged records: {len(merged_data)}")
    
    # Clean merged data
    print("  [CLEAN] Cleaning merged data...")
    merged_data = cleaner.clean_ic50_data(merged_data)
    
    # Remove duplicates across all columns
    before = len(merged_data)
    merged_data = merged_data.drop_duplicates(keep='first')
    if len(merged_data) < before:
        print(f"  [CLEAN] Removed {before - len(merged_data)} duplicate records")
    
    print(f"  Clean records: {len(merged_data)}")
    print(f"  Unique viruses: {merged_data['virus'].nunique()}")
    print(f"  Unique drugs: {merged_data['drug_id'].nunique()}")
    
    # Create splits
    print("\n  Creating stratified train/validation/test splits...")
    train_df, val_df, test_df = create_stratified_splits(merged_data, train_ratio, val_ratio, test_ratio)
    
    # Clean each split
    train_df = cleaner.clean_ic50_data(train_df)
    val_df = cleaner.clean_ic50_data(val_df)
    test_df = cleaner.clean_ic50_data(test_df)
    
    print(f"    Train: {len(train_df)} ({len(train_df)/len(merged_data)*100:.1f}%)")
    print(f"    Validation: {len(val_df)} ({len(val_df)/len(merged_data)*100:.1f}%)")
    print(f"    Test: {len(test_df)} ({len(test_df)/len(merged_data)*100:.1f}%)")
    
    # Save datasets
    print("\n  Saving processed datasets...")
    train_file = os.path.join(paths['base'], "train_data.csv")
    val_file = os.path.join(paths['base'], "validation_data.csv")
    test_file = os.path.join(paths['base'], "test_data.csv")
    
    cleaner.save_cleaned_data(train_df, train_file, clean_func=cleaner.clean_ic50_data)
    cleaner.save_cleaned_data(val_df, val_file, clean_func=cleaner.clean_ic50_data)
    cleaner.save_cleaned_data(test_df, test_file, clean_func=cleaner.clean_ic50_data)
    
    # Generate and save statistics
    stats = generate_statistics(train_df, val_df, test_df)
    stats_file = os.path.join(paths['base'], "dataset_statistics.json")
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"    ✓ Saved {os.path.basename(stats_file)}")
    
    # Print summary
    print("\n" + "="*70)
    print("DATASET STATISTICS")
    print("="*70)
    print(f"Total samples: {stats['total_samples']}")
    print(f"  Train: {stats['train_samples']} ({stats['train_ratio']*100:.1f}%)")
    print(f"  Validation: {stats['val_samples']} ({stats['val_ratio']*100:.1f}%)")
    print(f"  Test: {stats['test_samples']} ({stats['test_ratio']*100:.1f}%)")
    print(f"\nUnique viruses: {stats['num_viruses']}")
    print(f"Unique drugs: {stats['num_unique_drugs']}")
    
    if 'virus_distribution' in stats:
        print(f"\nVirus distribution:")
        for virus, count in sorted(stats['virus_distribution'].items(), key=lambda x: -x[1])[:10]:
            print(f"  {virus}: {count}")
    
    return True

if __name__ == "__main__":
    test_viruses = ["SARS-CoV-2", "Ebola", "Influenza", "HIV-1", "HCV"]
    generate_processed_datasets(test_viruses, 0.70, 0.20, 0.10)

