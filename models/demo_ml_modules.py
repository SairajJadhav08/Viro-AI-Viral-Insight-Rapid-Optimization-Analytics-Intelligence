"""
Demo script to show ML module outputs through CLI
"""

import sys
import os
import json

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

def demo_mutation_predictor():
    """Demo mutation predictor"""
    print("\n" + "="*70)
    print("MUTATION PREDICTOR DEMO")
    print("="*70)
    
    try:
        from models.mutation_predictor_enhanced import EnhancedMutationPredictor
        
        predictor = EnhancedMutationPredictor()
        sequence = "ATGGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAG"
        
        print(f"\nInput Sequence: {sequence[:50]}...")
        print(f"Virus: SARS-CoV-2")
        
        mutations = predictor.predict_with_details(sequence, virus_name="SARS-CoV-2")
        
        if mutations:
            print(f"\nPredicted {len(mutations)} mutations:")
            for i, mut in enumerate(mutations[:3], 1):  # Show first 3
                print(f"\n--- Mutation {i}: {mut['mutation']} ---")
                print(f"Probability: {mut['probability']:.3f}")
                print(f"Position: {mut['position']}")
                print(f"Genomic Level: {mut['genomicLevel']['mutationType']}")
                print(f"Binding Impact: {mut['receptorBinding']['deltaKd']}")
                print(f"Fitness Change: {mut['viralFitness']['replicationEfficiency']}")
        else:
            print("\nNo mutations predicted")
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

def demo_drug_analyzer():
    """Demo drug analyzer"""
    print("\n" + "="*70)
    print("DRUG ANALYZER DEMO")
    print("="*70)
    
    try:
        from models.drug_analyzer_enhanced import EnhancedDrugAnalyzer
        
        analyzer = EnhancedDrugAnalyzer()
        
        test_drugs = [
            {
                "name": "Remdesivir",
                "smiles": "CCC(CC)COC(=O)C(C)NP(=O)(OCC1C(C(C(O1)(C#N)C2=CC=C3N2N=CN=C3N)O)O)OC4=CC=CC=C4"
            },
            {
                "name": "Molnupiravir",
                "smiles": "CC(C)C(=O)OCC1C(C(C(O1)N2C=CC(=NC2=O)NO)O)O"
            }
        ]
        
        print(f"\nAnalyzing {len(test_drugs)} drug candidates...")
        
        for drug in test_drugs:
            analysis = analyzer.analyze_compound_detailed(
                smiles=drug["smiles"],
                compound_name=drug["name"],
                target_protein="Spike Protein",
                rank=1
            )
            
            print(f"\n--- {analysis['name']} ---")
            print(f"Overall Score: {analysis['overallScore']}/100")
            print(f"Binding Energy: {analysis['bindingMetrics']['bindingEnergy']}")
            print(f"IC50: {analysis['bindingMetrics']['ic50']}")
            print(f"LogP: {analysis['physicochemical']['logP']}")
            print(f"Absorption: {analysis['adme']['absorption']}")
            print(f"Half-life: {analysis['adme']['halfLife']}")
            print(f"Ames Test: {analysis['toxicology']['amesMutagenicity']}")
            print(f"Overall Quality: {analysis['comparativeScores']['overallQuality']}")
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

def demo_binding_affinity():
    """Demo binding affinity predictor"""
    print("\n" + "="*70)
    print("BINDING AFFINITY PREDICTOR DEMO")
    print("="*70)
    
    try:
        from models.binding_affinity_predictor import BindingAffinityPredictor
        
        predictor = BindingAffinityPredictor()
        
        # Try to load model
        model_path = "models/saved_models/binding_model_v1.pkl"
        if os.path.exists(model_path):
            predictor.load_model(model_path)
            print("\n[OK] Model loaded successfully")
        else:
            print("\n[WARNING] Model not found, using fallback predictions")
        
        test_drugs = [
            {
                "name": "Remdesivir",
                "smiles": "CCC(CC)COC(=O)C(C)NP(=O)(OCC1C(C(C(O1)(C#N)C2=CC=C3N2N=CN=C3N)O)O)OC4=CC=CC=C4",
                "virus": "SARS-CoV-2"
            },
            {
                "name": "Oseltamivir",
                "smiles": "CCC(CC)OC1C=C(CC(C1NC(=O)C)N)C(=O)OCC",
                "virus": "Influenza"
            }
        ]
        
        print(f"\nPredicting binding affinity for {len(test_drugs)} drug-virus pairs...")
        
        for drug in test_drugs:
            try:
                if predictor.is_trained:
                    pic50 = predictor.predict(
                        smiles=drug["smiles"],
                        virus=drug["virus"],
                        mol_weight=400,
                        logP=2.0
                    )
                    ic50_nm = 10 ** (9 - pic50)
                    print(f"\n--- {drug['name']} vs {drug['virus']} ---")
                    print(f"Predicted pIC50: {pic50:.2f}")
                    print(f"Predicted IC50: {ic50_nm:.1f} nM")
                else:
                    print(f"\n--- {drug['name']} vs {drug['virus']} ---")
                    print("[INFO] Model not trained, skipping prediction")
            except Exception as e:
                print(f"\n[ERROR] {drug['name']}: {e}")
                
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

