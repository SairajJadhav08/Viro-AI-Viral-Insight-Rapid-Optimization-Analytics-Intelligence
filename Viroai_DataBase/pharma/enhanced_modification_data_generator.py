"""
Enhanced Chemical Modification Data Generator
Creates comprehensive training data for chemical modifications
"""

import pandas as pd
import numpy as np
import os

def generate_enhanced_modification_data():
    """Generate enhanced modification training data with realistic property changes"""
    
    # Load base drugs
    base_path = "Viroai_DataBase/pharma/approved-drugs/antiviral_compounds.csv"
    if os.path.exists(base_path):
        base_drugs = pd.read_csv(base_path)
    else:
        base_drugs = pd.DataFrame({
            'name': ['Remdesivir', 'Molnupiravir'],
            'smiles': [
                'CCC(CC)COC(=O)C(C)NP(=O)(OCC1C(C(C(O1)(C#N)C2=CC=C3N2N=CN=C3N)O)O)OC4=CC=CC=C4',
                'CC(C)C(=O)OCC1C(C(C(O1)N2C=CC(=NC2=O)NO)O)O'
            ],
            'mol_weight': [602.6, 329.31],
            'logP': [1.9, -0.8]
        })
    
    np.random.seed(42)
    n_samples = 400
    
    modification_types = ['Fluorination', 'Methylation', 'Hydroxylation', 'Chlorination']
    
    data = []
    
    samples_per_combination = max(1, n_samples // (len(base_drugs) * len(modification_types)))
    
    for idx, drug in base_drugs.iterrows():
        base_mw = drug.get('mol_weight', 400)
        base_logp = drug.get('logP', 2.0)
        base_smiles = drug.get('smiles', '')
        
        for mod_type in modification_types:
            for i in range(samples_per_combination):
                # Calculate base properties
                c_count = base_smiles.count('C')
                n_count = base_smiles.count('N')
                o_count = base_smiles.count('O')
                rings = base_smiles.count('1') + base_smiles.count('2')
                
                # Modification-specific changes
                if mod_type == 'Fluorination':
                    mw_change = 18.0  # H to F
                    logp_change = 0.3 + np.random.uniform(-0.1, 0.1)
                    delta_be = -1.0 - np.random.uniform(0, 0.5)  # Improved binding
                    delta_rmsd = 0.2 + np.random.uniform(-0.1, 0.1)
                    delta_solubility = -0.2 + np.random.uniform(-0.1, 0.1)
                    metabolic_stability = 20 + np.random.uniform(-5, 10)
                    absorption_change = 6 + np.random.uniform(-3, 5)
                    clearance_change = -10 + np.random.uniform(-5, 5)
                    sas_score = 2.5 + np.random.uniform(-0.5, 0.5)
                    structural_score = 85 + np.random.uniform(-5, 10)
                    binding_score = 88 + np.random.uniform(-5, 10)
                    overall_viability = 88 + np.random.uniform(-5, 10)
                    
                elif mod_type == 'Methylation':
                    mw_change = 14.0  # H to CH3
                    logp_change = 0.5 + np.random.uniform(-0.1, 0.1)
                    delta_be = -0.6 - np.random.uniform(0, 0.4)
                    delta_rmsd = 0.3 + np.random.uniform(-0.1, 0.1)
                    delta_solubility = -0.1 + np.random.uniform(-0.1, 0.1)
                    metabolic_stability = 10 + np.random.uniform(-5, 8)
                    absorption_change = 4 + np.random.uniform(-2, 4)
                    clearance_change = -8 + np.random.uniform(-4, 4)
                    sas_score = 2.2 + np.random.uniform(-0.4, 0.4)
                    structural_score = 80 + np.random.uniform(-8, 12)
                    binding_score = 82 + np.random.uniform(-8, 12)
                    overall_viability = 82 + np.random.uniform(-8, 12)
                    
                elif mod_type == 'Hydroxylation':
                    mw_change = 16.0  # H to OH
                    logp_change = -0.2 + np.random.uniform(-0.1, 0.1)
                    delta_be = -0.5 - np.random.uniform(0, 0.3)
                    delta_rmsd = 0.25 + np.random.uniform(-0.1, 0.1)
                    delta_solubility = 0.3 + np.random.uniform(-0.1, 0.1)
                    metabolic_stability = 5 + np.random.uniform(-3, 8)
                    absorption_change = 2 + np.random.uniform(-2, 3)
                    clearance_change = -5 + np.random.uniform(-3, 3)
                    sas_score = 2.8 + np.random.uniform(-0.5, 0.5)
                    structural_score = 75 + np.random.uniform(-10, 15)
                    binding_score = 78 + np.random.uniform(-10, 15)
                    overall_viability = 75 + np.random.uniform(-10, 15)
                    
                else:  # Chlorination
                    mw_change = 34.5  # H to Cl
                    logp_change = 0.7 + np.random.uniform(-0.1, 0.1)
                    delta_be = -0.8 - np.random.uniform(0, 0.4)
                    delta_rmsd = 0.3 + np.random.uniform(-0.1, 0.1)
                    delta_solubility = -0.2 + np.random.uniform(-0.1, 0.1)
                    metabolic_stability = 15 + np.random.uniform(-5, 10)
                    absorption_change = 5 + np.random.uniform(-3, 5)
                    clearance_change = -9 + np.random.uniform(-5, 5)
                    sas_score = 2.8 + np.random.uniform(-0.5, 0.5)
                    structural_score = 82 + np.random.uniform(-8, 12)
                    binding_score = 85 + np.random.uniform(-8, 12)
                    overall_viability = 85 + np.random.uniform(-8, 12)
                
                data.append({
                    'base_compound': drug.get('name', 'Compound'),
                    'base_smiles': base_smiles,
                    'base_mw': base_mw,
                    'base_logp': base_logp,
                    'modification_type': mod_type,
                    'mw_change': mw_change,
                    'logp_change': logp_change,
                    'delta_be': delta_be,
                    'delta_rmsd': delta_rmsd,
                    'delta_solubility': delta_solubility,
                    'metabolic_stability': metabolic_stability,
                    'absorption_change': absorption_change,
                    'clearance_change': clearance_change,
                    'sas_score': sas_score,
                    'structural_score': structural_score,
                    'binding_score': binding_score,
                    'overall_viability': overall_viability
                })
    
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    print("Generating enhanced modification training data...")
    df = generate_enhanced_modification_data()
    
    # Save to proper location
    output_path = "Viroai_DataBase/pharma/enhanced_modification_training_data.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"\nGenerated {len(df)} enhanced modification samples")
    if len(df) > 0:
        print(f"Columns: {list(df.columns)}")
        print(f"\nSample statistics:")
        print(df[['mw_change', 'logp_change', 'delta_be', 'metabolic_stability', 'overall_viability']].describe())
    else:
        print("Warning: No data generated!")

