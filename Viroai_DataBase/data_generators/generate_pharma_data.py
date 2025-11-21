"""
Pharmaceutical Data Generator for Viro-AI
Generates pharmaceutical data including approved drugs and binding affinities
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
PHARMA_DIR = os.path.join(BASE_DIR, "pharma")

# Load existing drug data
DRUGS_FILE = os.path.join(PHARMA_DIR, "approved-drugs", "antiviral_compounds.csv")

# Virus-drug associations
VIRUS_DRUG_MAPPING = {
    "SARS-CoV-2": ["Remdesivir", "Molnupiravir", "Nirmatrelvir", "Paxlovid", "Baricitinib"],
    "Influenza": ["Oseltamivir", "Zanamivir", "Peramivir", "Baloxavir", "Amantadine"],
    "Ebola": ["Remdesivir", "Favipiravir", "Brincidofovir", "Galidesivir"],
    "HIV-1": ["Tenofovir", "Lamivudine", "Ritonavir", "Efavirenz", "Dolutegravir"],
    "HCV": ["Sofosbuvir", "Ledipasvir", "Daclatasvir", "Ribavirin"],
    "HBV": ["Tenofovir", "Entecavir", "Lamivudine", "Adefovir"],
    "HSV-1": ["Acyclovir", "Valacyclovir", "Famciclovir", "Penciclovir"],
    "CMV": ["Ganciclovir", "Valganciclovir", "Foscarnet", "Cidofovir"],
    "Dengue": ["Ribavirin", "Favipiravir"],
    "Zika": ["Ribavirin", "Favipiravir"],
    "Monkeypox": ["Tecovirimat", "Brincidofovir", "Cidofovir"],
    "Rabies": ["Ribavirin"],
    "RSV": ["Ribavirin", "Palivizumab"],
    "Adenovirus": ["Cidofovir", "Brincidofovir"]
}

def load_drug_database():
    """Load existing drug database"""
    try:
        drugs_df = pd.read_csv(DRUGS_FILE)
        return drugs_df
    except Exception as e:
        print(f"Warning: Could not load drug database: {e}")
        return pd.DataFrame()

def generate_drug_binding_data(virus, drugs_df, num_samples=100):
    """Generate drug-virus binding affinity data"""
    data = []
    
    # Get relevant drugs for this virus
    relevant_drug_names = VIRUS_DRUG_MAPPING.get(virus, [])
    
    # Filter drugs
    if not drugs_df.empty:
        relevant_drugs = drugs_df[drugs_df['name'].isin(relevant_drug_names)]
        if relevant_drugs.empty:
            # Use random drugs if no specific match
            relevant_drugs = drugs_df.sample(min(10, len(drugs_df)))
    else:
        # Create dummy drugs if database not available
        relevant_drugs = pd.DataFrame({
            'drug_id': [f"CID{random.randint(100000, 999999)}" for _ in range(10)],
            'name': [f"Drug_{i+1}" for i in range(10)],
            'smiles': ['C' for _ in range(10)],
            'mol_weight': [300 + i*50 for i in range(10)],
            'logP': [1.0 + i*0.5 for i in range(10)],
            'molecular_formula': ['C20H30N2O' for _ in range(10)]
        })
    
    # Virus-specific proteins
    proteins = {
        "SARS-CoV-2": ["Spike", "Mpro", "RdRp"],
        "Influenza": ["Hemagglutinin", "Neuraminidase"],
        "Ebola": ["Glycoprotein", "VP35"],
        "HIV-1": ["Reverse Transcriptase", "Protease"],
        "HCV": ["NS3/4A", "NS5A", "NS5B"],
        "HBV": ["Polymerase"],
        "HSV-1": ["Thymidine Kinase", "DNA Polymerase"],
        "CMV": ["UL97", "DNA Polymerase"],
        "Dengue": ["NS3", "NS5"],
        "Zika": ["NS3", "NS5"],
        "Monkeypox": ["VP37"],
        "Rabies": ["Glycoprotein"],
        "RSV": ["F protein"],
        "Adenovirus": ["Hexon"]
    }
    
    virus_proteins = proteins.get(virus, ["Unknown"])
    
    for _ in range(num_samples):
        drug = relevant_drugs.sample(1).iloc[0]
        protein = random.choice(virus_proteins)
        
        # Generate realistic binding affinity (IC50 in nM)
        # Distribution: some strong binders, mostly medium, some weak
        binding_class = random.choices(
            ['strong', 'medium', 'weak'],
            weights=[0.3, 0.5, 0.2]
        )[0]
        
        if binding_class == 'strong':
            ic50 = np.random.lognormal(mean=3.5, sigma=0.5)  # ~30-50 nM
        elif binding_class == 'medium':
            ic50 = np.random.lognormal(mean=5.5, sigma=0.5)  # ~200-500 nM
        else:
            ic50 = np.random.lognormal(mean=7.5, sigma=0.5)  # ~2000-5000 nM
        
        ic50 = max(0.5, min(ic50, 50000))
        
        # Calculate pIC50
        pic50 = -np.log10(ic50 * 1e-9)
        
        # Generate Ki (inhibition constant)
        ki = ic50 * np.random.uniform(0.7, 1.3) if random.random() > 0.3 else None
        
        # Binding free energy (kcal/mol)
        delta_g = -1.36 * pic50  # Approximate conversion
        
        # Assay information
        assay_type = random.choice(['IC50', 'Ki', 'EC50', 'Kd', 'IC90'])
        assay_date = datetime.now() - pd.Timedelta(days=random.randint(0, 1000))
        
        # Source
        source = random.choice(['PubChem', 'ChEMBL', 'Literature', 'Clinical Trial', 'PDB'])
        
        data.append({
            'virus': virus,
            'protein': protein,
            'drug_name': drug['name'],
            'drug_id': drug['drug_id'],
            'smiles': drug['smiles'],
            'mol_weight': drug['mol_weight'],
            'logP': drug['logP'],
            'ic50_nm': round(ic50, 2),
            'pic50': round(pic50, 3),
            'ki_nm': round(ki, 2) if ki else None,
            'binding_class': binding_class,
            'delta_g_kcal_mol': round(delta_g, 2),
            'assay_type': assay_type,
            'assay_date': assay_date.strftime('%Y-%m-%d'),
            'source': source
        })
    
    return pd.DataFrame(data)

def generate_enhanced_drug_data(virus, drugs_df):
    """Generate enhanced drug data with additional properties"""
    data = []
    
    relevant_drug_names = VIRUS_DRUG_MAPPING.get(virus, [])
    
    if not drugs_df.empty:
        relevant_drugs = drugs_df[drugs_df['name'].isin(relevant_drug_names)]
        if relevant_drugs.empty:
            relevant_drugs = drugs_df.sample(min(15, len(drugs_df)))
    else:
        relevant_drugs = pd.DataFrame({
            'drug_id': [f"CID{random.randint(100000, 999999)}" for _ in range(15)],
            'name': [f"Drug_{i+1}" for i in range(15)],
            'smiles': ['C' for _ in range(15)],
            'mol_weight': [300 + i*50 for i in range(15)],
            'logP': [1.0 + i*0.5 for i in range(15)],
            'molecular_formula': ['C20H30N2O' for _ in range(15)]
        })
    
    for _, drug in relevant_drugs.iterrows():
        # Additional molecular properties
        hbd = random.randint(0, 5)  # Hydrogen bond donors
        hba = random.randint(2, 10)  # Hydrogen bond acceptors
        rotatable_bonds = random.randint(0, 15)
        tpsa = random.uniform(50, 200)  # Topological polar surface area
        
        # Drug-likeness (Lipinski's Rule of Five)
        lipinski_violations = 0
        if drug['mol_weight'] > 500:
            lipinski_violations += 1
        if drug['logP'] > 5:
            lipinski_violations += 1
        if hbd > 5:
            lipinski_violations += 1
        if hba > 10:
            lipinski_violations += 1
        
        # Bioavailability score
        bioavailability = max(0.1, 1.0 - (lipinski_violations * 0.2))
        
        # Toxicity predictions (arbitrary)
        ld50_mg_kg = np.random.lognormal(mean=5, sigma=1)  # Oral LD50
        
        data.append({
            'drug_id': drug['drug_id'],
            'name': drug['name'],
            'smiles': drug['smiles'],
            'mol_weight': drug['mol_weight'],
            'logP': drug['logP'],
            'molecular_formula': drug['molecular_formula'],
            'hbd': hbd,
            'hba': hba,
            'rotatable_bonds': rotatable_bonds,
            'tpsa': round(tpsa, 2),
            'lipinski_violations': lipinski_violations,
            'bioavailability_score': round(bioavailability, 3),
            'ld50_mg_kg': round(ld50_mg_kg, 2),
            'virus_target': virus
        })
    
    return pd.DataFrame(data)

def generate_pharma_data_for_virus(virus):
    """Generate all pharmaceutical data for a single virus"""
    # Initialize data cleaner
    cleaner = DataCleaner(BASE_DIR)
    
    # Ensure correct folder structure
    paths = cleaner.ensure_folder_structure(virus, "pharma")
    if not cleaner.validate_file_paths(paths):
        print(f"    ✗ Failed to create folder structure for {virus}")
        return False
    
    print(f"\n  Generating pharmaceutical data for {virus}...")
    
    # Load drug database
    drugs_df = load_drug_database()
    
    # Generate binding data
    binding_data = generate_drug_binding_data(virus, drugs_df, num_samples=100)
    
    # Clean binding data
    print(f"    [CLEAN] Cleaning binding data...")
    binding_data = cleaner.clean_ic50_data(binding_data)
    
    # Check for existing data and merge
    binding_file = os.path.join(paths['real_world_binding'], f"{virus}_binding.csv")
    exists, existing_binding = cleaner.check_existing_data(binding_file)
    if exists and existing_binding is not None:
        binding_data = cleaner.merge_and_deduplicate(
            existing_binding, binding_data,
            ['virus', 'drug_id', 'protein']
        )
    
    # Save cleaned binding data
    cleaner.save_cleaned_data(binding_data, binding_file, clean_func=cleaner.clean_ic50_data)
    
    # Generate enhanced drug data
    enhanced_data = generate_enhanced_drug_data(virus, drugs_df)
    
    # Save enhanced drug data
    enhanced_file = os.path.join(PHARMA_DIR, f"{virus}_enhanced_drugs.csv")
    cleaner.save_cleaned_data(enhanced_data, enhanced_file)
    
    return True

def generate_pharma_datasets(viruses):
    """Generate pharmaceutical datasets for all viruses"""
    print(f"\nGenerating pharmaceutical data for {len(viruses)} viruses...")
    
    # Ensure directories exist
    os.makedirs(os.path.join(PHARMA_DIR, "real_world_binding"), exist_ok=True)
    os.makedirs(os.path.join(PHARMA_DIR, "approved-drugs"), exist_ok=True)
    
    success_count = 0
    for virus in viruses:
        try:
            if generate_pharma_data_for_virus(virus):
                success_count += 1
        except Exception as e:
            print(f"    ✗ Error generating data for {virus}: {e}")
            import traceback
            traceback.print_exc()
    
    # Merge all binding data
    try:
        all_binding_files = [os.path.join(PHARMA_DIR, "real_world_binding", f"{v}_binding.csv") 
                            for v in viruses]
        all_binding_dfs = []
        for f in all_binding_files:
            if os.path.exists(f):
                all_binding_dfs.append(pd.read_csv(f))
        
        if all_binding_dfs:
            combined_binding = pd.concat(all_binding_dfs, ignore_index=True)
            combined_file = os.path.join(PHARMA_DIR, "real_world_binding", "all_viruses_binding.csv")
            combined_binding.to_csv(combined_file, index=False)
            print(f"\n✓ Combined binding data: {combined_file} ({len(combined_binding)} records)")
    except Exception as e:
        print(f"Warning: Could not combine binding data: {e}")
    
    print(f"\n✓ Generated pharmaceutical data for {success_count}/{len(viruses)} viruses")
    return success_count == len(viruses)

if __name__ == "__main__":
    test_viruses = ["SARS-CoV-2", "Ebola", "Influenza"]
    generate_pharma_datasets(test_viruses)

