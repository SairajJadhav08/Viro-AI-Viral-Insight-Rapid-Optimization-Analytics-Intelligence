# fetch_virus_data_improved.py
from Bio import Entrez
from Bio.PDB import PDBList
import os
import requests
import time

# === CONFIGURATION ===
Entrez.email = "sairajjadhav433@gmail.com"  # Replace with your email
virus_list = ["SARS-CoV-2", "Influenza", "Ebola"]
num_sequences = {"SARS-CoV-2": 1000, "Influenza": 800, "Ebola": 500}

# Base directories (matching actual structure)
genomic_base_dir = "Viroai_DataBase/genomic"
structural_base_dir = "Viroai_DataBase/structural"

# PDB IDs for key viral proteins
pdb_structures = {
    "SARS-CoV-2": {
        "6VXX": "Spike Protein",
        "6VSB": "Spike RBD",
        "7BNN": "Main Protease (Mpro)"
    },
    "Influenza": {
        "1RVX": "Hemagglutinin",
        "4GMS": "Neuraminidase"
    },
    "Ebola": {
        "5JQ3": "Glycoprotein (GP)",
        "5JQ7": "GP Complex"
    }
}

# === FUNCTION TO FETCH AND SAVE SEQUENCES ===
def fetch_virus_sequences(virus_name, count):
    print(f"\n{'='*60}")
    print(f"Fetching {count} genomic sequences for {virus_name}...")
    print(f"{'='*60}")

    # Use correct directory structure
    save_dir = os.path.join(genomic_base_dir, virus_name, "raw-sequence")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
        print(f"[+] Created directory: {save_dir}")
    else:
        print(f"[+] Directory exists: {save_dir}")

    save_file = os.path.join(save_dir, f"{virus_name}_all.fasta")

    # Map virus names to NCBI search terms
    search_terms = {
        "SARS-CoV-2": "SARS-CoV-2[Organism] OR Severe acute respiratory syndrome coronavirus 2[Organism]",
        "Influenza": "Influenza A virus[Organism] OR Influenza virus A[Organism]",
        "Ebola": "Ebola virus[Organism] OR Zaire ebolavirus[Organism]"
    }
    
    search_term = search_terms.get(virus_name, f"{virus_name}[Organism]")
    
    # Search NCBI for sequences
    print(f"  Search term: {search_term}")
    handle = Entrez.esearch(db="nucleotide", term=search_term, retmax=count)
    record = Entrez.read(handle)
    ids = record["IdList"]

    if not ids:
        print(f"[WARNING] No sequences found for {virus_name}.")
        return

    # Fetch sequences in FASTA format
    handle = Entrez.efetch(db="nucleotide", id=ids, rettype="fasta", retmode="text")
    sequences = handle.read()

    # Save sequences to file
    with open(save_file, "w") as f:
        f.write(sequences)

    print(f"[OK] Saved {len(ids)} sequences for {virus_name} -> {save_file}")

# === FUNCTION TO FETCH PDB STRUCTURES ===
def fetch_pdb_structures(virus_name, pdb_dict):
    """
    Download PDB structure files from RCSB PDB for a given virus.
    
    Args:
        virus_name: Name of the virus (e.g., 'SARS-CoV-2')
        pdb_dict: Dictionary of {pdb_id: protein_description}
    """
    print(f"\n{'='*60}")
    print(f"Fetching PDB structures for {virus_name}...")
    print(f"{'='*60}")
    
    # Create save directory
    save_dir = os.path.join(structural_base_dir, virus_name, "proteins")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
        print(f"[+] Created directory: {save_dir}")
    
    pdb_downloader = PDBList()
    success_count = 0
    failed = []
    
    for pdb_id, description in pdb_dict.items():
        try:
            print(f"\n  Downloading {pdb_id} ({description})...")
            
            # Download using Biopython PDBList (saves to pdb{id}.ent format)
            pdb_downloader.retrieve_pdb_file(
                pdb_id, 
                file_format='pdb', 
                pdir=save_dir
            )
            
            # Rename from pdb{id}.ent to {id}.pdb for clarity
            old_file = os.path.join(save_dir, f"pdb{pdb_id.lower()}.ent")
            new_file = os.path.join(save_dir, f"{pdb_id}.pdb")
            
            if os.path.exists(old_file):
                os.rename(old_file, new_file)
                file_size = os.path.getsize(new_file) / 1024  # KB
                print(f"  [OK] Saved {pdb_id}.pdb ({file_size:.1f} KB)")
                success_count += 1
            else:
                print(f"  [WARNING] File not found after download: {pdb_id}")
                failed.append(pdb_id)
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"  [ERROR] Failed to download {pdb_id}: {str(e)}")
            failed.append(pdb_id)
    
    print(f"\n{'='*60}")
    print(f"Summary for {virus_name}:")
    print(f"  [OK] Successfully downloaded: {success_count}/{len(pdb_dict)} structures")
    if failed:
        print(f"  [FAILED] {', '.join(failed)}")
    print(f"  [LOCATION] {save_dir}")
    print(f"{'='*60}\n")
    
    return success_count == len(pdb_dict)

# === RUN FETCH FOR ALL VIRUSES ===
if __name__ == "__main__":
    print("\n" + "="*70)
    print("VIRO-AI DATA ACQUISITION - PHASE 1")
    print("="*70)
    
    # Step 1: Fetch PDB Protein Structures
    print("\n[STEP 1/2] Fetching Protein Structures from RCSB PDB...")
    all_structures_success = True
    
    for virus in virus_list:
        if virus in pdb_structures:
            success = fetch_pdb_structures(virus, pdb_structures[virus])
            all_structures_success = all_structures_success and success
    
    if all_structures_success:
        print("\n[SUCCESS] ALL PROTEIN STRUCTURES DOWNLOADED!")
    else:
        print("\n[WARNING] Some protein structures failed. Check logs above.")
    
    # Step 2: Fetch Genomic Sequences (original functionality)
    print("\n[STEP 2/2] Fetching Genomic Sequences from NCBI...")
    for virus in virus_list:
        fetch_virus_sequences(virus, num_sequences[virus])
    
    print("\n" + "="*70)
    print("[SUCCESS] DATA ACQUISITION COMPLETE!")
    print("="*70)
