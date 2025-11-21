-- Migration: Add virus_type and sequence_data to projects table
-- Created: 2025-11-20
-- Description: Add columns for virus type selection and sequence data storage

-- For SQLite
ALTER TABLE projects ADD COLUMN virus_type VARCHAR(50);
ALTER TABLE projects ADD COLUMN sequence_data TEXT;

-- Create index on virus_type for faster queries
CREATE INDEX IF NOT EXISTS idx_projects_virus_type ON projects(virus_type);

