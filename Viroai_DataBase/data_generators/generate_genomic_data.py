"""
Genomic Data Generator for Viro-AI
Generates genomic sequences, variants, and processed data for all viruses
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_cleaner import DataCleaner
# Try importing BioPython (optional)
try:
    from Bio.Seq import Seq
    from Bio.SeqRecord import SeqRecord
    from Bio import SeqIO
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False
    print("[WARNING] BioPython not installed - FASTA generation will be limited")
    print("[INFO] Install with: pip install biopython")

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENOMIC_DIR = os.path.join(BASE_DIR, "genomic")

# Reference genome lengths (approximate, in nucleotides)
GENOME_LENGTHS = {
    "SARS-CoV-2": 29903,
    "Influenza": 13588,
    "Ebola": 18959,
    "HIV-1": 9181,
    "HCV": 9600,
    "HBV": 3215,
    "HSV-1": 152261,
    "CMV": 235646,
    "Dengue": 10723,
    "Zika": 10794,
    "Monkeypox": 197209,
    "Rabies": 11932,
    "RSV": 15222,
    "Adenovirus": 35937
}

# Key genes/proteins for each virus
VIRUS_GENES = {
    "SARS-CoV-2": ["ORF1ab", "S", "E", "M", "N", "ORF3a", "ORF6", "ORF7a", "ORF8"],
    "Influenza": ["PB2", "PB1", "PA", "HA", "NP", "NA", "M1", "M2", "NS1", "NS2"],
    "Ebola": ["NP", "VP35", "VP40", "GP", "VP30", "VP24", "L"],
    "HIV-1": ["gag", "pol", "env", "vif", "vpr", "tat", "rev", "vpu", "nef"],
    "HCV": ["Core", "E1", "E2", "p7", "NS2", "NS3", "NS4A", "NS4B", "NS5A", "NS5B"],
    "HBV": ["P", "S", "C", "X"],
    "HSV-1": ["UL1-UL56", "US1-US12", "RL1-RL2"],
    "CMV": ["UL1-UL150", "US1-US34"],
    "Dengue": ["C", "prM", "E", "NS1", "NS2A", "NS2B", "NS3", "NS4A", "NS4B", "NS5"],
    "Zika": ["C", "prM", "E", "NS1", "NS2A", "NS2B", "NS3", "NS4A", "NS4B", "NS5"],
    "Monkeypox": ["Early genes", "Late genes", "Structural proteins"],
    "Rabies": ["N", "P", "M", "G", "L"],
    "RSV": ["NS1", "NS2", "N", "P", "M", "SH", "G", "F", "M2", "L"],
    "Adenovirus": ["E1A", "E1B", "E2", "E3", "E4", "L1-L5"]
}

# Known variants/lineages
KNOWN_VARIANTS = {
    "SARS-CoV-2": ["Alpha", "Beta", "Gamma", "Delta", "Omicron", "BA.1", "BA.2", "BA.4", "BA.5"],
    "Influenza": ["H1N1", "H3N2", "H5N1", "H7N9"],
    "Ebola": ["Zaire", "Sudan", "Bundibugyo", "Tai Forest", "Reston"],
    "HIV-1": ["Group M", "Group O", "Group N", "CRF01_AE", "CRF02_AG"],
    "HCV": ["Genotype 1a", "Genotype 1b", "Genotype 2", "Genotype 3", "Genotype 4"],
    "HBV": ["Genotype A", "Genotype B", "Genotype C", "Genotype D"],
    "HSV-1": ["Type 1", "Type 2"],
    "CMV": ["Strain AD169", "Strain Towne", "Strain Merlin"],
    "Dengue": ["DENV-1", "DENV-2", "DENV-3", "DENV-4"],
    "Zika": ["Asian", "African"],
    "Monkeypox": ["Clade I", "Clade IIa", "Clade IIb"],
    "Rabies": ["Classical", "Bat", "Dog"],
    "RSV": ["RSV-A", "RSV-B"],
    "Adenovirus": ["Type 1-51"]
}

def generate_sequence(virus, length=None):
    """Generate a random genomic sequence"""
    if length is None:
        length = GENOME_LENGTHS.get(virus, 10000)
    
    # Use realistic nucleotide frequencies
    # For RNA viruses: higher A/U, for DNA: balanced
    if virus in ["SARS-CoV-2", "Influenza", "Ebola", "HCV", "Dengue", "Zika", "RSV", "Rabies"]:
        # RNA virus frequencies
        nucleotides = ['A', 'U', 'G', 'C']
        probs = [0.30, 0.30, 0.20, 0.20]
    else:
        # DNA virus frequencies
        nucleotides = ['A', 'T', 'G', 'C']
        probs = [0.25, 0.25, 0.25, 0.25]
    
    sequence = ''.join(np.random.choice(nucleotides, size=length, p=probs))
    return sequence

def generate_fasta_sequences(virus, num_sequences=100):
    """Generate multiple FASTA sequences"""
    sequences = []
    base_length = GENOME_LENGTHS.get(virus, 10000)
    
    variants = KNOWN_VARIANTS.get(virus, ["Default"])
    
    for i in range(num_sequences):
        # Slight length variation
        length = int(base_length * np.random.uniform(0.98, 1.02))
        
        # Generate sequence
        seq = generate_sequence(virus, length)
        
        # Select variant
        variant = random.choice(variants)
        
        # Create sequence record
        record = SeqRecord(
            Seq(seq),
            id=f"{virus}_strain_{i+1:04d}",
            description=f"{virus} {variant} strain isolated from patient sample {i+1}"
        )
        sequences.append(record)
    
    return sequences

def generate_variants(virus, num_variants=200):
    """Generate variant/mutation data"""
    data = []
    genes = VIRUS_GENES.get(virus, ["Unknown"])
    variants = KNOWN_VARIANTS.get(virus, ["Default"])
    genome_length = GENOME_LENGTHS.get(virus, 10000)
    
    # Common amino acids
    amino_acids = ['A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I', 
                   'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V']
    
    for i in range(num_variants):
        # Select random position
        position = random.randint(1, min(genome_length, 10000))
        
        # Select gene
        gene = random.choice(genes)
        
        # Generate mutation (e.g., E484K)
        original_aa = random.choice(amino_acids)
        mutated_aa = random.choice([aa for aa in amino_acids if aa != original_aa])
        
        mutation_name = f"{original_aa}{position}{mutated_aa}"
        
        # Variant/lineage
        lineage = random.choice(variants)
        
        # Frequency (0-1)
        frequency = np.random.beta(a=2, b=5)  # Skewed towards lower frequencies
        
        # dN/dS ratio (nonsynonymous/synonymous)
        dnds = np.random.lognormal(mean=0.5, sigma=0.5)
        dnds = min(dnds, 5.0)
        
        # Binding impact (arbitrary scale)
        binding_impact = np.random.normal(loc=1.0, scale=0.5)
        binding_impact = max(0.1, min(binding_impact, 3.0))
        
        # Fitness score
        fitness = np.random.normal(loc=12.0, scale=2.0)
        fitness = max(5.0, min(fitness, 20.0))
        
        # Context sequences (10bp upstream/downstream)
        upstream = ''.join(np.random.choice(['A', 'T', 'G', 'C'], size=10))
        downstream = ''.join(np.random.choice(['A', 'T', 'G', 'C'], size=10))
        
        # Secondary structure
        structures = ['helix', 'sheet', 'loop', 'turn']
        structure = random.choice(structures)
        
        # Solvent accessibility (0-1)
        accessibility = np.random.beta(a=2, b=2)
        
        # Date
        date = datetime.now() - timedelta(days=random.randint(0, 1000))
        
        data.append({
            'mutation': mutation_name,
            'position': position,
            'original': original_aa,
            'predicted': mutated_aa,
            'virus': virus,
            'protein': gene,
            'frequency': round(frequency, 4),
            'lineage': lineage,
            'date': date.strftime('%Y-%m'),
            'dnds': round(dnds, 3),
            'binding_impact': round(binding_impact, 3),
            'fitness': round(fitness, 3),
            'upstream_context': upstream,
            'downstream_context': downstream,
            'secondary_structure': structure,
            'solvent_accessibility': round(accessibility, 4)
        })
    
    return pd.DataFrame(data)

def generate_sequence_statistics(virus, num_sequences):
    """Generate sequence statistics"""
    genome_length = GENOME_LENGTHS.get(virus, 10000)
    
    stats = {
        'virus': virus,
        'generation_date': datetime.now().isoformat(),
        'total_sequences': num_sequences,
        'avg_sequence_length': genome_length,
        'genome_type': 'RNA' if virus in ["SARS-CoV-2", "Influenza", "Ebola", "HCV", 
                                          "Dengue", "Zika", "RSV", "Rabies"] else 'DNA',
        'key_genes': VIRUS_GENES.get(virus, []),
        'known_variants': KNOWN_VARIANTS.get(virus, []),
        'reference_genome': f"NC_{random.randint(100000, 999999)}.{random.randint(1, 9)}"
    }
    
    return stats

def generate_variant_summary(virus, variants_df):
    """Generate variant summary"""
    if variants_df.empty:
        return {}
    
    summary = {
        'virus': virus,
        'total_variants': len(variants_df),
        'unique_mutations': variants_df['mutation'].nunique(),
        'key_genes': variants_df['protein'].unique().tolist(),
        'lineages': variants_df['lineage'].unique().tolist(),
        'avg_frequency': round(variants_df['frequency'].mean(), 4),
        'avg_dnds': round(variants_df['dnds'].mean(), 3),
        'avg_binding_impact': round(variants_df['binding_impact'].mean(), 3),
        'avg_fitness': round(variants_df['fitness'].mean(), 3)
    }
    
    return summary

def generate_genomic_data_for_virus(virus):
    """Generate all genomic data for a single virus"""
    # Initialize data cleaner
    cleaner = DataCleaner(BASE_DIR)
    
    # Ensure correct folder structure
    paths = cleaner.ensure_folder_structure(virus, "genomic")
    if not cleaner.validate_file_paths(paths):
        print(f"    ✗ Failed to create folder structure for {virus}")
        return False
    
    print(f"\n  Generating genomic data for {virus}...")
    
    # Generate sequences
    num_sequences = random.randint(50, 200)
    
    fasta_file = os.path.join(paths['raw_sequence'], f"{virus}_all.fasta")
    
    # Check if file exists and append or create new
    if BIOPYTHON_AVAILABLE:
        sequences = generate_fasta_sequences(virus, num_sequences)
        # Save FASTA file (append if exists)
        if os.path.exists(fasta_file):
            existing_sequences = list(SeqIO.parse(fasta_file, "fasta"))
            sequences = existing_sequences + sequences
            # Remove duplicates based on sequence ID
            seen_ids = set()
            unique_sequences = []
            for seq in sequences:
                if seq.id not in seen_ids:
                    seen_ids.add(seq.id)
                    unique_sequences.append(seq)
            sequences = unique_sequences
            print(f"    [CLEAN] Removed duplicate sequences, keeping {len(sequences)} unique")
        SeqIO.write(sequences, fasta_file, "fasta")
        print(f"    ✓ Saved {os.path.basename(fasta_file)} ({len(sequences)} sequences)")
    else:
        # Fallback: save as simple text format
        existing_count = 0
        if os.path.exists(fasta_file):
            with open(fasta_file, 'r') as f:
                existing_count = len([line for line in f if line.startswith('>')])
        
        with open(fasta_file, 'a' if existing_count > 0 else 'w') as f:
            start_idx = existing_count + 1
            for i in range(num_sequences):
                seq = generate_sequence(virus)
                f.write(f">{virus}_strain_{start_idx + i:04d}\n")
                f.write(f"{seq}\n")
        print(f"    ✓ Saved {os.path.basename(fasta_file)} ({num_sequences} new sequences)")
    
    # Generate variants
    num_variants = random.randint(100, 300)
    variants_df = generate_variants(virus, num_variants)
    
    # Clean variants
    print(f"    [CLEAN] Cleaning variant data...")
    variants_df = cleaner.clean_genomic_variants(variants_df)
    
    # Check for existing variants and merge
    variants_csv = os.path.join(paths['variants'], "variants.csv")
    exists, existing_variants = cleaner.check_existing_data(variants_csv)
    if exists and existing_variants is not None:
        variants_df = cleaner.merge_and_deduplicate(
            existing_variants, variants_df,
            ['mutation', 'position', 'virus']
        )
    
    # Save variants
    variants_file = os.path.join(paths['variants'], "variant_summary.json")
    variant_summary = generate_variant_summary(virus, variants_df)
    with open(variants_file, 'w') as f:
        json.dump(variant_summary, f, indent=2)
    print(f"    ✓ Saved variant_summary.json ({len(variants_df)} variants)")
    
    # Save variant CSV
    cleaner.save_cleaned_data(variants_df, variants_csv, clean_func=cleaner.clean_genomic_variants)
    
    # Generate sequence statistics
    seq_stats = generate_sequence_statistics(virus, num_sequences)
    stats_file = os.path.join(paths['processed'], "sequence_statistics.json")
    with open(stats_file, 'w') as f:
        json.dump(seq_stats, f, indent=2)
    print(f"    ✓ Saved sequence_statistics.json")
    
    return True

def generate_genomic_datasets(viruses):
    """Generate genomic datasets for all viruses"""
    print(f"\nGenerating genomic data for {len(viruses)} viruses...")
    
    success_count = 0
    for virus in viruses:
        try:
            if generate_genomic_data_for_virus(virus):
                success_count += 1
        except Exception as e:
            print(f"    ✗ Error generating data for {virus}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✓ Generated genomic data for {success_count}/{len(viruses)} viruses")
    return success_count == len(viruses)

if __name__ == "__main__":
    test_viruses = ["SARS-CoV-2", "Ebola", "Influenza"]
    generate_genomic_datasets(test_viruses)

