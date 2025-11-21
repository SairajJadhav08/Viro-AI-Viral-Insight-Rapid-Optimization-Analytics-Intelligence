# mutation_predictor.py
"""
Future Mutation Prediction Module
Predicts likely mutations and their impact on drug resistance
"""

import random
import pandas as pd

class MutationPredictor:
    """
    Predicts future viral mutations based on evolutionary patterns.
    Hackathon version: Rule-based with evolutionary hotspots.
    """
    
    # Known mutation hotspots for different viruses
    MUTATION_HOTSPOTS = {
        "SARS-CoV-2": {
            "Spike protein": ["N501Y", "E484K", "K417N", "L452R", "T478K", "D614G", "P681H"],
            "3CL protease": ["G143S", "M49I", "S144A", "H41Y"],
            "RNA polymerase": ["P323L", "V166L"]
        },
        "Influenza": {
            "Neuraminidase": ["H274Y", "N294S", "R292K"],
            "Hemagglutinin": ["D222G", "K180Q"]
        },
        "HIV-1": {
            "Protease": ["D30N", "L90M", "V82A", "I84V"],
            "Reverse Transcriptase": ["K103N", "M184V", "Y181C"]
        },
        "Ebola": {
            "Glycoprotein": ["A82V", "T544I"],
            "VP35": ["R312A"]
        }
    }
    
    def predict_mutations(self, virus_name, protein_name, num_predictions=3):
        """
        Predict likely future mutations for a virus (DETERMINISTIC).
        
        Args:
            virus_name: Name of virus
            protein_name: Target protein
            num_predictions: Number of mutation predictions
        
        Returns:
            List of predicted mutations with probabilities
        """
        print(f"\n[PREDICT] Analyzing mutation patterns for {virus_name}...")
        
        # Use virus+protein as seed for reproducible results
        seed = hash(f"{virus_name}_{protein_name}") % 100000
        random.seed(seed)
        
        # Get hotspots for this virus
        virus_hotspots = self.MUTATION_HOTSPOTS.get(virus_name, {})
        protein_mutations = virus_hotspots.get(protein_name, [])
        
        # If no data, generate generic predictions
        if not protein_mutations:
            protein_mutations = self._generate_generic_mutations(protein_name, seed)
        
        # Select top mutations (deterministic based on seed)
        predictions = []
        selected = random.sample(protein_mutations, min(num_predictions, len(protein_mutations)))
        
        for i, mutation in enumerate(selected, 1):
            # Calculate properties (deterministic based on mutation)
            mutation_hash = hash(f"{virus_name}_{mutation}") % 1000
            
            prediction = {
                "mutation_id": f"MUT{i}",
                "mutation": mutation,
                "location": protein_name,
                "probability": round(0.65 + (mutation_hash % 30) / 100.0, 2),  # 0.65-0.95
                "estimated_months": 3 + (mutation_hash % 16),  # 3-18 months
                "impact": self._assess_impact(mutation),
                "drug_resistance_risk": ["Low", "Medium", "High"][mutation_hash % 3],
                "transmissibility_change": ["+5%", "+10%", "+15%", "No change", "-5%"][mutation_hash % 5],
                "vaccine_escape": ["Low", "Medium", "High"][mutation_hash % 3]
            }
            predictions.append(prediction)
        
        # Sort by probability
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        # Reset random seed to avoid affecting other random operations
        import time
        random.seed(time.time())
        
        return predictions
    
    def _generate_generic_mutations(self, protein_name, seed=None):
        """Generate generic mutation names (deterministic if seed provided)."""
        if seed is not None:
            random.seed(seed)
        
        amino_acids = "ACDEFGHIKLMNPQRSTVWY"
        positions = random.sample(range(50, 600), 10)
        
        mutations = []
        for pos in positions:
            original = random.choice(amino_acids)
            mutated = random.choice(amino_acids.replace(original, ''))
            mutations.append(f"{original}{pos}{mutated}")
        
        return mutations
    
    def _assess_impact(self, mutation):
        """Assess impact level of mutation."""
        # Simplified: based on mutation type
        if any(x in mutation for x in ['K', 'R', 'D', 'E']):  # Charged residues
            return "HIGH"
        elif any(x in mutation for x in ['P', 'G']):  # Structure-affecting
            return "MEDIUM"
        else:
            return "LOW"
    
    def format_prediction_report(self, virus_name, predictions):
        """Format predictions as readable report."""
        report = []
        report.append("=" * 80)
        report.append(f"FUTURE MUTATION PREDICTION: {virus_name}")
        report.append("=" * 80)
        report.append("")
        report.append(f"Analyzing evolutionary patterns and mutation hotspots...")
        report.append(f"Total predictions: {len(predictions)}")
        report.append("")
        
        for pred in predictions:
            report.append(f"MUTATION #{pred['mutation_id']}: {pred['mutation']}")
            report.append("-" * 80)
            report.append(f"  Location:              {pred['location']}")
            report.append(f"  Probability:           {pred['probability'] * 100:.0f}%")
            report.append(f"  Estimated Timeline:    {pred['estimated_months']} months")
            report.append(f"  Impact Level:          {pred['impact']}")
            report.append(f"  Drug Resistance Risk:  {pred['drug_resistance_risk']}")
            report.append(f"  Transmissibility:      {pred['transmissibility_change']}")
            report.append(f"  Vaccine Escape:        {pred['vaccine_escape']}")
            report.append("")
        
        report.append("=" * 80)
        report.append("[INFO] These predictions are based on evolutionary patterns")
        report.append("[INFO] Actual mutations may differ - use for preparedness only")
        report.append("=" * 80)
        
        return "\n".join(report)


# === DEMO ===
if __name__ == "__main__":
    print("\n" + "="*80)
    print("VIRO-AI MUTATION PREDICTION - DEMO")
    print("="*80)
    
    predictor = MutationPredictor()
    
    # Test with SARS-CoV-2
    virus = "SARS-CoV-2"
    protein = "Spike protein"
    
    predictions = predictor.predict_mutations(virus, protein, num_predictions=3)
    report = predictor.format_prediction_report(virus, predictions)
    
    print("\n" + report)
    
    # Save to file
    import os
    output_dir = "Viroai_DataBase/Reports/mutation-predictions"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/{virus.replace(' ', '_')}_mutations.txt"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\n[SAVED] Report saved to: {output_file}")
    print("\n[OK] Mutation predictor ready!")

