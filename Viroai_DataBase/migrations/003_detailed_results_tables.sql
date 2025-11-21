-- Migration: Detailed Results Storage
-- Created: 2025-11-20
-- Description: Create comprehensive result storage tables for mutations, drugs, and modifications

-- Mutation Detailed Results Table
CREATE TABLE IF NOT EXISTS mutation_detailed_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    mutation_id VARCHAR(50) NOT NULL,
    position VARCHAR(50),
    original_aa VARCHAR(10),
    predicted_aa VARCHAR(10),
    probability FLOAT,
    
    -- Section 1: Genomic Level
    genomic_level JSON,
    
    -- Section 2: Probability Metrics
    probability_metrics JSON,
    
    -- Section 3: Selective Pressure
    selective_pressure JSON,
    
    -- Section 4: Structural Consequences
    structural_consequences JSON,
    
    -- Section 5: Receptor Binding
    receptor_binding JSON,
    
    -- Section 6: Immune Evasion
    immune_evasion JSON,
    
    -- Section 7: Viral Fitness
    viral_fitness JSON,
    
    -- Section 8: Pathogenicity
    pathogenicity JSON,
    
    -- Section 9: Lineage Emergence
    lineage_emergence JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_mutation_id (mutation_id)
);

-- Drug Detailed Results Table
CREATE TABLE IF NOT EXISTS drug_detailed_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    compound_name VARCHAR(255) NOT NULL,
    smiles TEXT,
    rank_position INT,
    overall_score FLOAT,
    
    -- Section 1: Molecular Identity
    molecular_identity JSON,
    
    -- Section 2: Binding Metrics
    binding_metrics JSON,
    
    -- Section 3: Interaction Map
    interaction_map JSON,
    
    -- Section 4: Structural Stability
    structural_stability JSON,
    
    -- Section 5: Physicochemical Properties
    physicochemical JSON,
    
    -- Section 6: ADME Predictions
    adme JSON,
    
    -- Section 7: Toxicology
    toxicology JSON,
    
    -- Section 8: Comparative Scores
    comparative_scores JSON,
    
    -- Section 9: Ensemble Analysis
    ensemble_analysis JSON,
    
    -- Section 10: Resistance Vulnerability
    resistance_vulnerability JSON,
    
    -- Section 11: Chemical Diversity
    chemical_diversity JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_compound_name (compound_name),
    INDEX idx_rank (rank_position)
);

-- Modification Detailed Results Table
CREATE TABLE IF NOT EXISTS modification_detailed_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    modification_id VARCHAR(50) NOT NULL,
    base_compound_id INT,
    base_formula VARCHAR(100),
    modified_formula VARCHAR(100),
    
    -- Section 1: Modification Identity
    modification_identity JSON,
    
    -- Section 2: Structural Effects
    structural_effects JSON,
    
    -- Section 3: Physicochemical Changes
    physicochemical_changes JSON,
    
    -- Section 4: Binding Affinity Effects
    binding_affinity_effects JSON,
    
    -- Section 5: Electronic Effects
    electronic_effects JSON,
    
    -- Section 6: Stability & Degradation
    stability_degradation JSON,
    
    -- Section 7: Solubility & Permeability
    solubility_permeability JSON,
    
    -- Section 8: ADME Shifts
    adme_shifts JSON,
    
    -- Section 9: Toxicity Signatures
    toxicity_signatures JSON,
    
    -- Section 10: Synthetic Feasibility
    synthetic_feasibility JSON,
    
    -- Section 11: Comparative Scoring
    comparative_scoring JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (base_compound_id) REFERENCES drug_detailed_results(id) ON DELETE SET NULL,
    INDEX idx_project_id (project_id),
    INDEX idx_modification_id (modification_id)
);

