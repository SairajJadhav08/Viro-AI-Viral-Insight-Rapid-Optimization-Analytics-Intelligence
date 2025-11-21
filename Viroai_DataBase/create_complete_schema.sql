-- ============================================================
-- VIRO-AI v2.0 - Complete Database Schema
-- Creates all required tables with all columns
-- ============================================================

-- Drop existing tables if they exist (fresh start)
DROP TABLE IF EXISTS modification_results;
DROP TABLE IF EXISTS drug_candidate_results;
DROP TABLE IF EXISTS mutation_results;
DROP TABLE IF EXISTS research_news;
DROP TABLE IF EXISTS user_settings;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

-- ============================================================
-- USERS TABLE - With ALL required columns
-- ============================================================
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Basic auth fields
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50),
    role VARCHAR(100),
    is_active INTEGER DEFAULT 1,  -- CRITICAL: Required by auth.py
    
    -- Profile enhancement fields (from migration 001)
    qualification VARCHAR(255),
    occupation VARCHAR(255),
    professional_summary TEXT,
    skills TEXT,  -- JSON stored as text
    experience TEXT,  -- JSON stored as text
    publications TEXT,  -- JSON stored as text
    awards TEXT,  -- JSON stored as text
    social_links TEXT,  -- JSON stored as text
    avatar_url TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for faster lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- ============================================================
-- USER SETTINGS TABLE - Required by auth.py line 132
-- ============================================================
CREATE TABLE user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- Notification settings
    email_notifications INTEGER DEFAULT 1,
    analysis_complete_alerts INTEGER DEFAULT 1,
    research_updates INTEGER DEFAULT 0,
    
    -- Display settings
    theme VARCHAR(50) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'en',
    
    -- Privacy settings
    data_sharing INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_settings_user_id ON user_settings(user_id);

-- ============================================================
-- PROJECTS TABLE - With extended metadata
-- ============================================================
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- Basic project info
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Pending',  -- Pending, Processing, Completed, Failed
    
    -- Geolocation data (from migration 002)
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    country VARCHAR(100),
    region VARCHAR(100),
    
    -- Clinical data (from migration 002)
    collection_timestamp TIMESTAMP,
    symptoms TEXT,
    clinical_severity VARCHAR(50),  -- asymptomatic, mild, moderate, severe, critical
    clinical_notes TEXT,
    
    -- File paths
    protein_files TEXT,  -- JSON array stored as text
    clinical_files TEXT,  -- JSON array stored as text
    assay_files TEXT,  -- JSON array stored as text
    
    -- Result counts (for History page)
    mutations_count INTEGER DEFAULT 0,
    drugs_count INTEGER DEFAULT 0,
    modifications_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);

-- ============================================================
-- MUTATION RESULTS TABLE - 9-section detailed analysis
-- ============================================================
CREATE TABLE mutation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    
    -- Basic mutation info
    mutation_position VARCHAR(50) NOT NULL,
    original_amino_acid CHAR(1) NOT NULL,
    predicted_amino_acid CHAR(1) NOT NULL,
    probability DECIMAL(5, 2),
    effect TEXT,
    risk_level VARCHAR(50),  -- Low, Medium, High
    
    -- 9-section detailed analysis (stored as JSON text)
    genomic_level TEXT,  -- JSON: nucleotideSubstitution, mutationType, etc.
    probability_metrics TEXT,  -- JSON: aiScore, historicalFrequency, etc.
    selective_pressure TEXT,  -- JSON: dNdS, conservationScore, etc.
    structural_consequences TEXT,  -- JSON: deltaRMSD, deltaGStability, etc.
    receptor_binding TEXT,  -- JSON: deltaKd, interfaceAlteration, etc.
    immune_evasion TEXT,  -- JSON: bCellEpitope, tCellEpitope, etc.
    viral_fitness TEXT,  -- JSON: replicationEfficiency, virionStability, etc.
    pathogenicity TEXT,  -- JSON: contribution, tropismImpact, etc.
    lineage_emergence TEXT,  -- JSON: newLineageProbability, phylogeneticPathway, etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_mutation_results_project_id ON mutation_results(project_id);

