**Primary** **Goal:**

Predict drug–virus/protein binding afinity using public bioinformatics
datasets and display top candidate drugs for a given viral mutation.

> **Phase** **1** **—** **Data** **Acquisition** **&** **Preparation**
> **(0–8** **hrs)**

**Objective:** Gather and preprocess core biological + chemical datasets
for model input.

**Tasks:**

> 1\. **Virus** **Genomic** **Data** **(NCBI** **/** **RCSB)**
>
> o Retrieve protein structures (e.g., spike, polymerase) for selected
> viruses.
>
> o Use APIs from **RCSB** **PDB** to fetch .pdb files.
>
> o Store under: ViroAI_Database/Genomic_Data/.
>
> 2\. **Drug** **&** **Compound** **Data** **(PubChem** **/**
> **ChEMBL)**
>
> o Fetch top antiviral compounds with SMILES or InChI keys.
>
> o Include properties like molecular weight, logP, bioactivity.
>
> o Store under: ViroAI_Database/Drug_Data/.
>
> 3\. **Docking/Bioactivity** **Reference** **(ChEMBL** **BioAssay**
> **data)**
>
> o Fetch binding afinities (IC50/Ki values) for training sample pairs.
>
> o Store under: ViroAI_Database/Bioactivity_Data/.
>
> 4\. **Data** **Cleaning** **Script**
>
> o Use Python (pandas, rdkit, biopython) to clean & merge datasets.
>
> o Validate entries: missing values, duplicates, invalid SMILES.
>
> **Output:**

Ready-to-use clean CSV datasets for model training and prediction.

> **Phase** **2** **—** **Backend** **Development** **(8–18** **hrs)**

**Objective:** Build and deploy core backend pipeline that predicts
binding afinities and ranks candidate drugs.

**Tasks:**

> 1\. **Model** **Core** **Setup** **(8–12** **hrs)**
>
> o Implement pretrained or lightweight GNN/Transformer model (can use
> **DeepChem** or **PyTorch** **Geometric**).
>
> o Input:
>
> ▪ Viral protein (sequence/structure embedding)
>
> ▪ Drug molecule (SMILES embedding)
>
> o Output:
>
> ▪ Predicted binding score / afinity value.
>
> 2\. **Prediction** **Engine** **(12–15** **hrs)**
>
> o Build Python API using **FastAPI** or **Flask**.
>
> o Routes:
>
> ▪ /predict → Input: virus ID or protein + drug list → Output: ranked
> binding afinities.
>
> ▪ /mutate (optional) → Predict mutation effects using similarity
> comparison.
>
> 3\. **Database** **Integration** **(15–18** **hrs)**
>
> o Store predictions, metadata, and molecule–protein pairs in local
> SQLite or MongoDB.
>
> o Create structure:
>
> o Database/
>
> o ├── viruses/
>
> o ├── drugs/
>
> o ├── binding_results/
>
> **Output:**

Functional backend that takes viral protein data + drug candidates and
returns ranked afinity predictions.

> **Phase** **3** **—** **Integration** **&** **Testing** **(18–24**
> **hrs)**

**Objective:** Finalize and test backend endpoints for frontend
handover.

**Tasks:**

> 1\. **API** **Testing**
>
> o Test API endpoints using Postman or Curl.
>
> o Verify JSON responses and latency (\<2s per prediction).
>
> 2\. **Model** **Validation**
>
> o Test on known virus–drug pairs (e.g., SARS-CoV-2 & Remdesivir).
>
> o Compare predicted vs known afinities.
>
> 3\. **Frontend** **Hand-off**
>
> o Provide clear API documentation (endpoints + payloads).
>
> o Example JSON output:
>
> o {
>
> o "virus": "SARS-CoV-2 Spike Protein",
>
> o "top_candidates": \[
>
> o {"drug": "Remdesivir", "score": 0.92},
>
> o {"drug": "Favipiravir", "score": 0.87}
>
> o \]
>
> o }
>
> **Output:**

Working backend ready for frontend integration.

> **Deliverables** **after** **24** **hrs**
>
> **Deliverable** **Description**
>
> **Clean** **Dataset** **Folder** Virus + Drug + Bioactivity datasets

**Deliverable**

**Model** **Script**

**API** **Backend**

**Docs**

**Demo** **Output**

**Description**

Core model training/prediction notebook

Flask/FastAPI server with /predict endpoint

API usage guide for frontend team

JSON prediction results for at least one virus
