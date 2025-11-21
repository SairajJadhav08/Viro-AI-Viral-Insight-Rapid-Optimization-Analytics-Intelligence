"""
Script to check the status of the latest SARS-CoV-2 project
"""
import sqlite3
from pathlib import Path
from datetime import datetime

db_path = Path("Viroai_DataBase/viroai.db")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get the latest project
cursor.execute("""
    SELECT 
        id, title, status, description, 
        mutations_count, drugs_count, modifications_count, 
        deadliness_score, created_at, updated_at,
        country, region, collection_timestamp,
        symptoms, clinical_severity
    FROM projects 
    WHERE title LIKE '%SARS%' OR title LIKE '%CoV%'
    ORDER BY created_at DESC 
    LIMIT 1
""")

project = cursor.fetchone()

if project:
    print("=" * 70)
    print("SARS-CoV-2 PROJECT STATUS REPORT")
    print("=" * 70)
    print(f"\nProject ID: {project[0]}")
    print(f"Title: {project[1]}")
    print(f"Status: {project[2]}")
    print(f"Description: {project[3] or 'N/A'}")
    print(f"\nResult Counts:")
    print(f"  Mutations: {project[4]}")
    print(f"  Drugs: {project[5]}")
    print(f"  Modifications: {project[6]}")
    print(f"  Deadliness Score: {project[7] or 'N/A'}")
    print(f"\nLocation:")
    print(f"  Country: {project[10] or 'N/A'}")
    print(f"  Region: {project[11] or 'N/A'}")
    print(f"  Collection Timestamp: {project[12] or 'N/A'}")
    print(f"\nClinical Data:")
    print(f"  Symptoms: {project[13] or 'N/A'}")
    print(f"  Clinical Severity: {project[14] or 'N/A'}")
    print(f"\nTimestamps:")
    print(f"  Created: {project[8]}")
    print(f"  Updated: {project[9]}")
    
    # Check if results exist in database
    project_id = project[0]
    cursor.execute("SELECT COUNT(*) FROM mutation_results WHERE project_id = ?", (project_id,))
    mut_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM drug_candidate_results WHERE project_id = ?", (project_id,))
    drug_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM modification_results WHERE project_id = ?", (project_id,))
    mod_count = cursor.fetchone()[0]
    
    print(f"\n" + "=" * 70)
    print("RESULTS IN DATABASE:")
    print("=" * 70)
    print(f"  Mutations in mutation_results table: {mut_count}")
    print(f"  Drugs in drug_candidate_results table: {drug_count}")
    print(f"  Modifications in modification_results table: {mod_count}")
    
    if project[2] == "Processing" and mut_count == 0 and drug_count == 0 and mod_count == 0:
        print(f"\n⚠️  WARNING: Project is still in 'Processing' status but no results found.")
        print(f"   This may indicate:")
        print(f"   1. Background processing is still running")
        print(f"   2. Processing encountered an error")
        print(f"   3. Processing hasn't started yet")
    
    if project[2] == "Completed" and (mut_count > 0 or drug_count > 0 or mod_count > 0):
        print(f"\n✅ Project processing completed successfully!")
    
    if project[2] == "Failed":
        print(f"\n❌ Project processing failed. Check backend logs for errors.")
else:
    print("No SARS-CoV-2 project found in database.")

conn.close()

