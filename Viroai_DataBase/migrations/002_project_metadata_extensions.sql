-- Migration: Project Metadata Extensions
-- Created: 2025-11-20
-- Description: Add geolocation, clinical metadata, and file tracking to projects

ALTER TABLE projects ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS country VARCHAR(100);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS region VARCHAR(100);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS collection_timestamp TIMESTAMP;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS symptoms TEXT;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS clinical_severity ENUM('asymptomatic', 'mild', 'moderate', 'severe', 'critical');
ALTER TABLE projects ADD COLUMN IF NOT EXISTS clinical_notes TEXT;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS protein_files JSON;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS clinical_files JSON;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS assay_files JSON;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE projects ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