def demo_chemical_modifier():
    """Demo chemical modifier"""
    print("\n" + "="*70)
    print("CHEMICAL MODIFIER DEMO")
    print("="*70)
    
    try:
        from models.chemical_modifier_enhanced import EnhancedChemicalModifier
        
        modifier = EnhancedChemicalModifier()
        
        test_modifications = [
            {
                "base_smiles": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
                "modified_smiles": "CC(C)CC1=CC=C(C=C1)C(C)(F)C(=O)O",
                "base_name": "Compound-A",
                "mod_type": "Fluorination"
            }
        ]
        
        print(f"\nAnalyzing {len(test_modifications)} chemical modifications...")
        
        for mod in test_modifications:
            analysis = modifier.analyze_modification_detailed(
                base_smiles=mod["base_smiles"],
                modified_smiles=mod["modified_smiles"],
                base_compound_name=mod["base_name"],
                modification_type=mod["mod_type"],
                modification_id=1
            )
            
            print(f"\n--- {analysis['modificationID']} ---")
            print(f"Base Compound: {analysis['baseCompound']}")
            print(f"Modification Type: {analysis['modificationType']}")
            print(f"Formula Change: {analysis['baseFormula']} -> {analysis['modifiedFormula']}")
            print(f"Binding Energy Change: {analysis['bindingAffinityEffects']['deltaBindingEnergy']}")
            print(f"Metabolic Stability: {analysis['stabilityDegradation']['metabolicStability']}")
            print(f"Overall Viability: {analysis['comparativeScoring']['overallViability']}")
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

def show_model_status():
    """Show status of all models"""
    print("\n" + "="*70)
    print("MODEL STATUS CHECK")
    print("="*70)
    
    import json
    
    models_status = {}
    
    # Check mutation models
    mut_path = "models/saved_models/mutation_models_metadata.json"
    if os.path.exists(mut_path):
        with open(mut_path, 'r') as f:
            data = json.load(f)
            avg_r2 = sum([m['test_r2'] for m in data['metrics'].values()]) / len(data['metrics'])
            models_status['Mutation Predictor'] = {
                'status': 'Trained',
                'models': len(data['metrics']),
                'avg_r2': f"{avg_r2:.3f}"
            }
    else:
        models_status['Mutation Predictor'] = {'status': 'Not Trained'}
    
    # Check drug models
    drug_path = "models/saved_models/drug_models_metadata.json"
    if os.path.exists(drug_path):
        with open(drug_path, 'r') as f:
            data = json.load(f)
            good_models = [m for m in data['metrics'].values() if m['test_r2'] > 0.5]
            models_status['Drug Analyzer'] = {
                'status': 'Trained',
                'models': len(data['metrics']),
                'good_models': len(good_models)
            }
    else:
        models_status['Drug Analyzer'] = {'status': 'Not Trained'}
    
    # Check modification models
    mod_path = "models/saved_models/modification_models_metadata.json"
    if os.path.exists(mod_path):
        with open(mod_path, 'r') as f:
            data = json.load(f)
            good_models = [m for m in data['metrics'].values() if m['test_r2'] > 0.5]
            models_status['Chemical Modifier'] = {
                'status': 'Trained',
                'models': len(data['metrics']),
                'good_models': len(good_models)
            }
    else:
        models_status['Chemical Modifier'] = {'status': 'Not Trained'}
    
    # Check binding model
    binding_path = "models/saved_models/binding_model_v1.pkl"
    if os.path.exists(binding_path):
        models_status['Binding Affinity'] = {'status': 'Trained'}
    else:
        models_status['Binding Affinity'] = {'status': 'Not Trained'}
    
    print("\nModel Status:")
    for model, status in models_status.items():
        print(f"\n{model}:")
        for key, value in status.items():
            print(f"  {key}: {value}")

def main():
    """Main demo function"""
    print("\n" + "="*70)
    print("VIRO-AI ML MODULES CLI DEMO")
    print("="*70)
    
    # Show model status first
    show_model_status()
    
    # Run demos
    demo_mutation_predictor()
    demo_drug_analyzer()
    demo_binding_affinity()
    demo_chemical_modifier()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()

