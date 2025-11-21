"""
Complete Training Pipeline: Generate Data -> Train Models -> Compare Accuracy
"""

import os
import sys
import subprocess
import json
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Viroai_DataBase", "data_generators"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "models"))

def check_and_generate_data():
    """Check if processed data exists, generate if needed"""
    processed_dir = "Viroai_DataBase/processed"
    train_file = os.path.join(processed_dir, "train_data.csv")
    
    if os.path.exists(train_file):
        import pandas as pd
        df = pd.read_csv(train_file)
        if len(df) > 100:  # If we have enough data
            print(f"[OK] Found existing processed data: {len(df)} training samples")
            return True
    
    print("[WARNING] Insufficient processed data. Generating datasets...")
    print("="*80)
    
    # Generate all datasets
    try:
        from generate_all_datasets import main as generate_all
        success = generate_all()
        if success:
            print("\n✓ All datasets generated successfully!")
            return True
        else:
            print("\n✗ Dataset generation had some issues")
            return False
    except Exception as e:
        print(f"\n[ERROR] Error generating datasets: {e}")
        return False

def train_all_models():
    """Train all ML models"""
    print("\n" + "="*80)
    print("TRAINING ALL ML MODULES")
    print("="*80)
    
    # Import training script
    try:
        from models.train_and_evaluate_all import main as train_all
        results = train_all()
        return results
    except Exception as e:
        print(f"Error training models: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_accuracy_table():
    """Generate final accuracy comparison table"""
    print("\n" + "="*80)
    print("GENERATING ACCURACY COMPARISON TABLE")
    print("="*80)
    
    # Load comparison results
    comparison_file = "ML_MODULES_ACCURACY_COMPARISON.json"
    if not os.path.exists(comparison_file):
        print("[WARNING] Comparison file not found. Running training first...")
        return
    
    with open(comparison_file, 'r') as f:
        data = json.load(f)
    
    previous = data.get('previous', {})
    current = data.get('current', {})
    
    # Create markdown table
    output = []
    output.append("# ML Modules Accuracy Comparison - Before vs After")
    output.append("")
    output.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    output.append("")
    output.append("## Summary")
    output.append("")
    output.append("| Module | Metric | Before | After | Improvement | Status |")
    output.append("|--------|--------|--------|-------|-------------|--------|")
    
    # Mutation Predictor
    mutation_targets = {
        'probability': 'Probability',
        'dnds': 'dN/dS Ratio',
        'binding': 'Binding Impact',
        'fitness': 'Fitness Score'
    }
    
    for key, label in mutation_targets.items():
        before = previous.get('mutation', {}).get(key, 0)
        after = current.get('mutation', {}).get(key, {}).get('r2', 0)
        improvement = after - before
        if improvement > 0.01:
            status = "✅ Improved"
        elif improvement < -0.01:
            status = "⚠️ Decreased"
        else:
            status = "➡️ Stable"
        
        output.append(f"| Mutation Predictor | {label} (R²) | {before:.3f} | {after:.3f} | {improvement:+.3f} | {status} |")
    
    # Drug Analyzer
    drug_targets = {
        'docking_score': 'Docking Score',
        'binding_energy': 'Binding Energy'
    }
    
    for key, label in drug_targets.items():
        before = previous.get('drug', {}).get(key, 0)
        after = current.get('drug', {}).get(key, {}).get('r2', 0)
        improvement = after - before
        if improvement > 0.01:
            status = "✅ Improved"
        elif improvement < -0.01:
            status = "⚠️ Decreased"
        else:
            status = "➡️ Stable"
        
        output.append(f"| Drug Analyzer | {label} (R²) | {before:.3f} | {after:.3f} | {improvement:+.3f} | {status} |")
    
    # Binding Affinity
    before_corr = previous.get('binding', {}).get('correlation', 0.6)
    after_corr = current.get('binding', {}).get('correlation', 0)
    improvement = after_corr - before_corr
    if improvement > 0.01:
        status = "✅ Improved"
    elif improvement < -0.01:
        status = "⚠️ Decreased"
    else:
        status = "➡️ Stable"
    
    output.append(f"| Binding Affinity | Correlation | {before_corr:.3f} | {after_corr:.3f} | {improvement:+.3f} | {status} |")
    
    after_r2 = current.get('binding', {}).get('r2', 0)
    output.append(f"| Binding Affinity | R² Score | N/A | {after_r2:.3f} | N/A | New Metric |")
    
    # Summary statistics
    output.append("")
    output.append("## Overall Statistics")
    output.append("")
    
    summary = data.get('summary', {})
    output.append(f"- ✅ Improved: {summary.get('improved', 0)} models")
    output.append(f"- ➡️ Stable: {summary.get('stable', 0)} models")
    output.append(f"- ⚠️ Decreased: {summary.get('decreased', 0)} models")
    
    # Save to file
    output_file = "ML_ACCURACY_BEFORE_AFTER.md"
    with open(output_file, 'w') as f:
        f.write('\n'.join(output))
    
        print(f"\n[OK] Accuracy comparison table saved to: {output_file}")
    print("\n" + '\n'.join(output[-20:]))  # Print last 20 lines
    
    return output_file

def main():
    """Main pipeline"""
    print("="*80)
    print("VIRO-AI ML TRAINING PIPELINE")
    print("Generate Data -> Train Models -> Compare Accuracy")
    print("="*80)
    
    # Step 1: Check and generate data
    if not check_and_generate_data():
        print("\n[ERROR] Failed to generate/verify datasets. Exiting.")
        return False
    
    # Step 2: Train all models
    results = train_all_models()
    if results is None:
        print("\n[ERROR] Training failed. Exiting.")
        return False
    
    # Step 3: Generate comparison table
    table_file = generate_accuracy_table()
    
    print("\n" + "="*80)
    print("PIPELINE COMPLETE!")
    print("="*80)
    print(f"\nResults saved to:")
    print(f"  - ML_MODULES_ACCURACY_COMPARISON.json")
    if table_file:
        print(f"  - {table_file}")
    print("\n[OK] All models trained and evaluated!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

