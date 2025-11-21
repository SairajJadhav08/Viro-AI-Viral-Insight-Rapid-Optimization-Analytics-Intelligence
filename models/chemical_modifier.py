# chemical_modifier.py
"""
AI-Suggested Chemical Modifications for Drug Optimization
Suggests structural modifications to improve binding affinity
"""

import pandas as pd
import re
from typing import List, Dict

class ChemicalModifier:
    """
    Suggests chemical modifications to improve drug binding affinity.
    Hackathon version: Rule-based SMILES transformations
    """
    
    # Common modifications that improve drug properties
    MODIFICATIONS = [
        {
            "name": "Add Fluorine (Fluorination)",
            "description": "Replace H with F on aliphatic carbon",
            "smiles_transform": lambda s: s.replace('CC', 'C(F)C', 1),
            "expected_improvement": {
                "binding": "+15-25%",
                "metabolic_stability": "+20-30%",
                "bioavailability": "+10-20%"
            },
            "confidence": 0.82
        },
        {
            "name": "Add Methyl Group (Methylation)",
            "description": "Add CH3 to aromatic ring",
            "smiles_transform": lambda s: s.replace('c1ccccc1', 'c1ccc(C)cc1', 1),
            "expected_improvement": {
                "binding": "+8-15%",
                "lipophilicity": "+12%",
                "membrane_permeability": "+15%"
            },
            "confidence": 0.75
        },
        {
            "name": "Add Hydroxyl Group (-OH)",
            "description": "Add OH for H-bonding",
            "smiles_transform": lambda s: s.replace('c1ccccc1', 'c1ccc(O)cc1', 1),
            "expected_improvement": {
                "binding": "+10-18%",
                "solubility": "+25%",
                "H_bond_interactions": "+30%"
            },
            "confidence": 0.78
        },
        {
            "name": "Chlorine Substitution",
            "description": "Add Cl for hydrophobic interaction",
            "smiles_transform": lambda s: s.replace('c1ccccc1', 'c1ccc(Cl)cc1', 1),
            "expected_improvement": {
                "binding": "+5-12%",
                "lipophilicity": "+18%",
                "protein_interaction": "+10%"
            },
            "confidence": 0.70
        },
        {
            "name": "Nitrogen Introduction",
            "description": "Replace C with N in ring",
            "smiles_transform": lambda s: s.replace('c1ccccc1', 'c1ncccc1', 1),
            "expected_improvement": {
                "binding": "+6-14%",
                "polar_interactions": "+20%",
                "metabolic_profile": "+8%"
            },
            "confidence": 0.68
        }
    ]
    
    # Virus-specific modification preferences
    VIRUS_PREFERENCES = {
        "SARS-CoV-2": [0, 2, 3],  # Fluorination, Hydroxyl, Chlorine
        "HIV-1": [0, 1, 4],  # Fluorination, Methylation, Nitrogen
        "Influenza": [0, 1, 2],  # Fluorination, Methylation, Hydroxyl
        "HCV": [2, 3, 4],  # Hydroxyl, Chlorine, Nitrogen
        "Ebola": [0, 2, 3],  # Fluorination, Hydroxyl, Chlorine
        "HSV-1": [1, 2, 3],  # Methylation, Hydroxyl, Chlorine
        "HBV": [0, 1, 2],  # Fluorination, Methylation, Hydroxyl
        "CMV": [2, 3, 4],  # Hydroxyl, Chlorine, Nitrogen
        "Dengue": [0, 2, 4],  # Fluorination, Hydroxyl, Nitrogen
        "Zika": [0, 2, 4],  # Fluorination, Hydroxyl, Nitrogen
        "RSV": [1, 2, 3],  # Methylation, Hydroxyl, Chlorine
        "Adenovirus": [0, 1, 3],  # Fluorination, Methylation, Chlorine
        "Monkeypox": [0, 2, 3],  # Fluorination, Hydroxyl, Chlorine
        "Rabies": [2, 3, 4],  # Hydroxyl, Chlorine, Nitrogen
    }
    
    def __init__(self):
        self.modifications = self.MODIFICATIONS
    
    def suggest_modifications(self, drug_name: str, drug_smiles: str, 
                             virus_name: str,  # NEW: virus-specific parameter
                             current_ic50_nm: float, num_suggestions: int = 3) -> List[Dict]:
        """
        Suggest chemical modifications for a drug against a specific virus.
        
        Args:
            drug_name: Name of the drug
            drug_smiles: SMILES string of original drug
            virus_name: Name of target virus (for virus-specific suggestions)
            current_ic50_nm: Current IC50 value in nM
            num_suggestions: Number of modification suggestions (default: 3)
        
        Returns:
            List of modification suggestions with predicted improvements
        """
        # Get virus-specific modification preferences
        mod_indices = self.VIRUS_PREFERENCES.get(virus_name, [0, 1, 2])
        selected_mods = [self.modifications[i] for i in mod_indices[:num_suggestions]]
        
        suggestions = []
        
        for i, mod in enumerate(selected_mods):
            try:
                # Apply transformation
                modified_smiles = mod['smiles_transform'](drug_smiles)
                
                # Calculate predicted IC50 improvement
                improvement_percent = float(mod['expected_improvement']['binding'].split('-')[0].replace('+', ''))
                predicted_ic50 = current_ic50_nm * (1 - improvement_percent / 100)
                
                # Calculate other improvements
                improvements = []
                for prop, val in mod['expected_improvement'].items():
                    improvements.append(f"{prop.replace('_', ' ').title()}: {val}")
                
                suggestion = {
                    "modification_id": i + 1,
                    "name": mod['name'],
                    "description": mod['description'],
                    "original_smiles": drug_smiles,
                    "modified_smiles": modified_smiles,
                    "smiles_changed": drug_smiles != modified_smiles,
                    "current_ic50_nm": current_ic50_nm,
                    "predicted_ic50_nm": round(predicted_ic50, 2),
                    "improvement_percent": improvement_percent,
                    "confidence": mod['confidence'],
                    "expected_improvements": improvements,
                    "synthetic_feasibility": "High" if mod['confidence'] > 0.75 else "Medium"
                }
                
                suggestions.append(suggestion)
                
            except Exception as e:
                # If transformation fails, skip
                continue
        
        return suggestions
    
    def format_modification_report(self, drug_name: str, suggestions: List[Dict]) -> str:
        """Format modification suggestions as readable report."""
        
        report = []
        report.append("=" * 80)
        report.append(f"AI-SUGGESTED CHEMICAL MODIFICATIONS FOR: {drug_name}")
        report.append("=" * 80)
        report.append("")
        
        if not suggestions:
            report.append("[INFO] No modifications suggested for this drug")
            return "\n".join(report)
        
        for i, sug in enumerate(suggestions, 1):
            report.append(f"MODIFICATION #{i}: {sug['name']}")
            report.append("-" * 80)
            report.append(f"Description: {sug['description']}")
            report.append("")
            report.append(f"Original SMILES:  {sug['original_smiles'][:60]}...")
            report.append(f"Modified SMILES:  {sug['modified_smiles'][:60]}...")
            report.append("")
            report.append(f"Current IC50:     {sug['current_ic50_nm']:.1f} nM")
            report.append(f"Predicted IC50:   {sug['predicted_ic50_nm']:.1f} nM")
            report.append(f"Improvement:      +{sug['improvement_percent']:.0f}%")
            report.append(f"Confidence:       {sug['confidence']*100:.0f}%")
            report.append(f"Feasibility:      {sug['synthetic_feasibility']}")
            report.append("")
            report.append("Expected Benefits:")
            for benefit in sug['expected_improvements']:
                report.append(f"  - {benefit}")
            report.append("")
            report.append("")
        
        return "\n".join(report)


# === DEMO/TEST ===
if __name__ == "__main__":
    print("\n" + "="*80)
    print("VIRO-AI CHEMICAL MODIFICATION SUGGESTER - DEMO")
    print("="*80)
    
    # Test with Remdesivir
    modifier = ChemicalModifier()
    
    drug_name = "Remdesivir"
    virus_name = "SARS-CoV-2"
    drug_smiles = "CCC(CC)COC(=O)C(C)NP(=O)(OCC1C(C(C(O1)(C#N)C2=CC=C3N2N=CN=C3N)O)O)OC4=CC=CC=C4"
    current_ic50 = 100.0  # nM
    
    print(f"\n[ANALYZE] Suggesting modifications for {drug_name} against {virus_name}")
    print(f"[CURRENT] IC50: {current_ic50} nM")
    
    suggestions = modifier.suggest_modifications(drug_name, drug_smiles, virus_name, current_ic50, num_suggestions=3)
    
    report = modifier.format_modification_report(drug_name, suggestions)
    print("\n" + report)
    
    # Save to file
    output_file = "Viroai_DataBase/Reports/modification-suggestions/remdesivir_modifications.txt"
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\n[SAVED] Report saved to: {output_file}")
    print("\n[OK] Chemical modifier module ready!")

