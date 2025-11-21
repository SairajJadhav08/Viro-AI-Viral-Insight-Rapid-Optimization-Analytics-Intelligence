"""
Train All ML Modules and Generate Before/After Accuracy Comparison
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.train_mutation_predictor import MutationPredictorTrainer
from models.train_drug_analyzer import DrugAnalyzerTrainer
from models.train_chemical_modifier import ChemicalModifierTrainer
from models.binding_affinity_predictor import BindingAffinityPredictor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load previous accuracy metrics
PREVIOUS_ACCURACY_FILE = "ML_MODULES_ACCURACY_REPORT.md"

def load_previous_accuracy():
    """Load previous accuracy metrics from report"""
    previous = {
        'mutation': {},
        'drug': {},
        'binding': {},
        'chemical': {}
    }
    
    try:
        with open(PREVIOUS_ACCURACY_FILE, 'r') as f:
            content = f.read()
            
        # Parse mutation predictor
        if 'probability' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '| **probability**' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        previous['mutation']['probability'] = float(parts[2])
                elif '| **dnds**' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        previous['mutation']['dnds'] = float(parts[2])
                elif '| **binding**' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        previous['mutation']['binding'] = float(parts[2])
        
        # Parse drug analyzer
        if 'docking_score' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '| **docking_score**' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        previous['drug']['docking_score'] = float(parts[2])
                elif '| **binding_energy**' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        previous['drug']['binding_energy'] = float(parts[2])
        
        # Binding affinity - use correlation > 0.6 as baseline
        previous['binding'] = {'correlation': 0.6}
        
    except Exception as e:
        logger.warning(f"Could not load previous accuracy: {e}")
    
    return previous

def train_all_modules():
    """Train all ML modules and return accuracy metrics"""
    logger.info("="*80)
    logger.info("TRAINING ALL ML MODULES ON NEW DATASETS")
    logger.info("="*80)
    
    results = {}
    
    # 1. Train Binding Affinity Predictor (uses processed data)
    logger.info("\n" + "="*80)
    logger.info("STEP 1/4: TRAINING BINDING AFFINITY PREDICTOR")
    logger.info("="*80)
    try:
        train_data = pd.read_csv("Viroai_DataBase/processed/train_data.csv")
        val_data = pd.read_csv("Viroai_DataBase/processed/validation_data.csv")
        test_data = pd.read_csv("Viroai_DataBase/processed/test_data.csv")
        
        logger.info(f"Training data: {len(train_data)} samples")
        logger.info(f"Validation data: {len(val_data)} samples")
        logger.info(f"Test data: {len(test_data)} samples")
        
        predictor = BindingAffinityPredictor()
        predictor.train(train_data, val_data, target_column='pic50')
        
        # Evaluate on test set
        X_test = predictor.prepare_features(test_data)
        X_test_scaled = predictor.scaler.transform(X_test)
        y_test = test_data['pic50'].values
        test_pred = predictor.model.predict(X_test_scaled)
        
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        test_r2 = r2_score(y_test, test_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        test_corr = np.corrcoef(y_test, test_pred)[0, 1]
        
        results['binding'] = {
            'r2': test_r2,
            'rmse': test_rmse,
            'mae': test_mae,
            'correlation': test_corr
        }
        
        logger.info(f"✓ Binding Affinity: R²={test_r2:.3f}, Corr={test_corr:.3f}, RMSE={test_rmse:.3f}")
        
        # Save model
        os.makedirs("models/saved_models", exist_ok=True)
        predictor.save_model("models/saved_models/binding_model_v2.pkl")
        
    except Exception as e:
        logger.error(f"✗ Binding Affinity training failed: {e}")
        results['binding'] = None
    
    # 2. Train Mutation Predictor
    logger.info("\n" + "="*80)
    logger.info("STEP 2/4: TRAINING MUTATION PREDICTOR")
    logger.info("="*80)
    try:
        mutation_trainer = MutationPredictorTrainer()
        mutation_results = mutation_trainer.train()
        results['mutation'] = mutation_results
        logger.info("✓ Mutation predictor training completed")
    except Exception as e:
        logger.error(f"✗ Mutation predictor training failed: {e}")
        results['mutation'] = None
    
    # 3. Train Drug Analyzer
    logger.info("\n" + "="*80)
    logger.info("STEP 3/4: TRAINING DRUG ANALYZER")
    logger.info("="*80)
    try:
        drug_trainer = DrugAnalyzerTrainer()
        drug_results = drug_trainer.train()
        results['drug'] = drug_results
        logger.info("✓ Drug analyzer training completed")
    except Exception as e:
        logger.error(f"✗ Drug analyzer training failed: {e}")
        results['drug'] = None
    
    # 4. Train Chemical Modifier
    logger.info("\n" + "="*80)
    logger.info("STEP 4/4: TRAINING CHEMICAL MODIFIER")
    logger.info("="*80)
    try:
        modifier_trainer = ChemicalModifierTrainer()
        modifier_results = modifier_trainer.train()
        results['chemical'] = modifier_results
        logger.info("✓ Chemical modifier training completed")
    except Exception as e:
        logger.error(f"✗ Chemical modifier training failed: {e}")
        results['chemical'] = None
    
    return results

def extract_metrics_from_results(results):
    """Extract accuracy metrics from training results"""
    metrics = {
        'mutation': {},
        'drug': {},
        'binding': {},
        'chemical': {}
    }
    
    # Mutation Predictor
    if results.get('mutation'):
        mutation_results = results['mutation']
        for target, data in mutation_results.items():
            if isinstance(data, dict) and 'test_r2' in data:
                metrics['mutation'][target] = {
                    'r2': data['test_r2'],
                    'rmse': data.get('test_rmse', 0),
                    'mae': data.get('test_mae', 0)
                }
    
    # Drug Analyzer
    if results.get('drug'):
        drug_results = results['drug']
        for target, data in drug_results.items():
            if isinstance(data, dict) and 'test_r2' in data:
                metrics['drug'][target] = {
                    'r2': data['test_r2'],
                    'rmse': data.get('test_rmse', 0),
                    'mae': data.get('test_mae', 0)
                }
    
    # Binding Affinity
    if results.get('binding'):
        metrics['binding'] = results['binding']
    
    # Chemical Modifier
    if results.get('chemical'):
        chemical_results = results['chemical']
        for target, data in chemical_results.items():
            if isinstance(data, dict) and 'test_r2' in data:
                metrics['chemical'][target] = {
                    'r2': data['test_r2'],
                    'rmse': data.get('test_rmse', 0),
                    'mae': data.get('test_mae', 0)
                }
    
    return metrics

def generate_comparison_table(previous, current):
    """Generate before/after comparison table"""
    
    print("\n" + "="*80)
    print("ACCURACY COMPARISON: BEFORE vs AFTER")
    print("="*80)
    
    # Mutation Predictor
    print("\n## 1. MUTATION PREDICTOR")
    print("-" * 80)
    print(f"{'Target':<20} {'Before (R²)':<15} {'After (R²)':<15} {'Improvement':<15} {'Status'}")
    print("-" * 80)
    
    mutation_targets = ['probability', 'dnds', 'binding', 'fitness']
    for target in mutation_targets:
        before = previous.get('mutation', {}).get(target, 0)
        after = current.get('mutation', {}).get(target, {}).get('r2', 0)
        improvement = after - before
        status = "✅ Improved" if improvement > 0 else "⚠️ Decreased" if improvement < -0.05 else "➡️ Stable"
        print(f"{target:<20} {before:<15.3f} {after:<15.3f} {improvement:+.3f}          {status}")
    
    # Drug Analyzer
    print("\n## 2. DRUG ANALYZER")
    print("-" * 80)
    print(f"{'Target':<20} {'Before (R²)':<15} {'After (R²)':<15} {'Improvement':<15} {'Status'}")
    print("-" * 80)
    
    drug_targets = ['docking_score', 'binding_energy']
    for target in drug_targets:
        before = previous.get('drug', {}).get(target, 0)
        after = current.get('drug', {}).get(target, {}).get('r2', 0)
        improvement = after - before
        status = "✅ Improved" if improvement > 0 else "⚠️ Decreased" if improvement < -0.05 else "➡️ Stable"
        print(f"{target:<20} {before:<15.3f} {after:<15.3f} {improvement:+.3f}          {status}")
    
    # Binding Affinity
    print("\n## 3. BINDING AFFINITY PREDICTOR")
    print("-" * 80)
    print(f"{'Metric':<20} {'Before':<15} {'After':<15} {'Improvement':<15} {'Status'}")
    print("-" * 80)
    
    before_corr = previous.get('binding', {}).get('correlation', 0.6)
    after_corr = current.get('binding', {}).get('correlation', 0)
    improvement = after_corr - before_corr
    status = "✅ Improved" if improvement > 0 else "⚠️ Decreased" if improvement < -0.05 else "➡️ Stable"
    print(f"{'Correlation':<20} {before_corr:<15.3f} {after_corr:<15.3f} {improvement:+.3f}          {status}")
    
    before_r2 = 0  # Not tracked before
    after_r2 = current.get('binding', {}).get('r2', 0)
    print(f"{'R² Score':<20} {'N/A':<15} {after_r2:<15.3f} {'N/A':<15} {'New Metric'}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_improvements = 0
    total_decreases = 0
    total_stable = 0
    
    for target in mutation_targets:
        before = previous.get('mutation', {}).get(target, 0)
        after = current.get('mutation', {}).get(target, {}).get('r2', 0)
        if after > before + 0.01:
            total_improvements += 1
        elif after < before - 0.01:
            total_decreases += 1
        else:
            total_stable += 1
    
    for target in drug_targets:
        before = previous.get('drug', {}).get(target, 0)
        after = current.get('drug', {}).get(target, {}).get('r2', 0)
        if after > before + 0.01:
            total_improvements += 1
        elif after < before - 0.01:
            total_decreases += 1
        else:
            total_stable += 1
    
    if after_corr > before_corr + 0.01:
        total_improvements += 1
    elif after_corr < before_corr - 0.01:
        total_decreases += 1
    else:
        total_stable += 1
    
    print(f"✅ Improved: {total_improvements}")
    print(f"➡️ Stable: {total_stable}")
    print(f"⚠️ Decreased: {total_decreases}")
    
    return {
        'improved': total_improvements,
        'stable': total_stable,
        'decreased': total_decreases
    }

def main():
    """Main function"""
    # Load previous accuracy
    logger.info("Loading previous accuracy metrics...")
    previous = load_previous_accuracy()
    
    # Train all modules
    results = train_all_modules()
    
    # Extract metrics
    current = extract_metrics_from_results(results)
    
    # Generate comparison
    summary = generate_comparison_table(previous, current)
    
    # Save results
    output_file = "ML_MODULES_ACCURACY_COMPARISON.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'previous': previous,
            'current': current,
            'summary': summary
        }, f, indent=2)
    
    logger.info(f"\nResults saved to {output_file}")
    
    return results

if __name__ == "__main__":
    main()

