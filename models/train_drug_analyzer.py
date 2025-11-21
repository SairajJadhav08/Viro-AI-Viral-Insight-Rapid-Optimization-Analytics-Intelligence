"""
ML Training Script for Enhanced Drug Analyzer
Trains models to predict comprehensive drug candidate metrics
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


class DrugAnalyzerTrainer:
    """
    Trainer for drug analysis models.
    Trains models to predict detailed drug property metrics.
    """
    
    def __init__(self, model_dir="models/saved_models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.models = {}
        self.scalers = {}
        self.feature_engineer = EnhancedFeatureEngineer()
        
    def load_training_data(self) -> pd.DataFrame:
        """Load and prepare drug training data from real-world and existing sources"""
        dfs = []
        
        # 1. Load enhanced drug training data (priority)
        enhanced_path = "Viroai_DataBase/pharma/enhanced_drug_training_data.csv"
        if os.path.exists(enhanced_path):
            try:
                enhanced_df = pd.read_csv(enhanced_path)
                logger.info(f"Loaded {len(enhanced_df)} enhanced drug training samples")
                dfs.append(enhanced_df)
            except Exception as e:
                logger.warning(f"Could not load enhanced data: {e}")
        
        # 2. Load real-world drug binding data
        real_world_path = "Viroai_DataBase/pharma/real_world_binding/real_world_drug_binding.csv"
        if os.path.exists(real_world_path):
            try:
                real_df = pd.read_csv(real_world_path)
                logger.info(f"Loaded {len(real_df)} real-world drug binding samples")
                dfs.append(real_df)
            except Exception as e:
                logger.warning(f"Could not load real-world data: {e}")
        
        # 3. Load existing processed data
        train_path = "Viroai_DataBase/processed/train_data.csv"
        val_path = "Viroai_DataBase/processed/validation_data.csv"
        test_path = "Viroai_DataBase/processed/test_data.csv"
        
        for path in [train_path, val_path, test_path]:
            if os.path.exists(path):
                try:
                    df = pd.read_csv(path)
                    dfs.append(df)
                except Exception as e:
                    logger.warning(f"Could not load {path}: {e}")
        
        if len(dfs) == 0:
            logger.info("No training data found, generating synthetic data...")
            return self._generate_synthetic_drug_data()
        
        df = pd.concat(dfs, ignore_index=True)
        logger.info(f"Total training samples: {len(df)}")
        return df
    
    def _generate_synthetic_drug_data(self, n_samples=300) -> pd.DataFrame:
        """Generate synthetic drug training data"""
        np.random.seed(42)
        
        # Load drug compounds
        drugs_path = "Viroai_DataBase/pharma/approved-drugs/antiviral_compounds.csv"
        if os.path.exists(drugs_path):
            drugs_df = pd.read_csv(drugs_path)
            n_samples = min(n_samples, len(drugs_df))
            drugs_df = drugs_df.sample(n=n_samples, random_state=42)
        else:
            # Create synthetic drugs
            drugs_df = pd.DataFrame({
                'name': [f'Drug_{i}' for i in range(n_samples)],
                'smiles': ['CC(C)CC1=CC=C(C=C1)C(C)C(=O)O' for _ in range(n_samples)],
                'mol_weight': np.random.uniform(200, 800, n_samples),
                'logP': np.random.uniform(-1, 6, n_samples)
            })
        
        # Generate features and targets
        data = []
        for idx, row in drugs_df.iterrows():
            mw = row.get('mol_weight', 400)
            logp = row.get('logP', 2.0)
            smiles = row.get('smiles', '')
            
            # Calculate molecular features
            c_count = smiles.count('C') if smiles else 20
            n_count = smiles.count('N') if smiles else 5
            o_count = smiles.count('O') if smiles else 5
            rings = smiles.count('1') + smiles.count('2') if smiles else 2
            aromatic = 1 if ('c' in smiles or 'C' in smiles) else 0
            
            # Generate target values (what we predict)
            binding_energy = -7.5 - np.random.uniform(0, 1.5)
            kd = 0.5 + np.random.uniform(0, 1.5)
            ic50 = 10 + np.random.uniform(0, 40)
            docking_score = binding_energy - 1.0
            
            # ADME properties
            absorption = 70 + np.random.uniform(0, 25)
            ppb = 60 + np.random.uniform(0, 30)
            clearance = 10 + np.random.uniform(0, 15)
            half_life = 3.5 + np.random.uniform(0, 20)
            
            # Toxicology
            ames_score = np.random.uniform(0, 0.3)  # Lower is better
            herg_ic50 = 10 + np.random.uniform(0, 20)
            
            # Stability
            rmsd = 0.8 + np.random.uniform(0, 1.2)
            mm_pbsa = -35 - np.random.uniform(0, 20)
            
            data.append({
                'name': row.get('name', f'Drug_{idx}'),
                'smiles': smiles,
                'mol_weight': mw,
                'logP': logp,
                'c_count': c_count,
                'n_count': n_count,
                'o_count': o_count,
                'rings': rings,
                'aromatic': aromatic,
                'heavy_atoms': c_count + n_count + o_count,
                'double_bonds': smiles.count('=') if smiles else 2,
                
                # Targets
                'binding_energy': binding_energy,
                'kd': kd,
                'ic50': ic50,
                'docking_score': docking_score,
                'absorption': absorption,
                'ppb': ppb,
                'clearance': clearance,
                'half_life': half_life,
                'ames_score': ames_score,
                'herg_ic50': herg_ic50,
                'rmsd': rmsd,
                'mm_pbsa': mm_pbsa,
                'overall_score': 80 + np.random.uniform(0, 20)
            })
        
        return pd.DataFrame(data)
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Prepare enhanced features using RDKit molecular descriptors + ADME + Toxicity"""
        # Extract enhanced molecular features for each drug
        enhanced_features_list = []
        for idx, row in df.iterrows():
            smiles = row.get('smiles', '')
            if not smiles or pd.isna(smiles):
                smiles = ''
            
            # Extract comprehensive features: basic + ADME + toxicity
            mol_features = self.feature_engineer.extract_rdkit_features(smiles)
            adme_features = self.feature_engineer.extract_adme_features(smiles)
            toxicity_features = self.feature_engineer.extract_toxicity_features(smiles)
            
            # Combine all features
            combined_features = {}
            combined_features.update(mol_features)
            combined_features.update(adme_features)
            combined_features.update(toxicity_features)
            enhanced_features_list.append(combined_features)
        
        # Convert to DataFrame
        features_df = pd.DataFrame(enhanced_features_list)
        
        # Fill missing values
        features_df = features_df.fillna(0)
        
        # Get feature columns (all molecular descriptors)
        feature_cols = [col for col in features_df.columns if col not in [
            'binding_energy', 'kd', 'ic50', 'docking_score', 'absorption', 'ppb',
            'clearance', 'half_life', 'ames_score', 'herg_ic50', 'rmsd', 'mm_pbsa', 'overall_score'
        ]]
        
        # Note: feature_cols are from features_df, not df, so we don't need to fill df columns
        # The features are already extracted in features_df
        
        # Target columns - get from original df
        target_cols = {
            'binding_energy': 'binding_energy',
            'kd': 'kd',
            'ic50': 'ic50',
            'docking_score': 'docking_score',
            'absorption': 'absorption',
            'ppb': 'ppb',
            'clearance': 'clearance',
            'half_life': 'half_life',
            'ames_score': 'ames_score',
            'herg_ic50': 'herg_ic50',
            'rmsd': 'rmsd',
            'mm_pbsa': 'mm_pbsa',
            'overall_score': 'overall_score'
        }
        
        # Create targets from df, with fallback generation if missing
        y_dict = {}
        for target_name, target_col in target_cols.items():
            if target_col in df.columns:
                y_dict[target_name] = df[target_col].fillna(0).values
            else:
                # Generate synthetic targets if missing
                logger.warning(f"Target {target_col} not found, generating synthetic values")
                if target_name == 'binding_energy':
                    y_dict[target_name] = -7.5 - np.random.uniform(0, 1.5, len(df))
                elif target_name == 'kd':
                    y_dict[target_name] = 0.5 + np.random.uniform(0, 1.5, len(df))
                elif target_name == 'ic50':
                    y_dict[target_name] = 10 + np.random.uniform(0, 40, len(df))
                elif target_name == 'docking_score':
                    # Try to get from df first
                    if 'binding_energy' in df.columns:
                        binding_energy = df['binding_energy'].fillna(-7.5).values
                        y_dict[target_name] = binding_energy - 1.0
                    # If binding_energy was just generated, use it
                    elif 'binding_energy' in y_dict:
                        y_dict[target_name] = y_dict['binding_energy'] - 1.0
                    else:
                        y_dict[target_name] = -8.5 - np.random.uniform(0, 1.5, len(df))
                elif target_name == 'absorption':
                    y_dict[target_name] = 70 + np.random.uniform(0, 25, len(df))
                elif target_name == 'ppb':
                    y_dict[target_name] = 60 + np.random.uniform(0, 30, len(df))
                elif target_name == 'clearance':
                    y_dict[target_name] = 10 + np.random.uniform(0, 15, len(df))
                elif target_name == 'half_life':
                    y_dict[target_name] = 3.5 + np.random.uniform(0, 20, len(df))
                elif target_name == 'ames_score':
                    y_dict[target_name] = np.random.uniform(0, 0.3, len(df))
                elif target_name == 'herg_ic50':
                    y_dict[target_name] = 10 + np.random.uniform(0, 20, len(df))
                elif target_name == 'rmsd':
                    y_dict[target_name] = 0.8 + np.random.uniform(0, 1.2, len(df))
                elif target_name == 'mm_pbsa':
                    y_dict[target_name] = -35 - np.random.uniform(0, 20, len(df))
                elif target_name == 'overall_score':
                    y_dict[target_name] = 80 + np.random.uniform(0, 20, len(df))
        
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
            
            # Feature selection for ADME/toxicity targets (improve performance)
            # BUT NOT for binding targets - they need all features
            is_adme_target = target_name in ['absorption', 'clearance', 'half_life', 'ppb']
            is_toxicity_target = target_name in ['ames_score', 'herg_ic50']
            is_binding_target = target_name in ['docking_score', 'binding_energy', 'kd', 'ic50']
            
            if is_adme_target or is_toxicity_target:
                # Select top features using mutual information
                n_features = min(100, X_train.shape[1] // 2)  # Use top 50% or 100 features
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
            elif is_binding_target:
                # For binding targets, use all features but with more selective approach
                logger.info(f"  Using all {X_train.shape[1]} features for binding target")
            
            # Scale features
            scaler = RobustScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Optimized models based on target type
            # For ADME/toxicity targets, use different hyperparameters
            is_adme_target = target_name in ['absorption', 'clearance', 'half_life', 'ppb']
            is_toxicity_target = target_name in ['ames_score', 'herg_ic50']
            is_binding_target = target_name in ['docking_score', 'binding_energy', 'kd', 'ic50']
            
            if is_adme_target or is_toxicity_target:
                # Optimized for ADME/toxicity: deeper trees, more estimators
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
            elif is_binding_target:
                # Optimized for binding targets: balance between depth and regularization
                rf_model = RandomForestRegressor(
                    n_estimators=500,
                    max_depth=15,
                    min_samples_split=3,
                    min_samples_leaf=1,
                    max_features='sqrt',
                    random_state=42,
                    n_jobs=-1
                )
                et_model = ExtraTreesRegressor(
                    n_estimators=500,
                    max_depth=15,
                    min_samples_split=3,
                    min_samples_leaf=1,
                    max_features='sqrt',
                    random_state=42,
                    n_jobs=-1
                )
                gb_model = GradientBoostingRegressor(
                    n_estimators=300,
                    max_depth=8,
                    learning_rate=0.03,
                    subsample=0.85,
                    min_samples_split=3,
                    min_samples_leaf=1,
                    max_features='sqrt',
                    random_state=42
                )
            else:
                # Standard hyperparameters for stability/other targets
                rf_model = RandomForestRegressor(
                    n_estimators=300,
                    max_depth=10,
                    min_samples_split=2,
                    min_samples_leaf=1,
                    max_features='sqrt',
                    random_state=42,
                    n_jobs=-1
                )
                et_model = ExtraTreesRegressor(
                    n_estimators=300,
                    max_depth=10,
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
            
            # Model 4: ElasticNet (for regularization)
            elastic_model = ElasticNet(
                alpha=0.5,
                l1_ratio=0.5,
                random_state=42,
                max_iter=2000
            )
            
            # Weighted ensemble - tree models get more weight
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
            model_path = os.path.join(self.model_dir, f"drug_{target_name}_model.pkl")
            scaler_path = os.path.join(self.model_dir, f"drug_{target_name}_scaler.pkl")
            
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
        
        metadata_path = os.path.join(self.model_dir, "drug_models_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved metadata: {metadata_path}")
    
    def train(self):
        """Main training function"""
        logger.info("="*70)
        logger.info("TRAINING DRUG ANALYZER MODELS")
        logger.info("="*70)
        
        # Load data
        df = self.load_training_data()
        logger.info(f"Loaded {len(df)} drug samples")
        
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
    trainer = DrugAnalyzerTrainer()
    trainer.train()

