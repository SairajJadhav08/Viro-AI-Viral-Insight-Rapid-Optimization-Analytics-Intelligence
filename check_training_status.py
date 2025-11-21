"""
Quick script to check training status
"""

import os
import json
from datetime import datetime

def check_training_status():
    """Check if models have been retrained"""
    model_dir = "models/saved_models"
    
    print("="*70)
    print("TRAINING STATUS CHECK")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check Drug Analyzer models
    drug_metadata = os.path.join(model_dir, "drug_models_metadata.json")
    if os.path.exists(drug_metadata):
        with open(drug_metadata, 'r') as f:
            data = json.load(f)
        print("Drug Analyzer Models:")
        print(f"  Total models: {len(data.get('targets', []))}")
        print(f"  Last updated: {datetime.fromtimestamp(os.path.getmtime(drug_metadata)).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show R² scores
        print("\n  Model Performance (R²):")
        metrics = data.get('metrics', {})
        good_models = sum(1 for m in metrics.values() if m.get('test_r2', 0) > 0.3)
        print(f"  - Good models (R² > 0.3): {good_models}/{len(metrics)}")
        
        for target, metric in list(metrics.items())[:5]:  # Show first 5
            r2 = metric.get('test_r2', 0)
            status = "✓" if r2 > 0.3 else "⚠" if r2 > 0 else "✗"
            print(f"    {status} {target}: {r2:.3f}")
        if len(metrics) > 5:
            print(f"    ... and {len(metrics) - 5} more")
    else:
        print("Drug Analyzer: No metadata found (not trained yet)")
    
    print()
    
    # Check Chemical Modifier models
    mod_metadata = os.path.join(model_dir, "modification_models_metadata.json")
    if os.path.exists(mod_metadata):
        with open(mod_metadata, 'r') as f:
            data = json.load(f)
        print("Chemical Modifier Models:")
        print(f"  Total models: {len(data.get('targets', []))}")
        print(f"  Last updated: {datetime.fromtimestamp(os.path.getmtime(mod_metadata)).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show R² scores
        print("\n  Model Performance (R²):")
        metrics = data.get('metrics', {})
        good_models = sum(1 for m in metrics.values() if m.get('test_r2', 0) > 0.3)
        print(f"  - Good models (R² > 0.3): {good_models}/{len(metrics)}")
        
        for target, metric in list(metrics.items())[:5]:  # Show first 5
            r2 = metric.get('test_r2', 0)
            status = "✓" if r2 > 0.3 else "⚠" if r2 > 0 else "✗"
            print(f"    {status} {target}: {r2:.3f}")
        if len(metrics) > 5:
            print(f"    ... and {len(metrics) - 5} more")
    else:
        print("Chemical Modifier: No metadata found (not trained yet)")
    
    print("\n" + "="*70)
    print("Note: Training is running in the background.")
    print("Run this script again in a few minutes to see updated results.")
    print("="*70)

if __name__ == "__main__":
    check_training_status()

