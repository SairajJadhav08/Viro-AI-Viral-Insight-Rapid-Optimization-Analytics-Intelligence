"""
ML Training Script for Enhanced Chemical Modifier
Trains models to predict detailed modification effects
"""

import pandas as pd
import numpy as np
import pickle
import os
import sys
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor, VotingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
import json
from typing import Dict, List, Tuple
import logging

# Add feature engineering module to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.feature_engineering.enhanced_features import EnhancedFeatureEngineer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChemicalModifierTrainer:
    """
    Trainer for chemical modification models.
    Trains models to predict detailed modification effects.
    """
    
    def __init__(self, model_dir="models/saved_models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.models = {}
        self.scalers = {}
        self.feature_engineer = EnhancedFeatureEngineer()
        
    def load_training_data(self) -> pd.DataFrame:
        """Load and prepare modification training data"""
        # 1. Try to load enhanced modification data (priority)
        enhanced_path = "Viroai_DataBase/pharma/enhanced_modification_training_data.csv"
        if os.path.exists(enhanced_path):
            try:
                enhanced_df = pd.read_csv(enhanced_path)
                logger.info(f"Loaded {len(enhanced_df)} enhanced modification training samples")
                return enhanced_df
            except Exception as e:
                logger.warning(f"Could not load enhanced data: {e}")
        
        # 2. Try to load existing modification data
        mods_dir = "Viroai_DataBase/Reports/modification-suggestions"
        if os.path.exists(mods_dir):
            # Could load from saved reports if available
            pass
        
        # 3. Generate synthetic training data
        logger.info("Generating synthetic modification training data...")
        return self._generate_synthetic_modification_data()
    
    def _generate_synthetic_modification_data(self, n_samples=400) -> pd.DataFrame:
        """Generate synthetic modification training data"""
        np.random.seed(42)
        
        # Load base drugs
        drugs_path = "Viroai_DataBase/pharma/approved-drugs/antiviral_compounds.csv"
        if os.path.exists(drugs_path):
            drugs_df = pd.read_csv(drugs_path)
            n_drugs = min(50, len(drugs_df))
            drugs_df = drugs_df.sample(n=n_drugs, random_state=42)
        else:
            drugs_df = pd.DataFrame({
                'name': ['Drug_1', 'Drug_2', 'Drug_3'],
                'smiles': ['CC(C)CC1=CC=C(C=C1)C(C)C(=O)O'] * 3,
                'mol_weight': [400, 450, 500],
                'logP': [2.0, 2.5, 3.0]
            })
        
        # Modification types
        mod_types = ['Fluorination', 'Methylation', 'Hydroxylation', 'Chlorination']
        
        data = []
        for idx, drug_row in drugs_df.iterrows():
            for mod_type in mod_types:
                for _ in range(n_samples // len(drugs_df) // len(mod_types)):
                    base_smiles = drug_row.get('smiles', 'CC(C)CC1=CC=C(C=C1)C(C)C(=O)O')
                    base_mw = drug_row.get('mol_weight', 400)
                    base_logp = drug_row.get('logP', 2.0)
                    
                    # Calculate base features
                    c_count = base_smiles.count('C')
                    n_count = base_smiles.count('N')
                    o_count = base_smiles.count('O')
                    rings = base_smiles.count('1') + base_smiles.count('2')
                    aromatic = 1 if ('c' in base_smiles or 'C' in base_smiles) else 0
                    
                    # Modification-specific effects
                    if mod_type == 'Fluorination':
                        mw_change = 18
                        logp_change = 0.3 + np.random.uniform(0, 0.3)
                        delta_be = -1.0 - np.random.uniform(0, 0.5)
                        metabolic_stab = 20 + np.random.uniform(0, 15)
                        sas_score = 2.5 + np.random.uniform(0, 1.0)
                    elif mod_type == 'Methylation':
                        mw_change = 14
                        logp_change = 0.5 + np.random.uniform(0, 0.4)
                        delta_be = -0.6 - np.random.uniform(0, 0.8)
                        metabolic_stab = 10 + np.random.uniform(0, 12)
                        sas_score = 2.2 + np.random.uniform(0, 0.8)
                    elif mod_type == 'Hydroxylation':
                        mw_change = 16
                        logp_change = -0.2 + np.random.uniform(0, 0.3)
                        delta_be = -0.5 - np.random.uniform(0, 0.7)
                        metabolic_stab = 5 + np.random.uniform(0, 10)
                        sas_score = 2.8 + np.random.uniform(0, 1.2)
                    else:  # Chlorination
                        mw_change = 35
                        logp_change = 0.7 + np.random.uniform(0, 0.5)
                        delta_be = -0.7 - np.random.uniform(0, 0.6)
                        metabolic_stab = 15 + np.random.uniform(0, 12)
                        sas_score = 2.8 + np.random.uniform(0, 1.2)
                    
                    # Generate targets
                    data.append({
                        'base_smiles': base_smiles,
                        'modification_type': mod_type,
                        'base_mw': base_mw,
                        'base_logp': base_logp,
                        'c_count': c_count,
                        'n_count': n_count,
                        'o_count': o_count,
                        'rings': rings,
                        'aromatic': aromatic,
                        'heavy_atoms': c_count + n_count + o_count,
                        
                        # Targets
                        'mw_change': mw_change,
                        'logp_change': logp_change,
                        'delta_be': delta_be,
                        'delta_rmsd': 0.2 + np.random.uniform(0, 0.5),
                        'delta_solubility': -0.2 + np.random.uniform(-0.3, 0.1),
                        'metabolic_stability': metabolic_stab,
                        'absorption_change': 6 + np.random.uniform(0, 8),
                        'clearance_change': -10 + np.random.uniform(-10, 0),
                        'sas_score': sas_score,
                        'structural_score': 80 + np.random.uniform(0, 15),
                        'binding_score': 85 + np.random.uniform(0, 12),
                        'overall_viability': 82 + np.random.uniform(0, 15)
                    })
        
        return pd.DataFrame(data)
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Prepare enhanced features using structural modification features"""
        # Extract enhanced features for each modification
        enhanced_features_list = []
        for idx, row in df.iterrows():
            base_smiles = row.get('base_smiles', '')
            modified_smiles = row.get('modified_smiles', base_smiles)  # Fallback to base if missing
            mod_type = row.get('modification_type', 'Fluorination')
            
            if not base_smiles or pd.isna(base_smiles):
                base_smiles = ''
            if not modified_smiles or pd.isna(modified_smiles):
                modified_smiles = base_smiles
            
            # Extract comprehensive modification features
            base_features = self.feature_engineer.extract_rdkit_features(base_smiles)
            mod_features = self.feature_engineer.extract_rdkit_features(modified_smiles)
            structural_features = self.feature_engineer.extract_modification_structural_features(
                base_smiles, modified_smiles, mod_type
            )
            
            # Combine all features
            combined_features = {}
            # Add base features with prefix
            for key, value in base_features.items():
                combined_features[f'base_{key}'] = value
            # Add modified features with prefix
            for key, value in mod_features.items():
                combined_features[f'mod_{key}'] = value
                # Add delta if base feature exists
                base_key = f'base_{key}'
                if base_key in combined_features:
                    combined_features[f'delta_{key}'] = value - combined_features[base_key]
            # Add structural modification features
            combined_features.update(structural_features)
            
            # Encode modification type
            mod_type_map = {'Fluorination': 0, 'Methylation': 1, 'Hydroxylation': 2, 'Chlorination': 3}
            combined_features['mod_type_encoded'] = mod_type_map.get(mod_type, 0)
            
            enhanced_features_list.append(combined_features)
        
        # Convert to DataFrame
        features_df = pd.DataFrame(enhanced_features_list)
        features_df = features_df.fillna(0)
        
        # Get feature columns (exclude target columns)
        feature_cols = [col for col in features_df.columns if col not in [
            'mw_change', 'logp_change', 'delta_be', 'delta_rmsd', 'delta_solubility',
            'metabolic_stability', 'absorption_change', 'clearance_change', 'sas_score',
            'structural_score', 'binding_score', 'overall_viability'
        ]]
        
        # Target columns
        target_cols = {
            'mw_change': 'mw_change',
            'logp_change': 'logp_change',
            'delta_be': 'delta_be',
            'delta_rmsd': 'delta_rmsd',
            'delta_solubility': 'delta_solubility',
            'metabolic_stability': 'metabolic_stability',
            'absorption_change': 'absorption_change',
            'clearance_change': 'clearance_change',
            'sas_score': 'sas_score',
            'structural_score': 'structural_score',
            'binding_score': 'binding_score',
            'overall_viability': 'overall_viability'
        }
        
        # Create targets if missing
        for target_name, target_col in target_cols.items():
            if target_col not in df.columns:
                if target_name == 'mw_change':
                    df[target_col] = np.random.choice([14, 16, 18, 35], len(df))
                elif target_name == 'logp_change':
                    df[target_col] = np.random.uniform(-0.2, 1.2, len(df))
                elif target_name == 'delta_be':
                    df[target_col] = -0.5 - np.random.uniform(0, 1.0, len(df))
                elif target_name == 'delta_rmsd':
                    df[target_col] = 0.2 + np.random.uniform(0, 0.5, len(df))
                elif target_name == 'delta_solubility':
                    df[target_col] = -0.2 + np.random.uniform(-0.3, 0.1, len(df))
                elif target_name == 'metabolic_stability':
                    df[target_col] = 10 + np.random.uniform(0, 20, len(df))
                elif target_name == 'absorption_change':
                    df[target_col] = 6 + np.random.uniform(0, 8, len(df))
                elif target_name == 'clearance_change':
                    df[target_col] = -10 + np.random.uniform(-10, 0, len(df))
                elif target_name == 'sas_score':
                    df[target_col] = 2.5 + np.random.uniform(0, 1.2, len(df))
                elif target_name == 'structural_score':
                    df[target_col] = 80 + np.random.uniform(0, 15, len(df))
                elif target_name == 'binding_score':
                    df[target_col] = 85 + np.random.uniform(0, 12, len(df))
                elif target_name == 'overall_viability':
                    df[target_col] = 82 + np.random.uniform(0, 15, len(df))
        
        # Ensure features_df has same length as df
        if len(features_df) != len(df):
            logger.warning(f"Feature length mismatch: {len(features_df)} vs {len(df)}")
            if len(features_df) < len(df):
                missing = len(df) - len(features_df)
                padding = pd.DataFrame(0, index=range(missing), columns=features_df.columns)
                features_df = pd.concat([features_df, padding], ignore_index=True)
            else:
                features_df = features_df.iloc[:len(df)]
        
        X = features_df[feature_cols].fillna(0).values
        
        # Create targets from df, with fallback generation if missing
        y_dict = {}
        for target_name, target_col in target_cols.items():
            if target_col in df.columns:
                y_dict[target_name] = df[target_col].fillna(0).values
            else:
                # Generate synthetic targets if missing
                logger.warning(f"Target {target_col} not found, generating synthetic values")
                if target_name == 'mw_change':
                    y_dict[target_name] = np.random.choice([14, 16, 18, 35], len(df))
                elif target_name == 'logp_change':
                    y_dict[target_name] = np.random.uniform(-0.2, 1.2, len(df))
                elif target_name == 'delta_be':
                    y_dict[target_name] = -0.5 - np.random.uniform(0, 1.0, len(df))
                elif target_name == 'delta_rmsd':
                    y_dict[target_name] = 0.2 + np.random.uniform(0, 0.5, len(df))
                elif target_name == 'delta_solubility':
                    y_dict[target_name] = -0.2 + np.random.uniform(-0.3, 0.1, len(df))
                elif target_name == 'metabolic_stability':
                    y_dict[target_name] = 10 + np.random.uniform(0, 20, len(df))
                elif target_name == 'absorption_change':
                    y_dict[target_name] = 6 + np.random.uniform(0, 8, len(df))
                elif target_name == 'clearance_change':
                    y_dict[target_name] = -10 + np.random.uniform(-10, 0, len(df))
                elif target_name == 'sas_score':
                    y_dict[target_name] = 2.5 + np.random.uniform(0, 1.2, len(df))
                elif target_name == 'structural_score':
                    y_dict[target_name] = 80 + np.random.uniform(0, 15, len(df))
                elif target_name == 'binding_score':
                    y_dict[target_name] = 85 + np.random.uniform(0, 12, len(df))
                elif target_name == 'overall_viability':
                    y_dict[target_name] = 82 + np.random.uniform(0, 15, len(df))
        
        logger.info(f"Feature matrix shape: {X.shape}")
        logger.info(f"Number of features: {len(feature_cols)}")
        
        return X, y_dict
    
    def train_models(self, X: np.ndarray, y_dict: Dict[str, np.ndarray]) -> Dict:
        """Train improved ensemble models for each target metric"""
        results = {}
        
        # Split data
        X_train, X_test, indices_train, indices_test = train_test_split(
            X, np.arange(len(X)), test_size=0.2, random_state=42
        )
        
        for target_name, y in y_dict.items():
            logger.info(f"Training improved ensemble model for {target_name}...")
            
            y_train = y[indices_train]
            y_test = y[indices_test]
            
            # Feature selection - be more selective for structural/binding
            is_structural_target = target_name in ['structural_score', 'binding_score']
            is_adme_target = target_name in ['absorption_change', 'clearance_change']
            
            if is_structural_target:
                # For structural/binding scores, use MORE features (they need comprehensive info)
                # But still select top features to avoid noise
                n_features = min(200, int(X_train.shape[1] * 0.75))  # Use top 75% features
                if n_features > 0:
                    try:
                        selector = SelectKBest(score_func=mutual_info_regression, k=n_features)
                        X_train_selected = selector.fit_transform(X_train, y_train)
                        X_test_selected = selector.transform(X_test)
                        logger.info(f"  Selected {n_features} features from {X_train.shape[1]} total for structural target")
                        X_train = X_train_selected
                        X_test = X_test_selected
                    except Exception as e:
                        logger.warning(f"  Feature selection failed: {e}, using all features")
            elif is_adme_target:
                # Select top features using mutual information
                n_features = min(150, X_train.shape[1] // 2)  # Use top 50% or 150 features
                if n_features > 0:
                    try:
                        selector = SelectKBest(score_func=mutual_info_regression, k=n_features)
                        X_train_selected = selector.fit_transform(X_train, y_train)
                        X_test_selected = selector.transform(X_test)
                        logger.info(f"  Selected {n_features} features from {X_train.shape[1]} total")
                        X_train = X_train_selected
                        X_test = X_test_selected
                    except Exception as e:
                        logger.warning(f"  Feature selection failed: {e}, using all features")
            
            # Scale features
            scaler = RobustScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Optimized models based on target type
            # For structural/binding targets, use different hyperparameters
            is_structural_target = target_name in ['structural_score', 'binding_score']
            is_adme_target = target_name in ['absorption_change', 'clearance_change']
            
            if is_structural_target:
                # Optimized for structural/binding: VERY deep trees, many estimators, less regularization
                rf_model = RandomForestRegressor(
                    n_estimators=600,
                    max_depth=20,
                    min_samples_split=2,
                    min_samples_leaf=1,
                    max_features='sqrt',
                    random_state=42,
                    n_jobs=-1
                )
                et_model = ExtraTreesRegressor(
                    n_estimators=600,
                    max_depth=20,
                    min_samples_split=2,
                    min_samples_leaf=1,
                    max_features='sqrt',
                    random_state=42,
                    n_jobs=-1
                )
                gb_model = GradientBoostingRegressor(
                    n_estimators=400,
                    max_depth=10,
                    learning_rate=0.02,
                    subsample=0.9,
                    min_samples_split=2,
                    min_samples_leaf=1,
                    max_features='sqrt',
                    random_state=42
                )
            elif is_adme_target:
                # Optimized for ADME: deeper trees, more estimators
                rf_model = RandomForestRegressor(
                    n_estimators=400,
                    max_depth=12,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    max_features='sqrt',
                    random_state=42,
                    n_jobs=-1
                )
                et_model = ExtraTreesRegressor(
                    n_estimators=400,
                    max_depth=12,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    max_features='sqrt',
                    random_state=42,
                    n_jobs=-1
                )
                gb_model = GradientBoostingRegressor(
                    n_estimators=300,
                    max_depth=7,
                    learning_rate=0.03,
                    subsample=0.85,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    max_features='sqrt',
                    random_state=42
                )
            else:
                # Standard hyperparameters for property changes (MW, LogP work well)
                rf_model = RandomForestRegressor(
                    n_estimators=300,
                    max_depth=8,
                    min_samples_split=2,
                    min_samples_leaf=1,
                    max_features='sqrt',
                    random_state=42,
                    n_jobs=-1
                )
                et_model = ExtraTreesRegressor(
                    n_estimators=300,
                    max_depth=8,
                    min_samples_split=2,
                    min_samples_leaf=1,
                    max_features='sqrt',
                    random_state=42,
                    n_jobs=-1
                )
                gb_model = GradientBoostingRegressor(
                    n_estimators=200,
                    max_depth=6,
                    learning_rate=0.05,
                    subsample=0.8,
                    min_samples_split=2,
                    max_features='sqrt',
                    random_state=42
                )
            
            # Add ElasticNet for regularization
            elastic_model = ElasticNet(
                alpha=0.5,
                l1_ratio=0.5,
                random_state=42,
                max_iter=2000
            )
            
            # Use ensemble with regularization
            model = VotingRegressor([
                ('rf', rf_model),
                ('et', et_model),
                ('gb', gb_model),
                ('elastic', elastic_model)
            ], weights=[2, 2, 2, 1])
            
            # Cross-validation
            try:
                cv = KFold(n_splits=min(5, len(X_train) // 10), shuffle=True, random_state=42)
                cv_scores = cross_val_score(
                    model, X_train_scaled, y_train,
                    cv=cv, scoring='r2', n_jobs=-1
                )
                cv_r2 = cv_scores.mean()
                logger.info(f"  Cross-validation R²: {cv_r2:.3f} (+/- {cv_scores.std():.3f})")
            except Exception as e:
                logger.warning(f"  Cross-validation failed: {e}")
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred_train = model.predict(X_train_scaled)
            y_pred_test = model.predict(X_test_scaled)
            
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            test_r2 = r2_score(y_test, y_pred_test)
            test_mae = mean_absolute_error(y_test, y_pred_test)
            
            results[target_name] = {
                'model': model,
                'scaler': scaler,
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'test_r2': test_r2,
                'test_mae': test_mae
            }
            
            status = "✅" if test_r2 > 0.1 else "⚠️" if test_r2 > 0 else "❌"
            logger.info(f"  {target_name}: Test RMSE={test_rmse:.3f}, R2={test_r2:.3f}, MAE={test_mae:.3f} {status}")
        
        return results
    
    def save_models(self, results: Dict):
        """Save trained models"""
        for target_name, result in results.items():
            model_path = os.path.join(self.model_dir, f"modification_{target_name}_model.pkl")
            scaler_path = os.path.join(self.model_dir, f"modification_{target_name}_scaler.pkl")
            
            with open(model_path, 'wb') as f:
                pickle.dump(result['model'], f)
            with open(scaler_path, 'wb') as f:
                pickle.dump(result['scaler'], f)
            
            logger.info(f"Saved model: {model_path}")
        
        # Save metadata
        metadata = {
            'targets': list(results.keys()),
            'metrics': {name: {
                'test_rmse': float(result['test_rmse']),
                'test_r2': float(result['test_r2']),
                'test_mae': float(result['test_mae'])
            } for name, result in results.items()}
        }
        
        metadata_path = os.path.join(self.model_dir, "modification_models_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved metadata: {metadata_path}")
    
    def train(self):
        """Main training function"""
        logger.info("="*70)
        logger.info("TRAINING CHEMICAL MODIFIER MODELS")
        logger.info("="*70)
        
        # Load data
        df = self.load_training_data()
        logger.info(f"Loaded {len(df)} modification samples")
        
        # Prepare features
        X, y_dict = self.prepare_features(df)
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Targets: {list(y_dict.keys())}")
        
        # Train models
        results = self.train_models(X, y_dict)
        
        # Save models
        self.save_models(results)
        
        logger.info("="*70)
        logger.info("TRAINING COMPLETE")
        logger.info("="*70)
        
        return results


if __name__ == "__main__":
    trainer = ChemicalModifierTrainer()
    trainer.train()

