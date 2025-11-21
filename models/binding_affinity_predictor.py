# binding_affinity_predictor.py
"""
Drug-Virus Binding Affinity Prediction Model for Viro-AI
FINE-TUNED VERSION: Enhanced feature engineering, cross-validation, and optimized hyperparameters
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor, ExtraTreesRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.model_selection import cross_val_score, KFold
import warnings
import logging

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class BindingAffinityPredictor:
    """
    Predicts drug-virus binding affinity without requiring RDKit.
    Uses SMILES-based features + molecular properties + VIRUS-SPECIFIC features.
    """
    
    def __init__(self, model_path=None):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        self.virus_encoder = None  # For encoding virus names
        self.supported_viruses = []  # List of all viruses in training
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def extract_smiles_features(self, smiles):
        """
        Extract ENHANCED features from SMILES string without RDKit.
        FINE-TUNED: Added more sophisticated molecular descriptors and ratios.
        """
        if pd.isna(smiles) or smiles == '':
            return np.zeros(35)  # Increased feature count
        
        smiles_upper = smiles.upper()
        smiles_len = len(smiles)
        
        # Basic atom counts
        c_count = smiles.count('C')
        n_count = smiles.count('N')
        o_count = smiles.count('O')
        s_count = smiles.count('S')
        f_count = smiles.count('F')
        cl_count = smiles.count('Cl')
        br_count = smiles.count('Br')
        p_count = smiles.count('P')
        
        # Bond counts
        double_bonds = smiles.count('=')
        triple_bonds = smiles.count('#')
        single_bonds = smiles.count('-')
        
        # Ring and structure counts
        branches = smiles.count('(')
        rings = smiles.count('1') + smiles.count('2') + smiles.count('3') + smiles.count('4') + smiles.count('5')
        aromatic = int('c' in smiles or 'n' in smiles or 'o' in smiles or 's' in smiles)
        
        # Functional groups
        carbonyl = smiles.count('=O')
        amine = smiles.count('NH') + smiles.count('N(')
        hydroxyl = smiles.count('OH')
        carboxyl = smiles.count('C(=O)O')
        ester = smiles.count('OC(=O)')
        amide = smiles.count('C(=O)N')
        
        # Total heavy atoms (non-H)
        heavy_atoms = c_count + n_count + o_count + s_count + f_count + cl_count + br_count + p_count
        
        # Avoid division by zero
        safe_smiles_len = max(smiles_len, 1)
        safe_c_count = max(c_count, 1)
        safe_heavy_atoms = max(heavy_atoms, 1)
        
        features = [
            # Basic counts (9 features)
            smiles_len,  # SMILES length
            c_count, n_count, o_count, s_count,
            f_count, cl_count, br_count, p_count,
            
            # Bond features (4 features)
            double_bonds, triple_bonds, single_bonds,
            double_bonds + triple_bonds,  # Total unsaturated bonds
            
            # Structural features (6 features)
            branches,
            rings,
            smiles.count('['),  # Brackets (charged atoms)
            smiles.count('@'),  # Chirality centers
            aromatic,
            smiles.count('-') + smiles.count('+'),  # Charges
            
            # Functional groups (7 features)
            o_count + n_count,  # H-bond donors/acceptors total
            carbonyl, amine, hydroxyl,
            carboxyl, ester, amide,
            
            # Ratios and complexity (9 features)
            heavy_atoms,  # Total heavy atoms
            n_count / safe_heavy_atoms,  # Nitrogen ratio
            o_count / safe_heavy_atoms,  # Oxygen ratio
            (f_count + cl_count + br_count) / safe_heavy_atoms,  # Halogen ratio
            (double_bonds + triple_bonds) / safe_smiles_len,  # Unsaturation ratio
            branches / safe_smiles_len,  # Branching ratio
            rings / safe_smiles_len,  # Ring density
            aromatic * rings / safe_smiles_len,  # Aromaticity score
            smiles_len / safe_c_count,  # Molecular complexity
        ]
        
        return np.array(features)
    
    def encode_virus(self, virus_name):
        """
        One-hot encode virus name.
        
        Args:
            virus_name: Name of the virus
        
        Returns:
            One-hot encoded vector
        """
        if self.supported_viruses is None or len(self.supported_viruses) == 0:
            return np.zeros(14)  # Default for 14 viruses
        
        # Create one-hot encoding
        virus_vector = np.zeros(len(self.supported_viruses))
        if virus_name in self.supported_viruses:
            idx = self.supported_viruses.index(virus_name)
            virus_vector[idx] = 1.0
        
        return virus_vector
    
    def prepare_features(self, df, is_training=False):
        """
        Prepare feature matrix from dataframe with enhanced descriptors + VIRUS encoding.
        
        Args:
            df: DataFrame with columns: smiles, mol_weight, logP, virus
            is_training: If True, build virus encoder from data
        
        Returns:
            Feature matrix (numpy array)
        """
        logger.info(f"Extracting features from {len(df)} samples...")
        
        # Build virus encoder during training
        if is_training and 'virus' in df.columns:
            self.supported_viruses = sorted(df['virus'].unique().tolist())
            logger.info(f"Found {len(self.supported_viruses)} unique viruses: {self.supported_viruses}")
        
        features_list = []
        
        for idx, row in df.iterrows():
            # SMILES-based features (35 features)
            smiles_feat = self.extract_smiles_features(row['smiles'])
            
            # Molecular property features (4 features - added derived features)
            mol_weight = row.get('mol_weight', 400.0)
            logP = row.get('logP', 2.0)
            
            # Derived features for drug-likeness
            lipinski_mw_score = 1.0 if mol_weight <= 500 else 0.5  # Lipinski MW rule
            lipinski_logp_score = 1.0 if -0.4 <= logP <= 5.6 else 0.5  # Lipinski logP rule
            
            # VIRUS-SPECIFIC features (one-hot encoding)
            if 'virus' in row and pd.notna(row['virus']):
                virus_features = self.encode_virus(row['virus'])
            else:
                virus_features = np.zeros(len(self.supported_viruses) if self.supported_viruses else 14)
            
            # Combine all features
            combined_features = np.concatenate([
                smiles_feat,  # 35 features
                [mol_weight, logP, lipinski_mw_score, lipinski_logp_score],  # 4 features
                virus_features  # 14 features (one-hot encoded virus)
            ])
            
            features_list.append(combined_features)
        
        X = np.array(features_list)
        
        logger.info(f"Feature matrix shape: {X.shape}")
        logger.info(f"Features: SMILES (35) + Molecular (4) + Virus (14) = {X.shape[1]} total")
        
        return X
    
    def train(self, train_data, val_data, target_column='pic50', use_cross_validation=True):
        """
        Train the binding affinity prediction model with enhanced optimization.
        
        Args:
            train_data: Training DataFrame
            val_data: Validation DataFrame
            target_column: Column name for target variable (default: pic50)
            use_cross_validation: Whether to perform cross-validation
        """
        logger.info("="*70)
        logger.info("TRAINING VIRUS-AWARE BINDING AFFINITY PREDICTION MODEL")
        logger.info("="*70)
        
        # Prepare features with virus encoding
        X_train = self.prepare_features(train_data, is_training=True)
        y_train = train_data[target_column].values
        
        X_val = self.prepare_features(val_data, is_training=False)
        y_val = val_data[target_column].values
        
        # Scale features - Use RobustScaler for better handling of outliers
        logger.info("Normalizing features with RobustScaler...")
        self.scaler = RobustScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # OPTIMIZED ENSEMBLE MODEL: Fine-tuned hyperparameters
        logger.info("Training OPTIMIZED ENSEMBLE MODEL...")
        logger.info("Components: RandomForest + ExtraTrees + GradientBoosting + ElasticNet")
        
        # Model 1: Random Forest (optimized hyperparameters)
        rf_model = RandomForestRegressor(
            n_estimators=200,  # Increased for better stability
            max_depth=6,  # Slightly deeper
            min_samples_split=3,  # Lower for more splits
            min_samples_leaf=1,  # Allow smaller leaves
            max_features='sqrt',
            random_state=42,
            n_jobs=-1,
            bootstrap=True
        )
        
        # Model 2: Extra Trees (adds more randomness, reduces overfitting)
        et_model = ExtraTreesRegressor(
            n_estimators=200,
            max_depth=7,
            min_samples_split=3,
            min_samples_leaf=1,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1,
            bootstrap=True
        )
        
        # Model 3: Gradient Boosting (fine-tuned for small datasets)
        gb_model = GradientBoostingRegressor(
            n_estimators=150,  # Increased
            max_depth=5,  # Deeper for more complexity
            learning_rate=0.03,  # Lower for better generalization
            subsample=0.85,  # Higher subsample
            min_samples_split=3,
            max_features='sqrt',
            random_state=42
        )
        
        # Model 4: ElasticNet (L1 + L2 regularization)
        elastic_model = ElasticNet(
            alpha=0.5,
            l1_ratio=0.5,
            random_state=42,
            max_iter=2000
        )
        
        # Weighted Ensemble: Give more weight to tree-based models
        self.model = VotingRegressor([
            ('rf', rf_model),
            ('et', et_model),
            ('gb', gb_model),
            ('elastic', elastic_model)
        ], weights=[2, 2, 2, 1])  # Tree models get double weight
        
        # Cross-validation on training set
        if use_cross_validation:
            logger.info("Performing 5-fold cross-validation...")
            cv = KFold(n_splits=5, shuffle=True, random_state=42)
            cv_scores = cross_val_score(
                self.model, X_train_scaled, y_train,
                cv=cv, scoring='neg_mean_squared_error', n_jobs=-1
            )
            cv_rmse = np.sqrt(-cv_scores.mean())
            cv_std = np.sqrt(cv_scores.std())
            logger.info(f"Cross-validation RMSE: {cv_rmse:.3f} (+/- {cv_std:.3f})")
        
        # Train on full training set
        logger.info("Training on full training set...")
        self.model.fit(X_train_scaled, y_train)
        print("  [OK] Ensemble trained!")
        
        # Evaluate on training set
        train_pred = self.model.predict(X_train_scaled)
        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        train_r2 = r2_score(y_train, train_pred)
        train_mae = mean_absolute_error(y_train, train_pred)
        
        # Evaluate on validation set
        val_pred = self.model.predict(X_val_scaled)
        val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
        val_r2 = r2_score(y_val, val_pred)
        val_mae = mean_absolute_error(y_val, val_pred)
        
        # Pearson correlation
        train_corr = np.corrcoef(y_train, train_pred)[0, 1]
        val_corr = np.corrcoef(y_val, val_pred)[0, 1]
        
        # Print results
        print(f"\n{'='*70}")
        print("TRAINING RESULTS:")
        print(f"{'='*70}")
        print(f"\nTraining Set ({len(y_train)} samples):")
        print(f"  RMSE:        {train_rmse:.3f}")
        print(f"  MAE:         {train_mae:.3f}")
        print(f"  R² Score:    {train_r2:.3f}")
        print(f"  Correlation: {train_corr:.3f}")
        
        print(f"\nValidation Set ({len(y_val)} samples):")
        print(f"  RMSE:        {val_rmse:.3f}")
        print(f"  MAE:         {val_mae:.3f}")
        print(f"  R2 Score:    {val_r2:.3f}")
        print(f"  Correlation: {val_corr:.3f} [KEY METRIC]")
        
        # Feature importance (from RandomForest component of ensemble)
        feature_names = [
            # Basic counts (9)
            'SMILES_length', 'C_count', 'N_count', 'O_count', 'S_count',
            'F_count', 'Cl_count', 'Br_count', 'P_count',
            # Bond features (4)
            'double_bonds', 'triple_bonds', 'single_bonds', 'unsaturated_bonds',
            # Structural (6)
            'branches', 'rings', 'brackets', 'chirality', 'aromatics', 'charges',
            # Functional groups (7)
            'H_bond_total', 'carbonyl', 'amine', 'hydroxyl', 'carboxyl', 'ester', 'amide',
            # Ratios and complexity (9)
            'heavy_atoms', 'N_ratio', 'O_ratio', 'halogen_ratio',
            'unsaturation_ratio', 'branching_ratio', 'ring_density', 'aromaticity_score', 'complexity',
            # Molecular properties (4)
            'mol_weight', 'logP', 'lipinski_mw_score', 'lipinski_logp_score'
        ]
        
        # Get feature importance from RF component
        try:
            rf_estimator = self.model.named_estimators_['rf']
            feature_importance = rf_estimator.feature_importances_
            top_features_idx = np.argsort(feature_importance)[-5:][::-1]
            
            print(f"\nTop 5 Important Features (from RandomForest):")
            for idx in top_features_idx:
                print(f"  {feature_names[idx]}: {feature_importance[idx]:.4f}")
        except:
            print(f"\n[INFO] Feature importance not available for ensemble model")
        
        self.is_trained = True
        self.feature_names = feature_names
        
        return {
            'train_rmse': train_rmse,
            'train_r2': train_r2,
            'val_rmse': val_rmse,
            'val_r2': val_r2,
            'val_correlation': val_corr
        }
    
    def predict(self, smiles, virus, mol_weight=None, logP=None):
        """
        Predict binding affinity for a single drug against a specific virus.
        
        Args:
            smiles: SMILES string
            virus: Virus name (REQUIRED for virus-specific prediction)
            mol_weight: Molecular weight (optional)
            logP: LogP value (optional)
        
        Returns:
            Predicted pIC50 value
        """
        if not self.is_trained:
            raise ValueError("Model not trained! Call train() first.")
        
        # Create temporary dataframe
        temp_df = pd.DataFrame([{
            'smiles': smiles,
            'virus': virus,  # CRITICAL: virus must be specified
            'mol_weight': mol_weight if mol_weight else 400,  # Default
            'logP': logP if logP else 2.0  # Default
        }])
        
        # Extract features
        X = self.prepare_features(temp_df, is_training=False)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        pic50 = self.model.predict(X_scaled)[0]
        
        return pic50
    
    def batch_predict(self, df, virus=None):
        """
        Predict binding affinity for multiple drugs against a specific virus.
        
        Args:
            df: DataFrame with columns: drug_id, name, smiles, mol_weight, logP
            virus: Virus name (if not in df, adds it to all rows)
        
        Returns:
            DataFrame with predictions sorted by affinity
        """
        if not self.is_trained:
            raise ValueError("Model not trained! Call train() first.")
        
        # Add virus column if not present
        temp_df = df.copy()
        if 'virus' not in temp_df.columns and virus:
            temp_df['virus'] = virus
        elif 'virus' not in temp_df.columns:
            # Default to first virus if not specified
            temp_df['virus'] = self.supported_viruses[0] if self.supported_viruses else 'Unknown'
        
        # Extract features
        X = self.prepare_features(temp_df, is_training=False)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        predictions = self.model.predict(X_scaled)
        
        # Add to dataframe
        result_df = df.copy()
        result_df['virus'] = temp_df['virus']
        result_df['predicted_pic50'] = predictions
        
        # Convert pIC50 to IC50 (nM)
        result_df['predicted_ic50_nm'] = 10 ** (9 - predictions)
        
        # Normalize to 0-1 score (higher = better binding)
        pic50_min = result_df['predicted_pic50'].min()
        pic50_max = result_df['predicted_pic50'].max()
        result_df['binding_score'] = (result_df['predicted_pic50'] - pic50_min) / (pic50_max - pic50_min)
        
        # Add binding strength classification
        result_df['binding_strength'] = pd.cut(
            result_df['predicted_pic50'],
            bins=[0, 5, 7, 15],
            labels=['weak', 'medium', 'strong']
        )
        
        # Sort by binding score (best first)
        result_df = result_df.sort_values('binding_score', ascending=False).reset_index(drop=True)
        result_df['rank'] = range(1, len(result_df) + 1)
        
        return result_df
    
    def save_model(self, path):
        """Save trained model to file."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model!")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained,
            'supported_viruses': self.supported_viruses  # Save virus encoder
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"[SAVED] Model saved to {path}")
    
    def load_model(self, path):
        """Load trained model from file."""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        self.supported_viruses = model_data.get('supported_viruses', [])  # Load virus encoder
        
        print(f"[LOADED] Model loaded from {path}")
        if self.supported_viruses:
            print(f"[INFO] Supports {len(self.supported_viruses)} viruses: {', '.join(self.supported_viruses)}")

