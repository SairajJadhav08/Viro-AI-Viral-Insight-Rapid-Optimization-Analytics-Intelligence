# Database Migrations for Viro-AI v2.0

## Overview

This directory contains SQL migration scripts to upgrade the Viro-AI database schema from v1.0 to v2.0.

## Migration Files

Migrations are executed in numerical order:

1. **005_base_tables_creation.sql** - Creates base tables (users, projects, settings) if they don't exist
2. **001_user_profile_enhancements.sql** - Adds enhanced profile fields for users
3. **002_project_metadata_extensions.sql** - Adds geolocation and clinical metadata to projects
4. **003_detailed_results_tables.sql** - Creates comprehensive result storage tables
5. **004_research_news_table.sql** - Creates research news feed table

## Running Migrations

### Automatic Migration

```bash
cd Viroai_DataBase/migrations
python run_migrations.py
```

### Check Status

```bash
python run_migrations.py status
```

## Features

- **Automatic Backup**: Creates database backup before running migrations
- **Migration History**: Tracks executed migrations to prevent re-execution
- **Rollback Support**: Backup files stored in `backups/` directory
- **Error Handling**: Stops on first error, allowing manual intervention

## Backup & Rollback

Backups are automatically created in the `backups/` directory with timestamps:
- Format: `backup_YYYYMMDD_HHMMSS.db`

To rollback, simply restore from a backup file.

## Migration History

The file `migration_history.json` tracks:
- List of executed migrations
- Timestamp of last migration
- Migration status

## Database Schema Changes

### Users Table
- Added profile fields: qualification, occupation, professional_summary
- Added JSON fields: skills, experience, publications, awards, social_links
- Added avatar_url for profile pictures

### Projects Table
- Added geolocation: latitude, longitude, country, region
- Added clinical metadata: symptoms, clinical_severity, clinical_notes
- Added file tracking: protein_files, clinical_files, assay_files
- Added collection_timestamp

### New Tables
- **mutation_detailed_results**: 9-section comprehensive mutation analysis
- **drug_detailed_results**: 11-section drug candidate analysis
- **modification_detailed_results**: 11-section chemical modification analysis
- **research_news**: News feed for Explore page
- **user_settings**: User preferences and settings

## Notes

- Migrations use `IF NOT EXISTS` clauses to be idempotent
- JSON columns store complex nested data structures
- All tables include timestamps (created_at, updated_at)
- Foreign keys ensure referential integrity with CASCADE deletes

