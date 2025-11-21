"""
Enhanced Drug Data Generator
Creates comprehensive training data with ADME and toxicity properties
"""

import pandas as pd
import numpy as np
import os

def generate_enhanced_drug_data():
    """Generate enhanced drug training data with realistic ADME and toxicity properties"""
    
    # Load existing drug data
    base_path = "Viroai_DataBase/pharma/approved-drugs/antiviral_compounds.csv"
    if os.path.exists(base_path):
        base_drugs = pd.read_csv(base_path)
    else:
        # Create base drugs if file doesn't exist
        base_drugs = pd.DataFrame({
            'name': ['Remdesivir', 'Molnupiravir', 'Nirmatrelvir'],
            'smiles': [
                'CCC(CC)COC(=O)C(C)NP(=O)(OCC1C(C(C(O1)(C#N)C2=CC=C3N2N=CN=C3N)O)O)OC4=CC=CC=C4',
                'CC(C)C(=O)OCC1C(C(C(O1)N2C=CC(=NC2=O)NO)O)O',
                'CC1(C2C1C(N(C2)C(=O)C(C(C)(C)C)NC(=O)C(F)(F)F)C(=O)NC(CC3CCNC3=O)C#N)C'
            ],
            'mol_weight': [602.6, 329.31, 499.5],
            'logP': [1.9, -0.8, 2.2]
        })
    
    np.random.seed(42)
    n_samples = 500  # Generate 500 samples
    
    data = []
    
    for idx, drug in base_drugs.iterrows():
        base_mw = drug.get('mol_weight', 400)
        base_logp = drug.get('logP', 2.0)
        smiles = drug.get('smiles', '')
        
        # Generate multiple variations
        for i in range(n_samples // len(base_drugs)):
            # Calculate molecular features from SMILES
            c_count = smiles.count('C')
            n_count = smiles.count('N')
            o_count = smiles.count('O')
            rings = smiles.count('1') + smiles.count('2')
            aromatic = 1 if ('c' in smiles or 'C' in smiles) else 0
            heavy_atoms = c_count + n_count + o_count
            
            # Generate realistic binding properties (correlated with structure)
            binding_energy = -7.5 - (heavy_atoms / 50) - np.random.uniform(0, 1.5)
            kd = 0.5 + (base_logp / 3) + np.random.uniform(0, 1.5)
            ic50 = 10 + (base_mw / 50) + np.random.uniform(0, 40)
            docking_score = binding_energy - 1.0 + np.random.uniform(-0.3, 0.3)
            
            # ADME properties (correlated with molecular properties)
            # Absorption: higher for lower MW, moderate logP
            absorption = 85 - (base_mw / 10) + (base_logp * 2) + np.random.uniform(-10, 10)
            absorption = np.clip(absorption, 20, 100)
            
            # Plasma protein binding: higher for higher logP
            ppb = 50 + (base_logp * 8) + np.random.uniform(-15, 15)
            ppb = np.clip(ppb, 10, 99)
            
            # Clearance: lower for higher MW, higher logP
            clearance = 20 - (base_mw / 30) - (base_logp * 2) + np.random.uniform(-5, 5)
            clearance = np.clip(clearance, 1, 30)
            
            # Half-life: higher for higher MW, higher logP
            half_life = 2 + (base_mw / 100) + (base_logp * 1.5) + np.random.uniform(-2, 5)
            half_life = np.clip(half_life, 0.5, 24)
            
            # Toxicity (Ames test - lower is better, typically 0-0.3)
            ames_score = 0.05 + (rings / 20) + np.random.uniform(0, 0.2)
            ames_score = np.clip(ames_score, 0, 0.5)
            
            # hERG IC50 (higher is better, typically >10 μM)
            herg_ic50 = 15 + (base_mw / 40) + np.random.uniform(-5, 10)
            herg_ic50 = np.clip(herg_ic50, 5, 50)
            
            # Stability (RMSD - lower is better)
            rmsd = 0.8 + (rings / 10) + np.random.uniform(0, 1.2)
            rmsd = np.clip(rmsd, 0.3, 3.0)
            
            # MM-PBSA (more negative is better)
            mm_pbsa = -35 - (heavy_atoms / 5) + np.random.uniform(-10, 10)
            mm_pbsa = np.clip(mm_pbsa, -60, -10)
            
            # Overall score (weighted combination)
            binding_score = (abs(binding_energy) / 10) * 30
            adme_score = (absorption / 100) * 25 + ((100 - ppb) / 100) * 15
            tox_score = ((1 - ames_score) * 20) + ((herg_ic50 / 50) * 10)
            overall_score = binding_score + adme_score + tox_score + np.random.uniform(-5, 5)
            overall_score = np.clip(overall_score, 0, 100)
            
            data.append({
                'name': f"{drug.get('name', 'Drug')}_{i}",
                'smiles': smiles,
                'mol_weight': base_mw + np.random.uniform(-20, 20),
                'logP': base_logp + np.random.uniform(-0.5, 0.5),
                'c_count': c_count,
                'n_count': n_count,
                'o_count': o_count,
                'rings': rings,
                'aromatic': aromatic,
                'heavy_atoms': heavy_atoms,
                'double_bonds': smiles.count('='),
                'binding_energy': binding_energy,
                'kd': kd,
                'ic50': ic50,
                'docking_score': docking_score,
                'absorption': absorption,
                'ppb': ppb,
                'clearance': clearance,
                'half_life': half_life,
                'ames_score': ames_score,
                'herg_ic50': herg_ic50,
                'rmsd': rmsd,
                'mm_pbsa': mm_pbsa,
                'overall_score': overall_score
            })
    
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    print("Generating enhanced drug training data...")
    df = generate_enhanced_drug_data()
    
    # Save to multiple locations
    output_paths = [
        "Viroai_DataBase/pharma/enhanced_drug_training_data.csv",
        "Viroai_DataBase/processed/enhanced_drug_data.csv"
    ]
    
    for path in output_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        print(f"Saved {len(df)} samples to {path}")
    
    print(f"\nGenerated {len(df)} enhanced drug samples")
    print(f"Columns: {list(df.columns)}")
    print(f"\nSample statistics:")
    print(df[['binding_energy', 'absorption', 'ppb', 'clearance', 'half_life', 'ames_score', 'overall_score']].describe())

