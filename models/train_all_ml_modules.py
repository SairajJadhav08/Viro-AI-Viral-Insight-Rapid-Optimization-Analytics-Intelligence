"""
Master Training Script for All ML Modules
Trains mutation predictor, drug analyzer, and chemical modifier models
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.train_mutation_predictor import MutationPredictorTrainer
from models.train_drug_analyzer import DrugAnalyzerTrainer
from models.train_chemical_modifier import ChemicalModifierTrainer

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def train_all_modules():
    """Train all ML modules"""
    logger.info("="*80)
    logger.info("VIRO-AI ML MODULES TRAINING - COMPLETE SYSTEM")
    logger.info("="*80)
    logger.info("")
    
    results = {}
    
    # 1. Train Mutation Predictor
    logger.info("="*80)
    logger.info("STEP 1/3: TRAINING MUTATION PREDICTOR")
    logger.info("="*80)
    try:
        mutation_trainer = MutationPredictorTrainer()
        mutation_results = mutation_trainer.train()
        results['mutation'] = mutation_results
        logger.info("✓ Mutation predictor training completed successfully")
    except Exception as e:
        logger.error(f"✗ Mutation predictor training failed: {e}")
        results['mutation'] = None
    
    logger.info("")
    
    # 2. Train Drug Analyzer
    logger.info("="*80)
    logger.info("STEP 2/3: TRAINING DRUG ANALYZER")
    logger.info("="*80)
    try:
        drug_trainer = DrugAnalyzerTrainer()
        drug_results = drug_trainer.train()
        results['drug'] = drug_results
        logger.info("✓ Drug analyzer training completed successfully")
    except Exception as e:
        logger.error(f"✗ Drug analyzer training failed: {e}")
        results['drug'] = None
    
    logger.info("")
    
    # 3. Train Chemical Modifier
    logger.info("="*80)
    logger.info("STEP 3/3: TRAINING CHEMICAL MODIFIER")
    logger.info("="*80)
    try:
        modifier_trainer = ChemicalModifierTrainer()
        modifier_results = modifier_trainer.train()
        results['modification'] = modifier_results
        logger.info("✓ Chemical modifier training completed successfully")
    except Exception as e:
        logger.error(f"✗ Chemical modifier training failed: {e}")
        results['modification'] = None
    
    # Summary
    logger.info("")
    logger.info("="*80)
    logger.info("TRAINING SUMMARY")
    logger.info("="*80)
    
    success_count = sum(1 for r in results.values() if r is not None)
    total_count = len(results)
    
    logger.info(f"Modules trained successfully: {success_count}/{total_count}")
    
    if results.get('mutation'):
        logger.info("  ✓ Mutation Predictor: Ready")
    else:
        logger.warning("  ✗ Mutation Predictor: Failed")
    
    if results.get('drug'):
        logger.info("  ✓ Drug Analyzer: Ready")
    else:
        logger.warning("  ✗ Drug Analyzer: Failed")
    
    if results.get('modification'):
        logger.info("  ✓ Chemical Modifier: Ready")
    else:
        logger.warning("  ✗ Chemical Modifier: Failed")
    
    logger.info("")
    logger.info("="*80)
    logger.info("TRAINING COMPLETE")
    logger.info("="*80)
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Models are saved in: models/saved_models/")
    logger.info("  2. Enhanced modules will automatically load trained models")
    logger.info("  3. Run analysis tasks to use ML-enhanced predictions")
    logger.info("")
    
    return results


if __name__ == "__main__":
    train_all_modules()

