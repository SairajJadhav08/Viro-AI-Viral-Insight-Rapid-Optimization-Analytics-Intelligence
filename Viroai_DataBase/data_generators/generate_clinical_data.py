"""
Clinical Data Generator for Viro-AI
Generates clinical data including outcomes, treatments, and metadata for all viruses
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_cleaner import DataCleaner

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLINICAL_DIR = os.path.join(BASE_DIR, "clinical")

# Virus-specific protein targets
VIRUS_PROTEINS = {
    "SARS-CoV-2": ["Spike", "Mpro", "RdRp", "PLpro"],
    "Influenza": ["Hemagglutinin", "Neuraminidase", "M2"],
    "Ebola": ["Glycoprotein", "VP35", "VP40", "NP"],
    "HIV-1": ["Reverse Transcriptase", "Protease", "Integrase", "GP120"],
    "HCV": ["NS3/4A", "NS5A", "NS5B"],
    "HBV": ["Polymerase", "Surface Antigen", "Core"],
    "HSV-1": ["Thymidine Kinase", "DNA Polymerase", "Glycoprotein D"],
    "CMV": ["UL97", "DNA Polymerase", "Glycoprotein B"],
    "Dengue": ["NS3", "NS5", "E protein"],
    "Zika": ["NS3", "NS5", "E protein"],
    "Monkeypox": ["VP37", "DNA Polymerase", "E8L"],
    "Rabies": ["Glycoprotein", "Nucleoprotein", "Phosphoprotein"],
    "RSV": ["F protein", "G protein", "L protein"],
    "Adenovirus": ["Hexon", "Penton", "DNA Polymerase"]
}

# Common antiviral drugs with their properties
ANTIVIRAL_DRUGS = {
    "Remdesivir": {"id": "CID121304016", "targets": ["RdRp", "Polymerase"]},
    "Molnupiravir": {"id": "CID145996610", "targets": ["RdRp", "Polymerase"]},
    "Nirmatrelvir": {"id": "CID155903259", "targets": ["Mpro", "Protease"]},
    "Favipiravir": {"id": "CID492405", "targets": ["RdRp", "Polymerase"]},
    "Ribavirin": {"id": "CID37542", "targets": ["RdRp", "Polymerase"]},
    "Oseltamivir": {"id": "CID65028", "targets": ["Neuraminidase"]},
    "Zanamivir": {"id": "CID60855", "targets": ["Neuraminidase"]},
    "Acyclovir": {"id": "CID2478", "targets": ["Thymidine Kinase", "DNA Polymerase"]},
    "Ganciclovir": {"id": "CID3449", "targets": ["DNA Polymerase", "UL97"]},
    "Tecovirimat": {"id": "CID16118730", "targets": ["VP37"]},
    "Sofosbuvir": {"id": "CID45375808", "targets": ["NS5B"]},
    "Ledipasvir": {"id": "CID67505836", "targets": ["NS5A"]},
    "Tenofovir": {"id": "CID464205", "targets": ["Reverse Transcriptase", "Polymerase"]},
    "Lamivudine": {"id": "CID60825", "targets": ["Reverse Transcriptase"]},
    "Entecavir": {"id": "CID153941", "targets": ["Polymerase"]}
}

# PDB IDs for structures
PDB_IDS = {
    "SARS-CoV-2": {"Spike": "6VXX", "Mpro": "7BNN", "RdRp": "7BV2"},
    "Influenza": {"Hemagglutinin": "1RVX", "Neuraminidase": "4GMS"},
    "Ebola": {"Glycoprotein": "5JQ3", "VP35": "4GH9"},
    "HIV-1": {"Protease": "1HHP", "Reverse Transcriptase": "1RTD"},
    "HCV": {"NS3/4A": "1A1R", "NS5B": "1C2P"},
    "HBV": {"Polymerase": "1QBS"},
    "HSV-1": {"Thymidine Kinase": "1KI2", "DNA Polymerase": "2GV9"},
    "CMV": {"UL97": "4Q0Y", "DNA Polymerase": "1YTS"},
    "Dengue": {"NS3": "2VBC", "E protein": "1K4R"},
    "Zika": {"NS3": "5GJ4", "E protein": "5IRE"},
    "Monkeypox": {"VP37": "3Q50"},
    "Rabies": {"Glycoprotein": "2J8J"},
    "RSV": {"F protein": "4JHW"},
    "Adenovirus": {"Hexon": "1P30"}
}

def generate_binding_efficacy_data(virus, num_samples=50):
    """Generate binding efficacy data for treatments"""
    data = []
    proteins = VIRUS_PROTEINS.get(virus, ["Unknown"])
    
    # Select relevant drugs for this virus
    relevant_drugs = []
    for drug_name, drug_info in ANTIVIRAL_DRUGS.items():
        if any(target in proteins or any(p in target for p in proteins) 
               for target in drug_info["targets"]):
            relevant_drugs.append((drug_name, drug_info))
    
    # If no specific match, use common antivirals
    if not relevant_drugs:
        relevant_drugs = list(ANTIVIRAL_DRUGS.items())[:5]
    
    for _ in range(num_samples):
        drug_name, drug_info = random.choice(relevant_drugs)
        protein = random.choice(proteins)
        pdb_id = PDB_IDS.get(virus, {}).get(protein, "N/A")
        
        # Generate realistic IC50 values (nM)
        # Strong binders: 1-100 nM, Medium: 100-1000 nM, Weak: 1000-10000 nM
        binding_strength = random.choices(
            ['strong', 'medium', 'weak'],
            weights=[0.3, 0.5, 0.2]
        )[0]
        
        if binding_strength == 'strong':
            ic50 = np.random.lognormal(mean=3.5, sigma=0.5)  # ~30-50 nM
        elif binding_strength == 'medium':
            ic50 = np.random.lognormal(mean=5.5, sigma=0.5)  # ~200-500 nM
        else:
            ic50 = np.random.lognormal(mean=7.5, sigma=0.5)  # ~2000-5000 nM
        
        ic50 = max(0.5, min(ic50, 50000))  # Clamp to reasonable range
        
        # Generate Ki (inhibition constant) - usually similar to IC50
        ki = ic50 * np.random.uniform(0.7, 1.3) if random.random() > 0.3 else None
        
        data.append({
            'virus': virus,
            'protein': protein,
            'pdb_id': pdb_id,
            'drug_name': drug_name,
            'drug_id': drug_info['id'],
            'ic50_nm': round(ic50, 2),
            'ki_nm': round(ki, 2) if ki else None,
            'assay_type': random.choice(['IC50', 'Ki', 'EC50', 'Kd']),
            'source': random.choice(['Literature', 'PubChem', 'ChEMBL', 'Clinical Trial'])
        })
    
    return pd.DataFrame(data)

def generate_drug_rankings(virus, binding_data):
    """Generate drug rankings based on binding efficacy"""
    if binding_data.empty:
        return pd.DataFrame()
    
    # Group by drug and calculate statistics
    rankings = binding_data.groupby(['drug_name', 'drug_id']).agg({
        'ic50_nm': ['mean', 'min', 'count']
    }).reset_index()
    
    rankings.columns = ['drug_name', 'drug_id', 'avg_ic50_nm', 'best_ic50_nm', 'num_targets']
    
    # Rank by best IC50 (lower is better)
    rankings = rankings.sort_values('best_ic50_nm').reset_index(drop=True)
    rankings['rank'] = range(1, len(rankings) + 1)
    
    return rankings[['drug_name', 'drug_id', 'avg_ic50_nm', 'best_ic50_nm', 'num_targets', 'rank']]

def generate_patient_outcomes(virus, num_samples=100):
    """Generate patient outcome data"""
    data = []
    
    # Virus-specific mortality rates (approximate)
    mortality_rates = {
        "Ebola": 0.50, "Rabies": 0.99, "SARS-CoV-2": 0.02,
        "Influenza": 0.001, "Dengue": 0.01, "Zika": 0.001,
        "Monkeypox": 0.01, "HIV-1": 0.05, "HCV": 0.02,
        "HBV": 0.01, "HSV-1": 0.001, "CMV": 0.01,
        "RSV": 0.001, "Adenovirus": 0.001
    }
    
    base_mortality = mortality_rates.get(virus, 0.01)
    
    for i in range(num_samples):
        # Patient demographics
        age = random.randint(18, 85)
        gender = random.choice(['M', 'F', 'Other'])
        
        # Treatment status
        treated = random.random() > 0.2  # 80% treated
        
        # Outcome based on treatment and age
        if treated:
            mortality_prob = base_mortality * 0.5  # Treatment reduces mortality
        else:
            mortality_prob = base_mortality * 1.5
        
        # Age factor
        if age > 65:
            mortality_prob *= 1.5
        elif age < 30:
            mortality_prob *= 0.7
        
        outcome = 'deceased' if random.random() < mortality_prob else 'recovered'
        
        # Recovery time (days)
        if outcome == 'recovered':
            recovery_days = np.random.gamma(shape=3, scale=5) + 7
            recovery_days = min(recovery_days, 90)
        else:
            recovery_days = None
        
        # Severity score (1-10)
        severity = random.randint(1, 10)
        
        # Date
        date = datetime.now() - timedelta(days=random.randint(0, 365))
        
        data.append({
            'patient_id': f"{virus[:3]}_{i+1:04d}",
            'virus': virus,
            'age': age,
            'gender': gender,
            'treated': treated,
            'outcome': outcome,
            'recovery_days': round(recovery_days, 1) if recovery_days else None,
            'severity_score': severity,
            'date': date.strftime('%Y-%m-%d')
        })
    
    return pd.DataFrame(data)

def generate_treatment_data(virus, num_samples=80):
    """Generate treatment protocol data"""
    data = []
    proteins = VIRUS_PROTEINS.get(virus, ["Unknown"])
    
    relevant_drugs = []
    for drug_name, drug_info in ANTIVIRAL_DRUGS.items():
        if any(target in proteins or any(p in target for p in proteins) 
               for target in drug_info["targets"]):
            relevant_drugs.append((drug_name, drug_info))
    
    if not relevant_drugs:
        relevant_drugs = list(ANTIVIRAL_DRUGS.items())[:5]
    
    for i in range(num_samples):
        drug_name, drug_info = random.choice(relevant_drugs)
        
        # Treatment protocol
        dosage_mg = random.choice([100, 200, 250, 500, 750, 1000])
        frequency = random.choice(['once daily', 'twice daily', 'three times daily'])
        duration_days = random.randint(5, 21)
        
        # Efficacy
        efficacy = random.choices(
            ['high', 'moderate', 'low'],
            weights=[0.4, 0.4, 0.2]
        )[0]
        
        # Side effects
        side_effects = random.sample(
            ['nausea', 'headache', 'fatigue', 'diarrhea', 'rash', 'liver toxicity'],
            k=random.randint(0, 3)
        )
        
        data.append({
            'treatment_id': f"{virus[:3]}_TREAT_{i+1:04d}",
            'virus': virus,
            'drug_name': drug_name,
            'drug_id': drug_info['id'],
            'dosage_mg': dosage_mg,
            'frequency': frequency,
            'duration_days': duration_days,
            'efficacy': efficacy,
            'side_effects': ', '.join(side_effects) if side_effects else 'none',
            'protocol_source': random.choice(['FDA', 'WHO', 'Clinical Trial', 'Literature'])
        })
    
    return pd.DataFrame(data)

def generate_metadata(virus, binding_data, outcomes_data, treatments_data):
    """Generate metadata summary"""
    metadata = {
        'virus': virus,
        'generation_date': datetime.now().isoformat(),
        'total_records': len(binding_data) + len(outcomes_data) + len(treatments_data),
        'unique_drugs': binding_data['drug_id'].nunique() if not binding_data.empty else 0,
        'unique_proteins': binding_data['protein'].nunique() if not binding_data.empty else 0,
        'proteins': binding_data['protein'].unique().tolist() if not binding_data.empty else [],
        'total_patients': len(outcomes_data) if outcomes_data is not None else 0,
        'total_treatments': len(treatments_data) if treatments_data is not None else 0
    }
    
    if outcomes_data is not None and not outcomes_data.empty:
        metadata['recovery_rate'] = round(
            (outcomes_data['outcome'] == 'recovered').sum() / len(outcomes_data), 3
        )
        metadata['avg_recovery_days'] = round(
            outcomes_data['recovery_days'].mean(), 1
        ) if outcomes_data['recovery_days'].notna().any() else None
    
    return metadata

def generate_clinical_data_for_virus(virus):
    """Generate all clinical data for a single virus"""
    # Initialize data cleaner
    cleaner = DataCleaner(BASE_DIR)
    
    # Ensure correct folder structure
    paths = cleaner.ensure_folder_structure(virus, "clinical")
    if not cleaner.validate_file_paths(paths):
        print(f"    ✗ Failed to create folder structure for {virus}")
        return False
    
    print(f"\n  Generating clinical data for {virus}...")
    
    # Generate data
    binding_data = generate_binding_efficacy_data(virus, num_samples=50)
    drug_rankings = generate_drug_rankings(virus, binding_data)
    outcomes_data = generate_patient_outcomes(virus, num_samples=100)
    treatments_data = generate_treatment_data(virus, num_samples=80)
    
    # Clean data
    print(f"    [CLEAN] Cleaning data for {virus}...")
    binding_data = cleaner.clean_ic50_data(binding_data)
    outcomes_data = cleaner.clean_patient_outcomes(outcomes_data)
    
    # Check for existing data and merge
    binding_file = os.path.join(paths['treatments'], "binding_efficacy.csv")
    exists, existing_binding = cleaner.check_existing_data(binding_file)
    if exists and existing_binding is not None:
        binding_data = cleaner.merge_and_deduplicate(
            existing_binding, binding_data, 
            ['virus', 'drug_id', 'protein']
        )
    
    outcomes_file = os.path.join(paths['outcomes'], "patient_outcomes.csv")
    exists, existing_outcomes = cleaner.check_existing_data(outcomes_file)
    if exists and existing_outcomes is not None:
        outcomes_data = cleaner.merge_and_deduplicate(
            existing_outcomes, outcomes_data,
            ['patient_id']
        )
    
    # Generate metadata after cleaning
    metadata = generate_metadata(virus, binding_data, outcomes_data, treatments_data)
    
    # Save cleaned files
    cleaner.save_cleaned_data(binding_data, binding_file, clean_func=cleaner.clean_ic50_data)
    
    if not drug_rankings.empty:
        rankings_file = os.path.join(paths['outcomes'], "drug_rankings.csv")
        cleaner.save_cleaned_data(drug_rankings, rankings_file)
    
    cleaner.save_cleaned_data(outcomes_data, outcomes_file, clean_func=cleaner.clean_patient_outcomes)
    
    treatments_file = os.path.join(paths['treatments'], "treatment_data.csv")
    cleaner.save_cleaned_data(treatments_data, treatments_file)
    
    # Save metadata
    metadata_file = os.path.join(paths['metadata'], "summary.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"    ✓ Saved summary.json")
    
    # Generate quality report
    quality_report_file = os.path.join(paths['metadata'], "data_quality_report.json")
    cleaner.generate_data_quality_report(binding_data, quality_report_file)
    
    return True

def generate_clinical_datasets(viruses):
    """Generate clinical datasets for all viruses"""
    print(f"\nGenerating clinical data for {len(viruses)} viruses...")
    
    success_count = 0
    for virus in viruses:
        try:
            if generate_clinical_data_for_virus(virus):
                success_count += 1
        except Exception as e:
            print(f"    ✗ Error generating data for {virus}: {e}")
    
    print(f"\n✓ Generated clinical data for {success_count}/{len(viruses)} viruses")
    return success_count == len(viruses)

if __name__ == "__main__":
    test_viruses = ["SARS-CoV-2", "Ebola", "Influenza"]
    generate_clinical_datasets(test_viruses)

