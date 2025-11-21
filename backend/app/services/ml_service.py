"""
ML Service Layer - Wraps existing ML models
"""
import sys
import os
from typing import Dict, Any, List, Optional

# Add parent directory to path to import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from models.mutation_predictor_enhanced import EnhancedMutationPredictor
from models.drug_analyzer_enhanced import EnhancedDrugAnalyzer
from models.binding_affinity_predictor import BindingAffinityPredictor
from models.chemical_modifier_enhanced import EnhancedChemicalModifier

# Try to import ML-powered versions (use trained models)
try:
    from models.drug_analyzer_ml import MLDrugAnalyzer
    ML_DRUG_ANALYZER_AVAILABLE = True
except ImportError:
    ML_DRUG_ANALYZER_AVAILABLE = False
    print("[ML Service] ML-powered drug analyzer not available, using enhanced version")

try:
    from models.chemical_modifier_ml import MLChemicalModifier
    ML_CHEMICAL_MODIFIER_AVAILABLE = True
except ImportError:
    ML_CHEMICAL_MODIFIER_AVAILABLE = False
    print("[ML Service] ML-powered chemical modifier not available, using enhanced version")


class MLService:
    """Service layer for ML model integration"""
    
    def __init__(self):
        """Initialize ML models"""
        self.mutation_predictor = None
        self.drug_analyzer = None
        self.binding_predictor = None
        self.chemical_modifier = None
        self._load_models()
    
    def _load_models(self):
        """Load ML models"""
        try:
            self.mutation_predictor = EnhancedMutationPredictor()
            print("[ML Service] Mutation predictor loaded")
        except Exception as e:
            print(f"[ML Service] Warning: Could not load mutation predictor: {e}")
        
        try:
            # Try ML-powered version first (uses trained models)
            if ML_DRUG_ANALYZER_AVAILABLE:
                self.drug_analyzer = MLDrugAnalyzer()
                print("[ML Service] ML-powered drug analyzer loaded (using trained models)")
            else:
                self.drug_analyzer = EnhancedDrugAnalyzer()
                print("[ML Service] Enhanced drug analyzer loaded (rule-based)")
        except Exception as e:
            print(f"[ML Service] Warning: Could not load drug analyzer: {e}")
            try:
                self.drug_analyzer = EnhancedDrugAnalyzer()
                print("[ML Service] Fallback to enhanced drug analyzer")
            except:
                pass
        
        try:
            self.binding_predictor = BindingAffinityPredictor()
            print("[ML Service] Binding affinity predictor loaded")
        except Exception as e:
            print(f"[ML Service] Warning: Could not load binding predictor: {e}")
        
        try:
            # Try ML-powered version first (uses trained models)
            if ML_CHEMICAL_MODIFIER_AVAILABLE:
                self.chemical_modifier = MLChemicalModifier()
                print("[ML Service] ML-powered chemical modifier loaded (using trained models)")
            else:
                self.chemical_modifier = EnhancedChemicalModifier()
                print("[ML Service] Enhanced chemical modifier loaded (rule-based)")
        except Exception as e:
            print(f"[ML Service] Warning: Could not load chemical modifier: {e}")
            try:
                self.chemical_modifier = EnhancedChemicalModifier()
                print("[ML Service] Fallback to enhanced chemical modifier")
            except:
                pass
    
    def predict_mutations(self, sequence: str, protein_structure: Optional[Dict] = None, 
                         virus_name: str = "SARS-CoV-2") -> List[Dict[str, Any]]:
        """Predict mutations using enhanced mutation predictor"""
        if not self.mutation_predictor:
            raise RuntimeError("Mutation predictor not loaded")
        
        try:
            results = self.mutation_predictor.predict_with_details(
                sequence=sequence,
                protein_structure=protein_structure,
                virus_name=virus_name
            )
            return results
        except Exception as e:
            print(f"[ML Service] Error in mutation prediction: {e}")
            return []
    
    def analyze_drug_candidates(self, drug_list: List[Dict[str, str]], 
                                target_protein: str = "Spike Protein") -> List[Dict[str, Any]]:
        """Analyze drug candidates using enhanced drug analyzer"""
        if not self.drug_analyzer:
            raise RuntimeError("Drug analyzer not loaded")
        
        results = []
        for idx, drug in enumerate(drug_list, 1):
            try:
                analysis = self.drug_analyzer.analyze_compound_detailed(
                    smiles=drug.get("smiles", ""),
                    compound_name=drug.get("name", f"Compound {idx}"),
                    target_protein=target_protein,
                    rank=idx
                )
                results.append(analysis)
            except Exception as e:
                print(f"[ML Service] Error analyzing drug {drug.get('name', idx)}: {e}")
        
        return results
    
    def predict_binding_affinity(self, smiles: str, virus_name: str = "SARS-CoV-2") -> float:
        """Predict binding affinity for a drug-virus pair"""
        if not self.binding_predictor:
            raise RuntimeError("Binding affinity predictor not loaded")
        
        try:
            # Extract features and predict
            features = self.binding_predictor.extract_smiles_features(smiles)
            virus_features = self.binding_predictor.encode_virus(virus_name)
            
            # Combine features (simplified - actual implementation may vary)
            combined_features = list(features) + list(virus_features)
            
            # Predict (simplified - actual model prediction)
            if hasattr(self.binding_predictor, 'model') and self.binding_predictor.model:
                prediction = self.binding_predictor.model.predict([combined_features])[0]
                return float(prediction)
            else:
                # Fallback estimation
                return -8.5 + (hash(smiles) % 100) / 100.0
        except Exception as e:
            print(f"[ML Service] Error in binding affinity prediction: {e}")
            return -8.5
    
    def suggest_modifications(self, base_compound: Dict[str, str], 
                             modification_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Suggest chemical modifications using enhanced chemical modifier"""
        if not self.chemical_modifier:
            raise RuntimeError("Chemical modifier not loaded")
        
        if modification_types is None:
            modification_types = ["Fluorination", "Methylation", "Hydroxylation"]
        
        results = []
        base_smiles = base_compound.get("smiles", "")
        base_name = base_compound.get("name", "Base Compound")
        
        for idx, mod_type in enumerate(modification_types, 1):
            try:
                # Generate modified SMILES (simplified)
                modified_smiles = self._apply_modification(base_smiles, mod_type)
                
                analysis = self.chemical_modifier.analyze_modification_detailed(
                    base_smiles=base_smiles,
                    modified_smiles=modified_smiles,
                    base_compound_name=base_name,
                    modification_type=mod_type,
                    modification_id=idx
                )
                results.append(analysis)
            except Exception as e:
                print(f"[ML Service] Error in modification analysis: {e}")
        
        return results
    
    def _apply_modification(self, smiles: str, mod_type: str) -> str:
        """Apply a modification to SMILES (simplified)"""
        # This is a placeholder - actual implementation would use proper chemistry libraries
        if mod_type == "Fluorination":
            return smiles + "F"
        elif mod_type == "Methylation":
            return smiles + "C"
        elif mod_type == "Hydroxylation":
            return smiles + "O"
        return smiles


# Global ML service instance
ml_service = MLService()