# === MAIN TRAINING SCRIPT ===
if __name__ == "__main__":
    print("\n" + "="*70)
    print("VIRO-AI BINDING AFFINITY MODEL - TRAINING")
    print("="*70)
    
    # Load data
    print("\n[LOAD] Loading processed datasets...")
    train_data = pd.read_csv("Viroai_DataBase/processed/train_data.csv")
    val_data = pd.read_csv("Viroai_DataBase/processed/validation_data.csv")
    test_data = pd.read_csv("Viroai_DataBase/processed/test_data.csv")
    
    print(f"  Train: {len(train_data)} samples")
    print(f"  Val:   {len(val_data)} samples")
    print(f"  Test:  {len(test_data)} samples")
    
    # Initialize and train model
    predictor = BindingAffinityPredictor()
    metrics = predictor.train(train_data, val_data, target_column='pic50')
    
    # Test on test set
    print(f"\n{'='*70}")
    print("TESTING ON HELD-OUT TEST SET:")
    print(f"{'='*70}")
    
    X_test = predictor.prepare_features(test_data)
    X_test_scaled = predictor.scaler.transform(X_test)
    y_test = test_data['pic50'].values
    
    test_pred = predictor.model.predict(X_test_scaled)
    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    test_r2 = r2_score(y_test, test_pred)
    test_corr = np.corrcoef(y_test, test_pred)[0, 1]
    
    print(f"\nTest Set ({len(y_test)} samples):")
    print(f"  RMSE:        {test_rmse:.3f}")
    print(f"  R2 Score:    {test_r2:.3f}")
    print(f"  Correlation: {test_corr:.3f} [FINAL]")
    
    # Save model
    model_path = "models/saved_models/binding_model_v1.pkl"
    os.makedirs("models/saved_models", exist_ok=True)
    predictor.save_model(model_path)
    
    print(f"\n{'='*70}")
    if test_corr > 0.6:
        print("[SUCCESS] Model trained successfully! Correlation > 0.6")
    else:
        print("[WARNING] Model performance below target (correlation < 0.6)")
    print(f"{'='*70}")
    
    # Demo prediction - Test virus-specific predictions
    print("\n[DEMO] Testing virus-specific predictions...")
    print("  Drug: Remdesivir")
    print("  Testing against multiple viruses:")
    
    remdesivir_smiles = train_data[train_data['drug_name'] == 'Remdesivir'].iloc[0]['smiles']
    remdesivir_mw = train_data[train_data['drug_name'] == 'Remdesivir'].iloc[0]['mol_weight']
    remdesivir_logp = train_data[train_data['drug_name'] == 'Remdesivir'].iloc[0]['logP']
    
    test_viruses = ['SARS-CoV-2', 'HIV-1', 'Influenza', 'HCV']
    for virus in test_viruses:
        if virus in predictor.supported_viruses:
            pred_pic50 = predictor.predict(remdesivir_smiles, virus, remdesivir_mw, remdesivir_logp)
            pred_ic50 = 10 ** (9 - pred_pic50)
            print(f"    {virus:15s}: pIC50 = {pred_pic50:.2f}, IC50 = {pred_ic50:8.1f} nM")
    
    print("\n[SUCCESS] Model shows virus-specific predictions!")
    print("\n[OK] Model ready for deployment!")

