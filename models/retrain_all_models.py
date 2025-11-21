"""
Retrain All ML Models with Enhanced Data
This script retrains all ML modules with enhanced training data
"""

import sys
import os
import subprocess

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def generate_enhanced_data():
    """Generate enhanced training data"""
    print("\n" + "="*70)
    print("STEP 1: GENERATING ENHANCED TRAINING DATA")
    print("="*70)
    
    # Generate drug data
    print("\n[1/2] Generating enhanced drug data...")
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from Viroai_DataBase.pharma.enhanced_drug_data_generator import generate_enhanced_drug_data
        import pandas as pd
        
        drug_df = generate_enhanced_drug_data()
        drug_path = "Viroai_DataBase/pharma/enhanced_drug_training_data.csv"
        os.makedirs(os.path.dirname(drug_path), exist_ok=True)
        drug_df.to_csv(drug_path, index=False)
        print(f"  [OK] Generated {len(drug_df)} drug samples")
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Generate modification data
    print("\n[2/2] Generating enhanced modification data...")
    try:
        from Viroai_DataBase.pharma.enhanced_modification_data_generator import generate_enhanced_modification_data
        
        mod_df = generate_enhanced_modification_data()
        mod_path = "Viroai_DataBase/pharma/enhanced_modification_training_data.csv"
        os.makedirs(os.path.dirname(mod_path), exist_ok=True)
        mod_df.to_csv(mod_path, index=False)
        print(f"  [OK] Generated {len(mod_df)} modification samples")
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def retrain_mutation_predictor():
    """Retrain mutation predictor"""
    print("\n" + "="*70)
    print("STEP 2: RETRAINING MUTATION PREDICTOR")
    print("="*70)
    
    try:
        from models.train_mutation_predictor import MutationPredictorTrainer
        trainer = MutationPredictorTrainer()
        results = trainer.train()
        print("\n  [OK] Mutation predictor training complete")
        return True
    except Exception as e:
        print(f"\n  [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def retrain_drug_analyzer():
    """Retrain drug analyzer"""
    print("\n" + "="*70)
    print("STEP 3: RETRAINING DRUG ANALYZER")
    print("="*70)
    
    try:
        from models.train_drug_analyzer import DrugAnalyzerTrainer
        trainer = DrugAnalyzerTrainer()
        results = trainer.train()
        print("\n  [OK] Drug analyzer training complete")
        return True
    except Exception as e:
        print(f"\n  [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def retrain_chemical_modifier():
    """Retrain chemical modifier"""
    print("\n" + "="*70)
    print("STEP 4: RETRAINING CHEMICAL MODIFIER")
    print("="*70)
    
    try:
        from models.train_chemical_modifier import ChemicalModifierTrainer
        trainer = ChemicalModifierTrainer()
        results = trainer.train()
        print("\n  [OK] Chemical modifier training complete")
        return True
    except Exception as e:
        print(f"\n  [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def retrain_binding_affinity():
    """Retrain binding affinity predictor"""
    print("\n" + "="*70)
    print("STEP 5: RETRAINING BINDING AFFINITY PREDICTOR")
    print("="*70)
    
    try:
        import pandas as pd
        from models.binding_affinity_predictor import BindingAffinityPredictor
        
        # Load data
        train_path = "Viroai_DataBase/processed/train_data.csv"
        val_path = "Viroai_DataBase/processed/validation_data.csv"
        
        if not os.path.exists(train_path) or not os.path.exists(val_path):
            print("  ⚠ Training data not found, skipping...")
            return True
        
        train_data = pd.read_csv(train_path)
        val_data = pd.read_csv(val_path)
        
        predictor = BindingAffinityPredictor()
        metrics = predictor.train(train_data, val_data, target_column='pic50')
        
        # Save model
        model_path = "models/saved_models/binding_model_v1.pkl"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        predictor.save_model(model_path)
        
        print("\n  [OK] Binding affinity predictor training complete")
        return True
    except Exception as e:
        print(f"\n  [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_results():
    """Show training results summary"""
    print("\n" + "="*70)
    print("TRAINING RESULTS SUMMARY")
    print("="*70)
    
    import json
    
    results = {}
    
    # Check mutation predictor
    mut_path = "models/saved_models/mutation_models_metadata.json"
    if os.path.exists(mut_path):
        with open(mut_path, 'r') as f:
            mut_data = json.load(f)
            avg_r2 = sum([m['test_r2'] for m in mut_data['metrics'].values()]) / len(mut_data['metrics'])
            results['Mutation Predictor'] = f"Average R²: {avg_r2:.3f}"
    
    # Check drug analyzer
    drug_path = "models/saved_models/drug_models_metadata.json"
    if os.path.exists(drug_path):
        with open(drug_path, 'r') as f:
            drug_data = json.load(f)
            good_models = [m for m in drug_data['metrics'].values() if m['test_r2'] > 0.5]
            results['Drug Analyzer'] = f"{len(good_models)}/{len(drug_data['metrics'])} models with R² > 0.5"
    
    # Check chemical modifier
    mod_path = "models/saved_models/modification_models_metadata.json"
    if os.path.exists(mod_path):
        with open(mod_path, 'r') as f:
            mod_data = json.load(f)
            good_models = [m for m in mod_data['metrics'].values() if m['test_r2'] > 0.5]
            results['Chemical Modifier'] = f"{len(good_models)}/{len(mod_data['metrics'])} models with R² > 0.5"
    
    for module, result in results.items():
        print(f"\n{module}: {result}")
    
    print("\n" + "="*70)

def main():
    """Main training pipeline"""
    print("\n" + "="*70)
    print("VIRO-AI ML MODELS RETRAINING PIPELINE")
    print("="*70)
    
    # Step 1: Generate enhanced data
    if not generate_enhanced_data():
        print("\n[ERROR] Failed to generate enhanced data. Exiting.")
        return
    
    # Step 2-5: Retrain models
    success_count = 0
    total_steps = 4
    
    if retrain_mutation_predictor():
        success_count += 1
    
    if retrain_drug_analyzer():
        success_count += 1
    
    if retrain_chemical_modifier():
        success_count += 1
    
    if retrain_binding_affinity():
        success_count += 1
    
    # Show results
    show_results()
    
    print("\n" + "="*70)
    print(f"TRAINING COMPLETE: {success_count}/{total_steps} modules trained successfully")
    print("="*70)
    
    if success_count == total_steps:
        print("\n[SUCCESS] All models retrained successfully!")
    else:
        print(f"\n[WARNING] {total_steps - success_count} module(s) failed to train")

if __name__ == "__main__":
    main()