-- ============================================================
-- DRUG CANDIDATE RESULTS TABLE - 11-section analysis
-- ============================================================
CREATE TABLE drug_candidate_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    
    -- Basic drug info
    drug_name VARCHAR(255) NOT NULL,
    smiles TEXT,
    binding_affinity DECIMAL(10, 2),
    ic50 VARCHAR(50),
    logp DECIMAL(10, 2),
    molecular_weight DECIMAL(10, 2),
    formula VARCHAR(255),
    heavy_atoms INTEGER,
    rank INTEGER,
    score INTEGER,
    
    -- 11-section detailed analysis (stored as JSON text)
    molecular_identity TEXT,  -- JSON: chemicalName, uniqueID, inchi, etc.
    binding_metrics TEXT,  -- JSON: bindingEnergy, kd, ki, ic50, etc.
    interaction_map TEXT,  -- JSON: hBonds, hydrophobicContacts, etc.
    structural_stability TEXT,  -- JSON: rmsd, rmsf, mmPBSA, etc.
    physicochemical TEXT,  -- JSON: logP, logS, tPSA, pKa, etc.
    adme TEXT,  -- JSON: absorption, metabolism, distribution, etc.
    toxicology TEXT,  -- JSON: ames, hERG, PAINS, LD50, etc.
    comparative_scores TEXT,  -- JSON: bindingStrength, drugLikeness, etc.
    ensemble_analysis TEXT,  -- JSON: conformationalDiversity, clusterAnalysis, etc.
    resistance_vulnerability TEXT,  -- JSON: mutationSensitivity, crossResistance, etc.
    chemical_diversity TEXT,  -- JSON: scaffoldDiversity, functionalGroups, etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_drug_results_project_id ON drug_candidate_results(project_id);

-- ============================================================
-- MODIFICATION RESULTS TABLE - 11-section analysis
-- ============================================================
CREATE TABLE modification_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    
    -- Basic modification info
    base_formula VARCHAR(255),
    modified_formula VARCHAR(255),
    changes TEXT,
    improvements TEXT,
    confidence DECIMAL(5, 2),
    
    -- 11-section detailed analysis (stored as JSON text)
    modification_identity TEXT,  -- JSON: addedGroups, removedGroups, etc.
    structural_effects TEXT,  -- JSON: deltaRMSD, molecularVolumeChange, etc.
    physicochemical_changes TEXT,  -- JSON: deltaLogP, deltaPKa, etc.
    binding_affinity_effects TEXT,  -- JSON: deltaBindingEnergy, kdImprovement, etc.
    electronic_effects TEXT,  -- JSON: homoLumoGap, dipoleMoment, etc.
    stability_degradation TEXT,  -- JSON: metabolicStability, thermalStability, etc.
    solubility_permeability TEXT,  -- JSON: deltaSolubility, caco2, etc.
    adme_shifts TEXT,  -- JSON: absorptionEfficiency, clearanceRate, etc.
    toxicity_signatures TEXT,  -- JSON: PAINS, mutagenicity, etc.
    synthetic_feasibility TEXT,  -- JSON: sasScore, yieldPrediction, etc.
    comparative_scoring TEXT,  -- JSON: overallViability, costBenefit, etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_modification_results_project_id ON modification_results(project_id);

-- ============================================================
-- RESEARCH NEWS TABLE - For Explore page
-- ============================================================
CREATE TABLE research_news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(512) NOT NULL,
    summary TEXT,
    source VARCHAR(255),
    publish_date DATE,
    tags TEXT,  -- JSON array stored as text
    credibility VARCHAR(100),
    relevance INTEGER,
    link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_research_news_publish_date ON research_news(publish_date);

-- ============================================================
-- SCHEMA MIGRATIONS TABLE - Track applied migrations
-- ============================================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mark all migrations as applied
INSERT INTO schema_migrations (version) VALUES 
    ('000_complete_schema'),
    ('001_user_profile_enhancements'),
    ('002_project_metadata_extensions'),
    ('003_detailed_results_tables'),
    ('004_research_news_table'),
    ('005_base_tables_creation');

-- ============================================================
-- VERIFICATION QUERY
-- ============================================================
-- Run this to verify all tables were created:
-- SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

