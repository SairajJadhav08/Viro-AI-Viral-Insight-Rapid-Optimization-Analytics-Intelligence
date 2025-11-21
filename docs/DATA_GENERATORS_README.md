# Viro-AI Dataset Generators

This package contains Python scripts to generate comprehensive datasets for all viruses in the Viro-AI system, following the **70-20-10 Train-Validation-Test model**.

## Overview

The dataset generators create high-quality synthetic and realistic data for:

1. **Clinical Data** - Patient outcomes, treatments, and binding efficacy
2. **Genomic Data** - Sequences, variants, and mutation data
3. **Pharmaceutical Data** - Drug binding affinities and drug properties
4. **Processed Data** - ML-ready datasets with 70-20-10 splits
5. **Migrations Data** - Geographic spread and migration patterns

## Structure

```
data_generators/
├── __init__.py
├── generate_all_datasets.py      # Master orchestrator
├── generate_clinical_data.py     # Clinical data generator
├── generate_genomic_data.py      # Genomic data generator
├── generate_pharma_data.py       # Pharmaceutical data generator
├── generate_processed_data.py    # Processed data with 70-20-10 splits
├── generate_migrations_data.py   # Migration/geographic spread data
└── README.md
```

## Usage

### Generate All Datasets

Run the master script to generate all datasets for all viruses:

```bash
cd Viroai_DataBase/data_generators
python generate_all_datasets.py
```

### Generate Individual Datasets

You can also run individual generators:

```python
# Clinical data
from generate_clinical_data import generate_clinical_datasets
viruses = ["SARS-CoV-2", "Ebola", "Influenza"]
generate_clinical_datasets(viruses)

# Genomic data
from generate_genomic_data import generate_genomic_datasets
generate_genomic_datasets(viruses)

# Pharmaceutical data
from generate_pharma_data import generate_pharma_datasets
generate_pharma_datasets(viruses)

# Processed data (70-20-10 splits)
from generate_processed_data import generate_processed_datasets
generate_processed_datasets(viruses, train_ratio=0.70, val_ratio=0.20, test_ratio=0.10)

# Migrations data
from generate_migrations_data import generate_migrations_datasets
generate_migrations_datasets(viruses)
```

## Supported Viruses

The generators support all 14 viruses in the Viro-AI system:

1. Adenovirus
2. CMV (Cytomegalovirus)
3. Dengue
4. Ebola
5. HBV (Hepatitis B)
6. HCV (Hepatitis C)
7. HIV-1
8. HSV-1 (Herpes Simplex Virus 1)
9. Influenza
10. Monkeypox
11. Rabies
12. RSV (Respiratory Syncytial Virus)
13. SARS-CoV-2
14. Zika

## Data Structure

### Clinical Data
- `metadata/summary.json` - Dataset summary
- `outcomes/patient_outcomes.csv` - Patient outcome data
- `outcomes/drug_rankings.csv` - Drug efficacy rankings
- `treatments/binding_efficacy.csv` - Drug-protein binding data
- `treatments/treatment_data.csv` - Treatment protocols

### Genomic Data
- `raw-sequence/{virus}_all.fasta` - Genomic sequences in FASTA format
- `variants/variant_summary.json` - Variant metadata
- `variants/variants.csv` - Detailed variant data
- `processed/sequence_statistics.json` - Sequence statistics

### Pharmaceutical Data
- `real_world_binding/{virus}_binding.csv` - Drug-virus binding affinities
- `approved-drugs/antiviral_compounds.csv` - Approved drug database

### Processed Data
- `train_data.csv` - Training set (70%)
- `validation_data.csv` - Validation set (20%)
- `test_data.csv` - Test set (10%)
- `dataset_statistics.json` - Dataset statistics

### Migrations Data
- `geographic_spread.csv` - Geographic distribution
- `migration_paths.csv` - Country-to-country migration paths
- `temporal_trends.csv` - Time-series trends
- `summary.json` - Migration summary

## 70-20-10 Model

All processed datasets follow the **70-20-10 Train-Validation-Test split**:

- **70% Training** - Used for model training
- **20% Validation** - Used for hyperparameter tuning and model selection
- **10% Test** - Used for final, unbiased performance evaluation

The splits are **stratified by virus** to ensure balanced representation across all viruses.

## Dependencies

Required Python packages:

```bash
pip install pandas numpy biopython
```

Optional (for enhanced features):
```bash
pip install rdkit-pypi  # For molecular property calculations
```

## Data Quality

The generators create realistic data by:

- Using virus-specific protein targets and drug associations
- Generating realistic IC50 values based on binding strength distributions
- Incorporating known variants and lineages
- Using appropriate genome lengths and nucleotide frequencies
- Following realistic geographic spread patterns
- Maintaining data consistency across all data types

## Notes

- Data is generated synthetically but follows realistic patterns
- All numeric values are within biologically plausible ranges
- Dates and timestamps are randomized within reasonable ranges
- Missing data is handled appropriately
- All data is saved in standard formats (CSV, JSON, FASTA)

## Example Output

After running the generators, you'll have:

- **Clinical data** for 14 viruses with ~100-200 records each
- **Genomic sequences** with 50-200 sequences per virus
- **Variant data** with 100-300 variants per virus
- **Pharmaceutical data** with binding affinities for relevant drugs
- **Processed datasets** with proper 70-20-10 splits
- **Migration data** showing geographic spread patterns

Total dataset size will be several GB, following the 40GB target architecture outlined in the 70-20-10 model document.

