"""
Enhanced Feature Engineering Module
Adds molecular descriptors (RDKit), sequence context, and advanced features
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import RDKit
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, Lipinski, rdMolDescriptors
    RDKIT_AVAILABLE = True
    logger.info("RDKit available for molecular descriptors")
except ImportError:
    RDKIT_AVAILABLE = False
    logger.warning("RDKit not available - using simplified molecular features")


class EnhancedFeatureEngineer:
    """Enhanced feature engineering with molecular descriptors and sequence context"""
    
    def __init__(self, cache_size=1000):
        self.rdkit_available = RDKIT_AVAILABLE
        # Cache for molecular objects to improve performance
        self._mol_cache = {}
        self.cache_size = cache_size
    
    def clear_cache(self):
        """Clear the molecular cache to free memory"""
        self._mol_cache.clear()
        logger.info("Molecular cache cleared")
    
    # ==================== MOLECULAR DESCRIPTORS (RDKit) ====================
    
    @lru_cache(maxsize=1000)
    def _get_mol_cached(self, smiles: str):
        """Cached molecule retrieval for performance"""
        if not self.rdkit_available:
            return None
        try:
            return Chem.MolFromSmiles(smiles)
        except Exception:
            return None
    
    def extract_rdkit_features(self, smiles: str) -> Dict[str, float]:
        """Extract comprehensive molecular descriptors using RDKit"""
        if not self.rdkit_available or not smiles:
            return self._extract_simplified_features(smiles)
        
        try:
            mol = self._get_mol(smiles)
            if mol is None:
                return self._extract_simplified_features(smiles)
            
            features = {}
            
            # Basic molecular properties
            features['mol_weight'] = Descriptors.MolWt(mol)
            features['logp'] = Descriptors.MolLogP(mol)
            features['tpsa'] = Descriptors.TPSA(mol)
            features['num_atoms'] = mol.GetNumAtoms()
            features['num_heavy_atoms'] = Descriptors.HeavyAtomCount(mol)
            features['num_rings'] = Descriptors.RingCount(mol)
            features['num_aromatic_rings'] = Descriptors.NumAromaticRings(mol)
            features['num_saturated_rings'] = Descriptors.NumSaturatedRings(mol)
            features['num_heteroatoms'] = Descriptors.NumHeteroatoms(mol)
            
            # Lipinski's Rule of Five
            features['lipinski_hbd'] = Lipinski.NumHDonors(mol)
            features['lipinski_hba'] = Lipinski.NumHAcceptors(mol)
            features['lipinski_mw'] = Descriptors.MolWt(mol)
            features['lipinski_logp'] = Descriptors.MolLogP(mol)
            
            # Topological descriptors
            features['balaban_j'] = Descriptors.BalabanJ(mol)
            features['bertz_ct'] = Descriptors.BertzCT(mol)
            features['chi0'] = Descriptors.Chi0(mol)
            features['chi1'] = Descriptors.Chi1(mol)
            features['chi0n'] = Descriptors.Chi0n(mol)
            features['chi1n'] = Descriptors.Chi1n(mol)
            features['chi2n'] = Descriptors.Chi2n(mol)
            features['chi3n'] = Descriptors.Chi3n(mol)
            features['chi4n'] = Descriptors.Chi4n(mol)
            
            # Connectivity indices
            features['kappa1'] = Descriptors.Kappa1(mol)
            features['kappa2'] = Descriptors.Kappa2(mol)
            features['kappa3'] = Descriptors.Kappa3(mol)
            
            # Electronic descriptors
            features['slogp_vsa1'] = Descriptors.SlogP_VSA1(mol)
            features['slogp_vsa2'] = Descriptors.SlogP_VSA2(mol)
            features['smr_vsa1'] = Descriptors.SMR_VSA1(mol)
            features['smr_vsa2'] = Descriptors.SMR_VSA2(mol)
            
            # Shape descriptors (removed - not available in all RDKit versions)
            # features['asphericity'] = Descriptors.Asphericity(mol)
            # features['eccentricity'] = Descriptors.Eccentricity(mol)
            # features['spherocity_index'] = Descriptors.SpherocityIndex(mol)
            features['asphericity'] = 0.0  # Placeholder
            features['eccentricity'] = 0.0  # Placeholder
            features['spherocity_index'] = 0.0  # Placeholder
            
            # Fragment-based features (handle version differences)
            try:
                features['fr_aromatic'] = Descriptors.fr_aromatic(mol)
            except AttributeError:
                features['fr_aromatic'] = Descriptors.NumAromaticRings(mol)  # Fallback
            try:
                features['fr_saturated'] = Descriptors.fr_saturated(mol)
            except AttributeError:
                features['fr_saturated'] = Descriptors.NumSaturatedRings(mol)  # Fallback
            try:
                features['fr_aliphatic'] = Descriptors.fr_aliphatic(mol)
            except AttributeError:
                features['fr_aliphatic'] = max(0, Descriptors.RingCount(mol) - Descriptors.NumAromaticRings(mol))  # Fallback
            
            # Rotatable bonds
            features['num_rotatable_bonds'] = Descriptors.NumRotatableBonds(mol)
            try:
                features['num_amide_bonds'] = rdMolDescriptors.CalcNumAmideBonds(mol)
            except AttributeError:
                features['num_amide_bonds'] = 0  # Fallback
            try:
                features['num_aromatic_bonds'] = rdMolDescriptors.CalcNumAromaticBonds(mol)
            except AttributeError:
                # Fallback: count aromatic bonds manually
                features['num_aromatic_bonds'] = sum(1 for bond in mol.GetBonds() if bond.GetIsAromatic())
            
            # Hydrogen bonding
            features['num_hbd'] = Descriptors.NumHDonors(mol)
            features['num_hba'] = Descriptors.NumHAcceptors(mol)
            
            # Charge and polarity
            features['formal_charge'] = Chem.rdmolops.GetFormalCharge(mol)
            features['num_radical_electrons'] = Descriptors.NumRadicalElectrons(mol)
            
            # Complexity
            features['mol_complexity'] = Descriptors.MolMR(mol)
            features['fraction_csp3'] = Descriptors.FpDensityMorgan1(mol)
            
            return features
            
        except Exception as e:
            logger.warning(f"Error extracting RDKit features: {e}")
            return self._extract_simplified_features(smiles)
    
    def _extract_simplified_features(self, smiles: str) -> Dict[str, float]:
        """Fallback simplified feature extraction without RDKit"""
        if not smiles:
            return {}
        
        features = {}
        features['mol_weight'] = smiles.count('C') * 12 + smiles.count('N') * 14 + smiles.count('O') * 16
        features['logp'] = smiles.count('C') * 0.5 - smiles.count('O') * 0.3
        features['tpsa'] = smiles.count('O') * 20 + smiles.count('N') * 12
        features['num_atoms'] = len([c for c in smiles if c.isupper()])
        features['num_heavy_atoms'] = smiles.count('C') + smiles.count('N') + smiles.count('O')
        features['num_rings'] = smiles.count('1') + smiles.count('2')
        features['num_aromatic_rings'] = 1 if 'c' in smiles or 'C' in smiles else 0
        features['num_rotatable_bonds'] = max(3, int(features['num_heavy_atoms'] / 5))
        features['num_hbd'] = min(smiles.count('N'), 2)
        features['num_hba'] = smiles.count('O') + smiles.count('N')
        
        # Fill missing RDKit features with defaults
        rdkit_features = [
            'lipinski_hbd', 'lipinski_hba', 'balaban_j', 'bertz_ct',
            'chi0', 'chi1', 'chi0n', 'chi1n', 'chi2n', 'chi3n', 'chi4n',
            'kappa1', 'kappa2', 'kappa3', 'slogp_vsa1', 'slogp_vsa2',
            'smr_vsa1', 'smr_vsa2', 'asphericity', 'eccentricity',
            'spherocity_index', 'fr_aromatic', 'fr_saturated', 'fr_aliphatic',
            'num_amide_bonds', 'num_aromatic_bonds', 'formal_charge',
            'num_radical_electrons', 'mol_complexity', 'fraction_csp3'
        ]
        
        for feat in rdkit_features:
            features[feat] = 0.0
        
        return features
    
    # ==================== SEQUENCE CONTEXT FEATURES ====================
    
    def extract_sequence_context(self, sequence: str, position: int, window_size: int = 10) -> Dict[str, float]:
        """Extract sequence context features around mutation position"""
        if not sequence or not isinstance(sequence, str) or position < 0:
            return {}
        
        # Ensure position is within sequence bounds
        if position >= len(sequence):
            position = len(sequence) - 1
        
        features = {}
        
        # Get context windows
        start = max(0, position - window_size)
        end = min(len(sequence), position + window_size + 1)
        upstream = sequence[start:position] if position > 0 else ''
        downstream = sequence[position+1:end] if position < len(sequence) else ''
        
        # Amino acid composition in context
        aa_counts = {}
        for aa in 'ACDEFGHIKLMNPQRSTVWY':
            aa_counts[f'upstream_{aa}'] = upstream.count(aa) / max(len(upstream), 1)
            aa_counts[f'downstream_{aa}'] = downstream.count(aa) / max(len(downstream), 1)
        
        features.update(aa_counts)
        
        # Hydrophobicity in context
        hydrophobic_aa = 'AILMFWYV'
        features['upstream_hydrophobicity'] = sum(upstream.count(aa) for aa in hydrophobic_aa) / max(len(upstream), 1)
        features['downstream_hydrophobicity'] = sum(downstream.count(aa) for aa in hydrophobic_aa) / max(len(downstream), 1)
        
        # Charge in context
        positive_aa = 'KRH'
        negative_aa = 'DE'
        features['upstream_positive_charge'] = sum(upstream.count(aa) for aa in positive_aa) / max(len(upstream), 1)
        features['upstream_negative_charge'] = sum(upstream.count(aa) for aa in negative_aa) / max(len(upstream), 1)
        features['downstream_positive_charge'] = sum(downstream.count(aa) for aa in positive_aa) / max(len(downstream), 1)
        features['downstream_negative_charge'] = sum(downstream.count(aa) for aa in negative_aa) / max(len(downstream), 1)
        
        # Polarity in context
        polar_aa = 'STNQ'
        features['upstream_polarity'] = sum(upstream.count(aa) for aa in polar_aa) / max(len(upstream), 1)
        features['downstream_polarity'] = sum(downstream.count(aa) for aa in polar_aa) / max(len(downstream), 1)
        
        # Size in context
        large_aa = 'FWYREKQH'
        features['upstream_size'] = sum(upstream.count(aa) for aa in large_aa) / max(len(upstream), 1)
        features['downstream_size'] = sum(downstream.count(aa) for aa in large_aa) / max(len(downstream), 1)
        
        # Conservation score (simplified - would use actual conservation data)
        features['conservation_score'] = 0.5  # Placeholder
        
        # Secondary structure prediction (simplified)
        features['predicted_secondary_structure'] = 0.33  # Placeholder (helix/sheet/loop)
        
        return features
    
    # ==================== MUTATION-SPECIFIC FEATURES ====================
    
    def extract_mutation_features(self, original_aa: str, predicted_aa: str, 
                                  position: int, sequence: Optional[str] = None) -> Dict[str, float]:
        """Extract features specific to the mutation"""
        features = {}
        
        # Amino acid properties
        aa_properties = {
            'A': {'hydrophobic': 1, 'charge': 0, 'polarity': 0, 'size': 1, 'aromatic': 0},
            'C': {'hydrophobic': 0, 'charge': 0, 'polarity': 1, 'size': 1, 'aromatic': 0},
            'D': {'hydrophobic': 0, 'charge': -1, 'polarity': 1, 'size': 1, 'aromatic': 0},
            'E': {'hydrophobic': 0, 'charge': -1, 'polarity': 1, 'size': 2, 'aromatic': 0},
            'F': {'hydrophobic': 1, 'charge': 0, 'polarity': 0, 'size': 2, 'aromatic': 1},
            'G': {'hydrophobic': 0, 'charge': 0, 'polarity': 0, 'size': 0, 'aromatic': 0},
            'H': {'hydrophobic': 0, 'charge': 1, 'polarity': 1, 'size': 2, 'aromatic': 1},
            'I': {'hydrophobic': 1, 'charge': 0, 'polarity': 0, 'size': 2, 'aromatic': 0},
            'K': {'hydrophobic': 0, 'charge': 1, 'polarity': 1, 'size': 2, 'aromatic': 0},
            'L': {'hydrophobic': 1, 'charge': 0, 'polarity': 0, 'size': 2, 'aromatic': 0},
            'M': {'hydrophobic': 1, 'charge': 0, 'polarity': 0, 'size': 2, 'aromatic': 0},
            'N': {'hydrophobic': 0, 'charge': 0, 'polarity': 1, 'size': 1, 'aromatic': 0},
            'P': {'hydrophobic': 0, 'charge': 0, 'polarity': 0, 'size': 1, 'aromatic': 0},
            'Q': {'hydrophobic': 0, 'charge': 0, 'polarity': 1, 'size': 2, 'aromatic': 0},
            'R': {'hydrophobic': 0, 'charge': 1, 'polarity': 1, 'size': 2, 'aromatic': 0},
            'S': {'hydrophobic': 0, 'charge': 0, 'polarity': 1, 'size': 1, 'aromatic': 0},
            'T': {'hydrophobic': 0, 'charge': 0, 'polarity': 1, 'size': 1, 'aromatic': 0},
            'V': {'hydrophobic': 1, 'charge': 0, 'polarity': 0, 'size': 1, 'aromatic': 0},
            'W': {'hydrophobic': 1, 'charge': 0, 'polarity': 0, 'size': 2, 'aromatic': 1},
            'Y': {'hydrophobic': 1, 'charge': 0, 'polarity': 1, 'size': 2, 'aromatic': 1},
        }
        
        orig_props = aa_properties.get(original_aa, {})
        pred_props = aa_properties.get(predicted_aa, {})
        
        # Property changes
        features['charge_change'] = abs(orig_props.get('charge', 0) - pred_props.get('charge', 0))
        features['size_change'] = abs(orig_props.get('size', 1) - pred_props.get('size', 1))
        features['hydrophobicity_change'] = abs(orig_props.get('hydrophobic', 0) - pred_props.get('hydrophobic', 0))
        features['polarity_change'] = abs(orig_props.get('polarity', 0) - pred_props.get('polarity', 0))
        features['aromaticity_change'] = abs(orig_props.get('aromatic', 0) - pred_props.get('aromatic', 0))
        
        # Original and predicted properties
        features['orig_hydrophobic'] = orig_props.get('hydrophobic', 0)
        features['orig_charge'] = orig_props.get('charge', 0)
        features['orig_polarity'] = orig_props.get('polarity', 0)
        features['orig_size'] = orig_props.get('size', 1)
        features['orig_aromatic'] = orig_props.get('aromatic', 0)
        
        features['pred_hydrophobic'] = pred_props.get('hydrophobic', 0)
        features['pred_charge'] = pred_props.get('charge', 0)
        features['pred_polarity'] = pred_props.get('polarity', 0)
        features['pred_size'] = pred_props.get('size', 1)
        features['pred_aromatic'] = pred_props.get('aromatic', 0)
        
        # Position features
        features['position_normalized'] = position / 1000.0
        features['is_hotspot'] = 1 if position in [484, 501, 417, 452, 614, 681, 478] else 0
        
        # Add sequence context if available
        if sequence:
            context_features = self.extract_sequence_context(sequence, position)
            features.update(context_features)
        
        return features
    
    # ==================== ADME-SPECIFIC FEATURES ====================
    
    def extract_adme_features(self, smiles: str) -> Dict[str, float]:
        """Extract ADME-specific molecular descriptors"""
        features = {}
        
        if not self.rdkit_available:
            return features
        
        try:
            mol = self._get_mol(smiles)
            if mol is None:
                return features
            
            # 1. Permeability-related features
            features['polar_surface_area'] = Descriptors.TPSA(mol)
            features['rotatable_bonds'] = Descriptors.NumRotatableBonds(mol)
            features['flexibility'] = features['rotatable_bonds'] / max(1, mol.GetNumAtoms())
            
            # 2. Solubility predictors
            features['aromatic_ratio'] = Descriptors.NumAromaticRings(mol) / max(1, Descriptors.RingCount(mol))
            features['heteroatom_ratio'] = Descriptors.NumHeteroatoms(mol) / max(1, mol.GetNumAtoms())
            features['hbd_count'] = Descriptors.NumHDonors(mol)
            features['hba_count'] = Descriptors.NumHAcceptors(mol)
            features['hbd_hba_ratio'] = features['hbd_count'] / max(1, features['hba_count'])
            
            # 3. Metabolism-related
            features['cyp_substrate_likeness'] = self._calculate_cyp_likeness(mol)
            features['metabolic_soft_spots'] = self._count_metabolic_soft_spots(mol)
            features['ester_bonds'] = self._count_ester_bonds(mol)
            features['amide_bonds'] = rdMolDescriptors.CalcNumAmideBonds(mol)
            
            # 4. Protein binding predictors
            features['lipophilicity'] = Descriptors.MolLogP(mol)
            features['molecular_volume'] = Descriptors.MolMR(mol)
            features['charge_density'] = Descriptors.FpDensityMorgan1(mol)
            
            # 5. Clearance predictors
            features['molecular_complexity'] = Descriptors.BertzCT(mol)
            features['ring_complexity'] = Descriptors.RingCount(mol) * Descriptors.NumAromaticRings(mol)
            
            # 6. Half-life predictors
            features['metabolic_stability_score'] = self._calculate_metabolic_stability(mol)
            features['plasma_stability'] = self._estimate_plasma_stability(mol)
            
            # 7. Absorption predictors (Lipinski + Veber)
            features['lipinski_violations'] = self._count_lipinski_violations(mol)
            features['veber_pass'] = 1 if (features['rotatable_bonds'] <= 10 and features['polar_surface_area'] <= 140) else 0
            
            # 8. Distribution predictors
            features['vd_prediction'] = self._estimate_volume_distribution(mol)
            features['ppb_prediction'] = self._estimate_protein_binding(mol)
            
        except Exception as e:
            logger.warning(f"Error extracting ADME features: {e}")
        
        return features
    
    def extract_toxicity_features(self, smiles: str) -> Dict[str, float]:
        """Extract toxicity-specific molecular descriptors"""
        features = {}
        
        if not self.rdkit_available:
            return features
        
        try:
            mol = self._get_mol(smiles)
            if mol is None:
                return features
            
            # 1. Ames mutagenicity predictors
            features['mutagenic_alerts'] = self._count_mutagenic_alerts(mol)
            features['aromatic_amines'] = self._count_aromatic_amines(mol)
            features['nitro_groups'] = self._count_nitro_groups(mol)
            features['azo_groups'] = self._count_azo_groups(mol)
            features['aldehyde_groups'] = self._count_aldehyde_groups(mol)
            
            # 2. hERG channel blockers
            features['herg_risk_score'] = self._calculate_herg_risk(mol)
            features['basic_nitrogen_count'] = self._count_basic_nitrogens(mol)
            features['aromatic_ring_count'] = Descriptors.NumAromaticRings(mol)
            features['herg_lipophilicity'] = Descriptors.MolLogP(mol)  # High logP = higher risk
            
            # 3. General toxicity indicators
            features['reactive_groups'] = self._count_reactive_groups(mol)
            features['electrophilic_sites'] = self._count_electrophilic_sites(mol)
            features['nucleophilic_sites'] = self._count_nucleophilic_sites(mol)
            
            # 4. Structural alerts
            features['structural_alerts'] = self._count_structural_alerts(mol)
            features['toxicophore_count'] = self._count_toxicophores(mol)
            
        except Exception as e:
            logger.warning(f"Error extracting toxicity features: {e}")
        
        return features
    
    # ==================== MODIFICATION-SPECIFIC FEATURES ====================
    
    def extract_modification_structural_features(self, base_smiles: str, 
                                                modified_smiles: str,
                                                modification_type: str) -> Dict[str, float]:
        """Extract features for predicting structural/binding effects of modifications"""
        features = {}
        
        if not self.rdkit_available:
            return features
        
        try:
            base_mol = self._get_mol(base_smiles)
            mod_mol = self._get_mol(modified_smiles)
            
            if base_mol is None or mod_mol is None:
                return features
            
            # 1. Structural change magnitude
            features['mw_change'] = Descriptors.MolWt(mod_mol) - Descriptors.MolWt(base_mol)
            features['logp_change'] = Descriptors.MolLogP(mod_mol) - Descriptors.MolLogP(base_mol)
            features['tpsa_change'] = Descriptors.TPSA(mod_mol) - Descriptors.TPSA(base_mol)
            
            # 2. Conformational changes
            features['rotatable_bonds_change'] = (
                Descriptors.NumRotatableBonds(mod_mol) - 
                Descriptors.NumRotatableBonds(base_mol)
            )
            features['ring_count_change'] = (
                Descriptors.RingCount(mod_mol) - 
                Descriptors.RingCount(base_mol)
            )
            
            # 3. Electronic properties
            features['dipole_change'] = self._estimate_dipole_change(base_mol, mod_mol)
            features['homo_lumo_gap_change'] = self._estimate_homo_lumo_change(base_mol, mod_mol)
            
            # 4. Binding site accessibility
            features['binding_site_accessibility'] = self._calculate_binding_accessibility(mod_mol)
            features['hydrophobic_surface_change'] = self._calculate_hydrophobic_surface_change(base_mol, mod_mol)
            features['polar_surface_change'] = Descriptors.TPSA(mod_mol) - Descriptors.TPSA(base_mol)
            
            # 5. Modification-specific features
            if modification_type == 'Fluorination':
                features['fluorine_count'] = modified_smiles.count('F')
                features['electron_withdrawing_effect'] = 0.5
            elif modification_type == 'Methylation':
                features['methyl_groups_added'] = 1
                features['steric_hindrance'] = 0.3
            elif modification_type == 'Hydroxylation':
                features['hydroxyl_groups_added'] = 1
                features['hydrogen_bonding_capacity'] = 1.0
            elif modification_type == 'Chlorination':
                features['chlorine_count'] = modified_smiles.count('Cl')
                features['lipophilicity_increase'] = 0.7
            
            # 6. Structural stability indicators
            features['strain_energy_change'] = self._estimate_strain_energy_change(base_mol, mod_mol)
            features['torsional_strain'] = self._calculate_torsional_strain(mod_mol)
            
            # 7. Binding affinity predictors
            features['binding_affinity_score'] = self._estimate_binding_affinity_change(
                base_mol, mod_mol, modification_type
            )
            features['interaction_potential'] = self._calculate_interaction_potential(mod_mol)
            
        except Exception as e:
            logger.warning(f"Error extracting structural features: {e}")
        
        return features
    
    # ==================== HELPER METHODS FOR ADME/TOXICITY ====================
    
    def _get_mol(self, smiles: str):
        """Get molecule object with caching for performance"""
        if smiles in self._mol_cache:
            return self._mol_cache[smiles]
        
        if not self.rdkit_available:
            return None
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is not None:
                # Limit cache size to prevent memory issues
                if len(self._mol_cache) >= self.cache_size:
                    # Remove oldest entry (simple FIFO)
                    oldest_key = next(iter(self._mol_cache))
                    del self._mol_cache[oldest_key]
                self._mol_cache[smiles] = mol
            return mol
        except Exception:
            return None
    
    def _calculate_cyp_likeness(self, mol) -> float:
        """Calculate CYP450 substrate likelihood"""
        try:
            cyp_patterns = [
                Chem.MolFromSmarts('c1ccccc1'),  # Benzene ring
                Chem.MolFromSmarts('[N+](=O)[O-]'),  # Nitro groups
                Chem.MolFromSmarts('C=O'),  # Carbonyl groups
            ]
            score = 0
            for pattern in cyp_patterns:
                if pattern and mol.HasSubstructMatch(pattern):
                    score += 1
            return float(score)
        except Exception:
            return 0.0
    
    def _count_metabolic_soft_spots(self, mol) -> float:
        """Count metabolic soft spots (easily metabolized groups)"""
        try:
            soft_spots = [
                Chem.MolFromSmarts('CO'),  # Ethers
                Chem.MolFromSmarts('CN'),  # Amines
                Chem.MolFromSmarts('C=O'),  # Carbonyls
                Chem.MolFromSmarts('[OH]'),  # Hydroxyls
            ]
            count = 0
            for pattern in soft_spots:
                if pattern:
                    count += len(mol.GetSubstructMatches(pattern))
            return float(count)
        except Exception:
            return 0.0
    
    def _count_ester_bonds(self, mol) -> float:
        """Count ester bonds"""
        try:
            pattern = Chem.MolFromSmarts('C(=O)O')
            if pattern:
                return float(len(mol.GetSubstructMatches(pattern)))
            return 0.0
        except Exception:
            return 0.0
    
    def _calculate_metabolic_stability(self, mol) -> float:
        """Calculate metabolic stability score"""
        try:
            # Higher complexity = more stable
            complexity = Descriptors.BertzCT(mol)
            # Fewer soft spots = more stable
            soft_spots = self._count_metabolic_soft_spots(mol)
            stability = complexity / max(1, soft_spots + 1)
            return float(stability)
        except Exception:
            return 0.0
    
    def _estimate_plasma_stability(self, mol) -> float:
        """Estimate plasma stability"""
        try:
            # Based on ester bonds and metabolic soft spots
            ester_bonds = self._count_ester_bonds(mol)
            soft_spots = self._count_metabolic_soft_spots(mol)
            stability = 1.0 / max(1, ester_bonds + soft_spots)
            return float(stability)
        except Exception:
            return 0.5
    
    def _count_lipinski_violations(self, mol) -> float:
        """Count Lipinski's Rule of Five violations"""
        try:
            violations = 0
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            hbd = Descriptors.NumHDonors(mol)
            hba = Descriptors.NumHAcceptors(mol)
            
            if mw > 500:
                violations += 1
            if logp > 5:
                violations += 1
            if hbd > 5:
                violations += 1
            if hba > 10:
                violations += 1
            
            return float(violations)
        except Exception:
            return 0.0
    
    def _estimate_volume_distribution(self, mol) -> float:
        """Estimate volume of distribution"""
        try:
            logp = Descriptors.MolLogP(mol)
            mw = Descriptors.MolWt(mol)
            # Higher logP and MW = higher Vd
            vd = (logp * 0.5) + (mw / 1000)
            return float(vd)
        except Exception:
            return 0.5
    
    def _estimate_protein_binding(self, mol) -> float:
        """Estimate plasma protein binding"""
        try:
            logp = Descriptors.MolLogP(mol)
            aromatic_rings = Descriptors.NumAromaticRings(mol)
            # Higher logP and aromatic rings = higher PPB
            ppb = (logp * 5) + (aromatic_rings * 10)
            return float(min(ppb, 100))
        except Exception:
            return 50.0
    
    def _count_mutagenic_alerts(self, mol) -> float:
        """Count mutagenic structural alerts"""
        try:
            patterns = [
                Chem.MolFromSmarts('[N+](=O)[O-]'),  # Nitro groups
                Chem.MolFromSmarts('c1ccc(N)cc1'),  # Aromatic amines
                Chem.MolFromSmarts('C=O'),  # Aldehydes
            ]
            count = 0
            for pattern in patterns:
                if pattern and mol.HasSubstructMatch(pattern):
                    count += 1
            return float(count)
        except Exception:
            return 0.0
    
    def _count_aromatic_amines(self, mol) -> float:
        """Count aromatic amine groups"""
        try:
            pattern = Chem.MolFromSmarts('c1ccc(N)cc1')
            if pattern:
                return float(len(mol.GetSubstructMatches(pattern)))
            return 0.0
        except Exception:
            return 0.0
    
    def _count_nitro_groups(self, mol) -> float:
        """Count nitro groups"""
        try:
            pattern = Chem.MolFromSmarts('[N+](=O)[O-]')
            if pattern:
                return float(len(mol.GetSubstructMatches(pattern)))
            return 0.0
        except Exception:
            return 0.0
    
    def _count_azo_groups(self, mol) -> float:
        """Count azo groups"""
        try:
            pattern = Chem.MolFromSmarts('N=N')
            if pattern:
                return float(len(mol.GetSubstructMatches(pattern)))
            return 0.0
        except Exception:
            return 0.0
    
    def _count_aldehyde_groups(self, mol) -> float:
        """Count aldehyde groups"""
        try:
            pattern = Chem.MolFromSmarts('[CX3H1](=O)')
            if pattern:
                return float(len(mol.GetSubstructMatches(pattern)))
            return 0.0
        except Exception:
            return 0.0
    
    def _calculate_herg_risk(self, mol) -> float:
        """Calculate hERG channel blocking risk"""
        try:
            basic_n = self._count_basic_nitrogens(mol)
            aromatic = Descriptors.NumAromaticRings(mol)
            logp = Descriptors.MolLogP(mol)
            
            risk = (basic_n * 0.3) + (aromatic * 0.2) + (max(0, logp - 2) * 0.1)
            return float(min(risk, 1.0))  # Normalize to 0-1
        except Exception:
            return 0.0
    
    def _count_basic_nitrogens(self, mol) -> float:
        """Count basic nitrogen atoms"""
        try:
            # Count nitrogens in amines
            pattern = Chem.MolFromSmarts('[N;H2,H1;!$(N=*);!$(N#*)]')
            if pattern:
                return float(len(mol.GetSubstructMatches(pattern)))
            return 0.0
        except Exception:
            return 0.0
    
    def _count_reactive_groups(self, mol) -> float:
        """Count reactive groups"""
        try:
            reactive_patterns = [
                Chem.MolFromSmarts('C=O'),  # Carbonyls
                Chem.MolFromSmarts('[Cl,Br,I]'),  # Halogens
                Chem.MolFromSmarts('C#N'),  # Nitriles
            ]
            count = 0
            for pattern in reactive_patterns:
                if pattern:
                    count += len(mol.GetSubstructMatches(pattern))
            return float(count)
        except Exception:
            return 0.0
    
    def _count_electrophilic_sites(self, mol) -> float:
        """Count electrophilic sites"""
        try:
            patterns = [
                Chem.MolFromSmarts('C=O'),  # Carbonyls
                Chem.MolFromSmarts('C(=O)Cl'),  # Acid chlorides
            ]
            count = 0
            for pattern in patterns:
                if pattern:
                    count += len(mol.GetSubstructMatches(pattern))
            return float(count)
        except Exception:
            return 0.0
    
    def _count_nucleophilic_sites(self, mol) -> float:
        """Count nucleophilic sites"""
        try:
            patterns = [
                Chem.MolFromSmarts('[OH]'),  # Hydroxyls
                Chem.MolFromSmarts('[NH2]'),  # Amines
            ]
            count = 0
            for pattern in patterns:
                if pattern:
                    count += len(mol.GetSubstructMatches(pattern))
            return float(count)
        except Exception:
            return 0.0
    
    def _count_structural_alerts(self, mol) -> float:
        """Count structural alerts"""
        try:
            alerts = (
                self._count_mutagenic_alerts(mol) +
                self._count_reactive_groups(mol) +
                self._count_electrophilic_sites(mol)
            )
            return float(alerts)
        except Exception:
            return 0.0
    
    def _count_toxicophores(self, mol) -> float:
        """Count toxicophore patterns"""
        try:
            toxicophores = (
                self._count_aromatic_amines(mol) +
                self._count_nitro_groups(mol) +
                self._count_azo_groups(mol)
            )
            return float(toxicophores)
        except Exception:
            return 0.0
    
    # ==================== HELPER METHODS FOR MODIFICATIONS ====================
    
    def _estimate_dipole_change(self, base_mol, mod_mol) -> float:
        """Estimate dipole moment change"""
        try:
            # Simplified: based on polar surface area change
            base_tpsa = Descriptors.TPSA(base_mol)
            mod_tpsa = Descriptors.TPSA(mod_mol)
            return float(mod_tpsa - base_tpsa) / 100.0
        except Exception:
            return 0.0
    
    def _estimate_homo_lumo_change(self, base_mol, mod_mol) -> float:
        """Estimate HOMO-LUMO gap change"""
        try:
            # Simplified: based on aromaticity and conjugation
            base_aromatic = Descriptors.NumAromaticRings(base_mol)
            mod_aromatic = Descriptors.NumAromaticRings(mod_mol)
            return float(mod_aromatic - base_aromatic) * 0.1
        except Exception:
            return 0.0
    
    def _calculate_binding_accessibility(self, mod_mol) -> float:
        """Calculate binding site accessibility"""
        try:
            # Based on molecular size and flexibility
            mw = Descriptors.MolWt(mod_mol)
            rot_bonds = Descriptors.NumRotatableBonds(mod_mol)
            accessibility = (rot_bonds / max(1, mw / 100)) * 10
            return float(accessibility)
        except Exception:
            return 0.5
    
    def _calculate_hydrophobic_surface_change(self, base_mol, mod_mol) -> float:
        """Calculate hydrophobic surface area change"""
        try:
            base_logp = Descriptors.MolLogP(base_mol)
            mod_logp = Descriptors.MolLogP(mod_mol)
            return float(mod_logp - base_logp) * 10
        except Exception:
            return 0.0
    
    def _estimate_strain_energy_change(self, base_mol, mod_mol) -> float:
        """Estimate strain energy change"""
        try:
            base_complexity = Descriptors.BertzCT(base_mol)
            mod_complexity = Descriptors.BertzCT(mod_mol)
            return float(mod_complexity - base_complexity) / 100.0
        except Exception:
            return 0.0
    
    def _calculate_torsional_strain(self, mod_mol) -> float:
        """Calculate torsional strain"""
        try:
            rot_bonds = Descriptors.NumRotatableBonds(mod_mol)
            rings = Descriptors.RingCount(mod_mol)
            strain = rot_bonds / max(1, rings + 1)
            return float(strain)
        except Exception:
            return 0.0
    
    def _estimate_binding_affinity_change(self, base_mol, mod_mol, mod_type: str) -> float:
        """Estimate binding affinity change"""
        try:
            base_logp = Descriptors.MolLogP(base_mol)
            mod_logp = Descriptors.MolLogP(mod_mol)
            logp_change = mod_logp - base_logp
            
            # Different modifications have different effects
            if mod_type == 'Fluorination':
                return float(logp_change * 0.5 - 0.5)  # Generally improves
            elif mod_type == 'Methylation':
                return float(logp_change * 0.3 - 0.3)
            else:
                return float(logp_change * 0.2 - 0.2)
        except Exception:
            return 0.0
    
    def _calculate_interaction_potential(self, mod_mol) -> float:
        """Calculate interaction potential"""
        try:
            hbd = Descriptors.NumHDonors(mod_mol)
            hba = Descriptors.NumHAcceptors(mod_mol)
            aromatic = Descriptors.NumAromaticRings(mod_mol)
            potential = (hbd + hba) * 0.1 + aromatic * 0.2
            return float(potential)
        except Exception:
            return 0.0
    
    # ==================== COMBINED FEATURE EXTRACTION ====================
    
    def extract_all_features(self, data_type: str, **kwargs) -> Dict[str, float]:
        """Extract all features based on data type"""
        if data_type == 'mutation':
            return self.extract_mutation_features(
                kwargs.get('original_aa'),
                kwargs.get('predicted_aa'),
                kwargs.get('position'),
                kwargs.get('sequence')
            )
        elif data_type == 'drug':
            # Combine basic, ADME, and toxicity features for drugs
            smiles = kwargs.get('smiles', '')
            features = {}
            features.update(self.extract_rdkit_features(smiles))
            features.update(self.extract_adme_features(smiles))
            features.update(self.extract_toxicity_features(smiles))
            return features
        elif data_type == 'modification':
            base_smiles = kwargs.get('base_smiles', '')
            modified_smiles = kwargs.get('modified_smiles', '')
            mod_type = kwargs.get('modification_type', '')
            
            # Combine base and modified features with structural features
            combined = {}
            base_features = self.extract_rdkit_features(base_smiles)
            mod_features = self.extract_rdkit_features(modified_smiles)
            structural_features = self.extract_modification_structural_features(
                base_smiles, modified_smiles, mod_type
            )
            
            # Add base and modified features
            for key in base_features:
                combined[f'base_{key}'] = base_features[key]
                if key in mod_features:
                    combined[f'mod_{key}'] = mod_features[key]
                    combined[f'delta_{key}'] = mod_features[key] - base_features[key]
            
            # Add structural modification features
            combined.update(structural_features)
            return combined
        else:
            return {}
    
    def extract_features_batch(self, data_type: str, data_list: List[Dict]) -> List[Dict[str, float]]:
        """Extract features for multiple molecules in parallel (faster)"""
        if not data_list:
            return []
        
        # Use ThreadPoolExecutor for parallel processing
        max_workers = min(4, len(data_list))  # Limit to 4 workers
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for data in data_list:
                if data_type == 'drug':
                    future = executor.submit(
                        self.extract_all_features, 
                        'drug', 
                        smiles=data.get('smiles', '')
                    )
                elif data_type == 'modification':
                    future = executor.submit(
                        self.extract_all_features,
                        'modification',
                        base_smiles=data.get('base_smiles', ''),
                        modified_smiles=data.get('modified_smiles', ''),
                        modification_type=data.get('modification_type', '')
                    )
                else:
                    future = executor.submit(lambda: {})
                futures.append(future)
            
            # Collect results
            results = []
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.warning(f"Error in parallel feature extraction: {e}")
                    results.append({})
        
        return results


if __name__ == "__main__":
    engineer = EnhancedFeatureEngineer()
    
    # Test molecular features
    test_smiles = "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"
    mol_features = engineer.extract_rdkit_features(test_smiles)
    print(f"Molecular features extracted: {len(mol_features)} features")
    print(f"Sample features: {list(mol_features.items())[:10]}")
    
    # Test mutation features
    mut_features = engineer.extract_mutation_features('E', 'K', 484, 'ATGGCTAGCTAGCTAG')
    print(f"\nMutation features extracted: {len(mut_features)} features")
    print(f"Sample features: {list(mut_features.items())[:10]}")

