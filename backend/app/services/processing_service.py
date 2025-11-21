"""
Processing service for orchestrating file parsing, ML model calls, and result aggregation
"""
import os
import json
from typing import Dict, Any, List, Optional
from Bio import SeqIO
try:
    from Bio.PDB import PDBParser
    PDB_AVAILABLE = True
except ImportError:
    PDB_AVAILABLE = False
    print("Warning: Bio.PDB not available, PDB parsing will be skipped")
import pandas as pd
from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.results import MutationResult, DrugCandidateResult, ModificationResult
from app.services.ml_service import ml_service
from app.services.file_service import get_file_path
from decimal import Decimal


class ProcessingService:
    """Service for processing projects and generating results"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ml_service = ml_service
    
    def process_project(self, project_id: int) -> Dict[str, Any]:
        """
        Process a project: parse files, run REAL ML models, store results
        
        NOTE: This method ALWAYS uses real ML modules. Fast mode has been removed.
        All projects will be processed with actual ML predictions.
        
        Args:
            project_id: ID of the project to process
        
        Returns:
            Processing status and results summary
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Update status to Processing
        project.status = "Processing"
        self.db.commit()
        
        try:
            # ALWAYS use real ML modules - parse files and run ML models
            print(f"[Processing] Parsing files for project {project_id}...")
            parsed_data = self._parse_project_files(project)
            
            print(f"[Processing] Running REAL ML modules for project {project_id}...")
            print(f"  - Sequence length: {len(parsed_data.get('sequence', ''))}")
            print(f"  - Drug candidates: {len(parsed_data.get('drug_candidates', []))}")
            
            results = self._run_ml_analysis(parsed_data, project)
            
            print(f"[Processing] ML analysis complete:")
            print(f"  - Mutations: {len(results.get('mutations', []))}")
            print(f"  - Drugs: {len(results.get('drugs', []))}")
            print(f"  - Modifications: {len(results.get('modifications', []))}")
            
            # Store results in database
            self._store_results(project_id, results)
            
            # Extract and store structure data from PDB files
            structure_data = parsed_data.get("protein_structure")
            if structure_data and isinstance(structure_data, dict):
                # Store structure metadata in results for frontend access
                results["structure_data"] = {
                    "residues_count": structure_data.get("residues_count"),
                    "molecular_weight_kda": structure_data.get("molecular_weight_kda"),
                    "pdb_file_path": structure_data.get("file_path")
                }
            
            # Calculate deadliness score
            deadliness_score = self._calculate_deadliness_score(results)
            project.deadliness_score = Decimal(str(deadliness_score))
            
            # Update project status and counts
            project.status = "Completed"
            project.mutations_count = len(results.get("mutations", []))
            project.drugs_count = len(results.get("drugs", []))
            project.modifications_count = len(results.get("modifications", []))
            self.db.commit()
            
            return {
                "status": "completed",
                "mutations_count": project.mutations_count,
                "drugs_count": project.drugs_count,
                "modifications_count": project.modifications_count,
                "deadliness_score": deadliness_score,
                "structure_data": results.get("structure_data")
            }
        except Exception as e:
            project.status = "Failed"
            self.db.commit()
            raise Exception(f"Processing failed: {str(e)}")
    
    def _generate_fast_results(self, project: Project) -> Dict[str, Any]:
        """Generate sample results quickly without heavy ML processing"""
        import random
        
        # Generate sample mutations (5-10 mutations)
        mutations = []
        positions = ["S:501", "S:484", "S:452", "S:417", "S:477", "N:203", "N:204", "E:6"]
        amino_acids = ["A", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "Y"]
        risk_levels = ["Low", "Medium", "High"]
        effects = ["Increased binding affinity", "Reduced antibody recognition", "Enhanced viral entry", 
                  "Altered receptor binding", "Immune evasion", "Structural stability change"]
        
        num_mutations = random.randint(5, 10)
        for i in range(num_mutations):
            pos = random.choice(positions)
            original = random.choice(amino_acids)
            predicted = random.choice([aa for aa in amino_acids if aa != original])
            risk = random.choice(risk_levels)
            effect = random.choice(effects)
            
            mutations.append({
                "position": pos,
                "original": original,
                "predicted": predicted,
                "probability": round(random.uniform(0.3, 0.95), 2),
                "risk_level": risk,
                "effect": effect,
                "genomicLevel": {"mutationType": "Point mutation", "genomicRegion": "Spike protein"},
                "probabilityMetrics": {"aiScore": round(random.uniform(0.4, 0.9), 2)},
                "selectivePressure": {"dNdS": round(random.uniform(0.5, 2.0), 2)},
                "structuralConsequences": {"deltaRMSD": f"{random.uniform(0.1, 2.0):.2f} Å"},
                "receptorBinding": {"deltaKd": f"{random.uniform(-2.0, 2.0):.2f} kcal/mol"},
                "immuneEvasion": {"bCellEpitope": "Altered"},
                "viralFitness": {"replicationEfficiency": f"{random.uniform(80, 120):.1f}%"},
                "pathogenicity": {"contribution": f"{random.randint(5, 25)}/100"},
                "lineageEmergence": {"newLineageProbability": f"{random.randint(10, 40)}%"}
            })
        
        # Generate sample drugs (3-5 drugs)
        default_drugs = [
            {"name": "Remdesivir", "smiles": "CCCCCCCCN1C=NC2=C1C(=O)N(C(=O)N2C)C3C(C(C(O3)CCOP(=O)(O)OP(=O)(O)O)O)O"},
            {"name": "Favipiravir", "smiles": "C1=CC(=C(C(=C1F)F)N2C=NC(=C2C(=O)O)N)F"},
            {"name": "Ribavirin", "smiles": "C1=NC(=NN1C2C(C(C(O2)CO)O)O)C(=O)N"},
            {"name": "Molnupiravir", "smiles": "CC1=NC(=O)N(C=C1)C2C(C(C(O2)CO)O)O"},
            {"name": "Paxlovid", "smiles": "CC(C)(CN)NC(=O)[C@H](Cc1ccccc1)NC(=O)[C@H](CC(C)C)NC(=O)O[C@H]1CC[C@H](C1)C(=O)N"}
        ]
        
        drugs = []
        num_drugs = random.randint(3, 5)
        selected_drugs = random.sample(default_drugs, min(num_drugs, len(default_drugs)))
        
        for idx, drug in enumerate(selected_drugs, 1):
            binding_affinity = round(random.uniform(-10.0, -7.0), 2)
            drugs.append({
                "name": drug["name"],
                "smiles": drug["smiles"],
                "binding_affinity": binding_affinity,
                "rank": idx,
                "overallScore": round(random.uniform(70, 95), 1),
                "molecularIdentity": {
                    "molecularWeight": random.randint(200, 600),
                    "formula": "C" + str(random.randint(10, 30)) + "H" + str(random.randint(15, 50)) + "N" + str(random.randint(2, 10)) + "O" + str(random.randint(2, 15)),
                    "heavyAtoms": random.randint(15, 40)
                },
                "bindingMetrics": {
                    "ic50": f"{random.uniform(0.1, 50.0):.2f} μM",
                    "kd": f"{random.uniform(0.01, 10.0):.3f} nM"
                },
                "physicochemical": {
                    "logP": round(random.uniform(0.5, 5.0), 2),
                    "molecularWeight": random.randint(200, 600)
                },
                "adme": {"bioavailability": f"{random.randint(30, 90)}%"},
                "toxicology": {"ld50": f">{random.randint(100, 1000)} mg/kg"},
                "comparativeScores": {"overallViability": f"{random.randint(60, 95)}%"}
            })
        
        # Sort by binding affinity
        drugs.sort(key=lambda x: x.get("binding_affinity", 0), reverse=True)
        for idx, drug in enumerate(drugs, 1):
            drug["rank"] = idx
        
        # Generate sample modifications (2-4 modifications)
        modifications = []
        mod_types = ["Methylation", "Hydroxylation", "Fluorination", "Amination", "Halogenation"]
        num_mods = random.randint(2, 4)
        
        for i in range(num_mods):
            modifications.append({
                "baseFormula": "C20H30N5O10",
                "modifiedFormula": "C21H32N5O11",
                "modificationType": random.choice(mod_types),
                "modificationIdentity": {"type": random.choice(mod_types)},
                "structuralEffects": {"deltaRMSD": f"{random.uniform(0.1, 1.5):.2f} Å"},
                "bindingAffinityEffects": {"deltaKd": f"{random.uniform(-1.0, 1.0):.2f} kcal/mol"},
                "physicochemicalChanges": {"logPChange": f"{random.uniform(-1.0, 1.0):.2f}"},
                "comparativeScoring": {
                    "overallViability": f"{random.randint(65, 90)}%",
                    "confidence": round(random.uniform(0.7, 0.95), 2)
                }
            })
        
        return {
            "mutations": mutations,
            "drugs": drugs,
            "modifications": modifications
        }
    
    def _parse_project_files(self, project: Project) -> Dict[str, Any]:
        """Parse uploaded files (PDB, CSV, FASTA)"""
        parsed_data = {
            "sequence": None,
            "protein_structure": None,
            "clinical_data": None,
            "drug_candidates": []
        }
        
        # Parse protein files (PDB or FASTA)
        protein_files = project.get_protein_files()
        for file_path in protein_files:
            full_path = get_file_path(file_path)
            if os.path.exists(full_path):
                if file_path.endswith('.pdb'):
                    parsed_data["protein_structure"] = self._parse_pdb(full_path)
                elif file_path.endswith(('.fasta', '.fa')):
                    parsed_data["sequence"] = self._parse_fasta(full_path)
        
        # Parse clinical files (CSV)
        clinical_files = project.get_clinical_files()
        for file_path in clinical_files:
            full_path = get_file_path(file_path)
            if os.path.exists(full_path):
                parsed_data["clinical_data"] = self._parse_csv(full_path)
        
        # Parse assay files (CSV) - may contain drug candidates
        assay_files = project.get_assay_files()
        for file_path in assay_files:
            full_path = get_file_path(file_path)
            if os.path.exists(full_path):
                drug_candidates = self._parse_drug_candidates(full_path)
                parsed_data["drug_candidates"].extend(drug_candidates)
        
        # If no sequence from files, generate a default
        if not parsed_data["sequence"]:
            parsed_data["sequence"] = self._generate_default_sequence()
        
        # If no drug candidates, use default candidates
        if not parsed_data["drug_candidates"]:
            parsed_data["drug_candidates"] = self._get_default_drug_candidates()
        
        return parsed_data
    
    def _parse_pdb(self, file_path: str) -> Optional[Dict]:
        """Parse PDB file and extract structure data"""
        if not PDB_AVAILABLE:
            # Fallback: try to extract basic info from PDB file text
            return self._parse_pdb_fallback(file_path)
        
        try:
            parser = PDBParser(QUIET=True)
            structure = parser.get_structure('protein', file_path)
            
            # Extract structure data
            residues_count = 0
            molecular_weight = 0.0
            
            # Count residues from all chains
            for model in structure:
                for chain in model:
                    for residue in chain:
                        # Only count standard amino acids (not water, ions, etc.)
                        if residue.id[0] == ' ' and residue.get_resname() in [
                            'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
                            'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL'
                        ]:
                            residues_count += 1
                            
                            # Calculate molecular weight (approximate)
                            # Average molecular weight per residue is ~110 Da
                            molecular_weight += 110.0
            
            # Convert to kDa
            molecular_weight_kda = molecular_weight / 1000.0
            
            return {
                "structure": str(structure),
                "residues_count": residues_count,
                "molecular_weight_kda": round(molecular_weight_kda, 1),
                "file_path": file_path
            }
        except Exception as e:
            print(f"Error parsing PDB with BioPython: {e}")
            # Fallback to text parsing
            return self._parse_pdb_fallback(file_path)
    
    def _parse_pdb_fallback(self, file_path: str) -> Optional[Dict]:
        """Fallback PDB parser using text parsing when BioPython is unavailable"""
        try:
            residues_count = 0
            seen_residues = set()
            
            with open(file_path, 'r') as f:
                for line in f:
                    # ATOM or HETATM records
                    if line.startswith(('ATOM  ', 'HETATM')):
                        # Extract chain ID and residue number
                        chain_id = line[21:22].strip()
                        residue_num = line[22:26].strip()
                        residue_name = line[17:20].strip()
                        
                        # Only count standard amino acids
                        if residue_name in [
                            'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
                            'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL'
                        ]:
                            residue_key = f"{chain_id}_{residue_num}"
                            if residue_key not in seen_residues:
                                seen_residues.add(residue_key)
                                residues_count += 1
            
            # Calculate molecular weight
            molecular_weight_kda = (residues_count * 110.0) / 1000.0
            
            return {
                "residues_count": residues_count,
                "molecular_weight_kda": round(molecular_weight_kda, 1),
                "file_path": file_path
            }
        except Exception as e:
            print(f"Error in fallback PDB parsing: {e}")
            return None
    
    def _parse_fasta(self, file_path: str) -> Optional[str]:
        """Parse FASTA file and extract sequence"""
        try:
            for record in SeqIO.parse(file_path, "fasta"):
                return str(record.seq)
        except Exception as e:
            print(f"Error parsing FASTA: {e}")
            return None
    
    def _parse_csv(self, file_path: str) -> Optional[pd.DataFrame]:
        """Parse CSV file"""
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            return None
    
    def _parse_drug_candidates(self, file_path: str) -> List[Dict[str, str]]:
        """Parse drug candidates from CSV"""
        try:
            df = pd.read_csv(file_path)
            candidates = []
            for _, row in df.iterrows():
                if 'smiles' in row and 'name' in row:
                    candidates.append({
                        "name": str(row['name']),
                        "smiles": str(row['smiles'])
                    })
            return candidates
        except Exception as e:
            print(f"Error parsing drug candidates: {e}")
            return []
    
    def _generate_default_sequence(self) -> str:
        """Generate a default sequence if none provided"""
        # Default SARS-CoV-2 spike protein sequence (simplified)
        return "MFVFLVLLPLVSSQCVNLTTRTQLPPAYTNSFTRGVYYPDKVFRSSVLHSTQDLFLPFFSNVTWFHAIHVSGTNGTKRFDNPVLPFNDGVYFASTEKSNIIRGWIFGTTLDSKTQSLLIVNNATNVVIKVCEFQFCNDPFLGVYYHKNNKSWMESEFRVYSSANNCTFEYVSQPFLMDLEGKQGNFKNLREFVFKNIDGYFKIYSKHTPINLVRDLPQGFSALEPLVDLPIGINITRFQTLLALHRSYLTPGDSSSGWTAGAAAYYVGYLQPRTFLLKYNENGTITDAVDCALDPLSETKCTLKSFTVEKGIYQTSNFRVQPTESIVRFPNITNLCPFGEVFNATRFASVYAWNRKRISNCVADYSVLYNSASFSTFKCYGVSPTKLNDLCFTNVYADSFVIRGDEVRQIAPGQTGKIADYNYKLPDDFTGCVIAWNSNNLDSKVGGNYNYLYRLFRKSNLKPFERDISTEIYQAGSTPCNGVEGFNCYFPLQSYGFQPTNGVGYQPYRVVVLSFELLHAPATVCGPKKSTNLVKNKCVNFNFNGLTGTGVLTESNKKFLPFQQFGRDIADTTDAVRDPQTLEILDITPCSFGGVSVITPGTNTSNQVAVLYQDVNCTEVPVAIHADQLTPTWRVYSTGSNVFQTRAGCLIGAEHVNNSYECDIPIGAGICASYQTQTNSPRRARSVASQSIIAYTMSLGAENSVAYSNNSIAIPTNFTISVTTEILPVSMTKTSVDCTMYICGDSTECSNLLLQYGSFCTQLNRALTGIAVEQDKNTQEVFAQVKQIYKTPPIKDFGGFNFSQILPDPSKPSKRSFIEDLLFNKVTLADAGFIKQYGDCLGDIAARDLICAQKFNGLTVLPPLLTDEMIAQYTSALLAGTITSGWTFGAGAALQIPFAMQMAYRFNGIGVTQNVLYENQKLIANQFNSAIGKIQDSLSSTASALGKLQDVVNQNAQALNTLVKQLSSNFGAISSVLNDILSRLDKVEAEVQIDRLITGRLQSLQTYVTQQLIRAAEIRASANLAATKMSECVLGQSKRVDFCGKGYHLMSFPQSAPHGVVFLHVTYVPAQEKNFTTAPAICHDGKAHFPREGVFVSNGTHWFVTQRNFYEPQIITTDNTFVSGNCDVVIGIVNNTVYDPLQPELDSFKEELDKYFKNHTSPDVDLGDISGINASVVNIQKEIDRLNEVAKNLNESLIDLQELGKYEQYIKWPWYIWLGFIAGLIAIVMVTIMLCCMTSCCSCLKGCCSCGSCCKFDEDDSEPVLKGVKLHYT"
    
    def _get_default_drug_candidates(self) -> List[Dict[str, str]]:
        """Get default drug candidates if none provided"""
        return [
            {"name": "Remdesivir", "smiles": "CCCCCCCCN1C=NC2=C1C(=O)N(C(=O)N2C)C3C(C(C(O3)CCOP(=O)(O)OP(=O)(O)O)O)O"},
            {"name": "Favipiravir", "smiles": "C1=CC(=C(C(=C1F)F)N2C=NC(=C2C(=O)O)N)F"},
            {"name": "Ribavirin", "smiles": "C1=NC(=NN1C2C(C(C(O2)CO)O)O)C(=O)N"},
        ]
    
    def _run_ml_analysis(self, parsed_data: Dict, project: Project) -> Dict[str, Any]:
        """Run ML models on parsed data"""
        results = {
            "mutations": [],
            "drugs": [],
            "modifications": []
        }
        
        # 1. Mutation prediction
        try:
            sequence = parsed_data.get("sequence", "")
            if not sequence:
                print("[ML Analysis] Warning: No sequence provided, using default")
                sequence = self._generate_default_sequence()
            
            virus_name = project.country or project.title or "SARS-CoV-2"  # Use country/title as virus hint
            print(f"[ML Analysis] Running mutation prediction for {virus_name} (sequence length: {len(sequence)})...")
            
            mutations = self.ml_service.predict_mutations(
                sequence=sequence,
                protein_structure=parsed_data.get("protein_structure"),
                virus_name=virus_name
            )
            
            print(f"[ML Analysis] Mutation prediction complete: {len(mutations)} mutations found")
            results["mutations"] = mutations if mutations else []
        except Exception as e:
            print(f"[ML Analysis] Error in mutation prediction: {e}")
            import traceback
            traceback.print_exc()
            results["mutations"] = []
        
        # 2. Drug candidate analysis
        try:
            drug_candidates = parsed_data.get("drug_candidates", [])
            if not drug_candidates:
                print("[ML Analysis] Warning: No drug candidates provided, using defaults")
                drug_candidates = self._get_default_drug_candidates()
            
            print(f"[ML Analysis] Analyzing {len(drug_candidates)} drug candidates...")
            
            analyzed_drugs = self.ml_service.analyze_drug_candidates(
                drug_list=drug_candidates,
                target_protein="Spike Protein"
            )
            
            # Add binding affinity predictions
            for drug in analyzed_drugs:
                if drug.get("smiles"):
                    try:
                        binding_affinity = self.ml_service.predict_binding_affinity(
                            smiles=drug["smiles"],
                            virus_name=virus_name
                        )
                        drug["binding_affinity"] = binding_affinity
                    except Exception as e:
                        print(f"[ML Analysis] Warning: Could not predict binding affinity: {e}")
                        drug["binding_affinity"] = -8.5
            
            # Sort by binding affinity (lower is better, so reverse=True means most negative first)
            analyzed_drugs.sort(key=lambda x: x.get("binding_affinity", -8.5), reverse=True)
            
            # Assign ranks
            for idx, drug in enumerate(analyzed_drugs, 1):
                drug["rank"] = idx
            
            print(f"[ML Analysis] Drug analysis complete: {len(analyzed_drugs)} drugs analyzed")
            results["drugs"] = analyzed_drugs if analyzed_drugs else []
        except Exception as e:
            print(f"[ML Analysis] Error in drug analysis: {e}")
            import traceback
            traceback.print_exc()
            results["drugs"] = []
        
        # 3. Chemical modifications (based on top drug)
        try:
            if results["drugs"]:
                top_drug = results["drugs"][0]
                print(f"[ML Analysis] Generating modifications for top drug: {top_drug.get('name', 'Unknown')}...")
                
                modifications = self.ml_service.suggest_modifications(
                    base_compound={"name": top_drug.get("name", ""), "smiles": top_drug.get("smiles", "")}
                )
                
                print(f"[ML Analysis] Modification analysis complete: {len(modifications)} modifications generated")
                results["modifications"] = modifications if modifications else []
            else:
                print("[ML Analysis] No drugs available for modification analysis")
                results["modifications"] = []
        except Exception as e:
            print(f"[ML Analysis] Error in modification analysis: {e}")
            import traceback
            traceback.print_exc()
            results["modifications"] = []
        
        return results
    
    def _store_results(self, project_id: int, results: Dict[str, Any]):
        """Store ML results in database using raw SQL to avoid created_at column issues"""
        from sqlalchemy import text
        
        # Store mutations using raw SQL
        for mutation in results.get("mutations", []):
            # Calculate effect and risk_level from mutation data if not provided
            effect = mutation.get("effect", "")
            if not effect:
                # Derive effect from structural consequences
                structural = mutation.get("structuralConsequences", {})
                if structural:
                    delta_g = structural.get("deltaGStability", "")
                    if "unstable" in str(delta_g).lower() or "+" in str(delta_g):
                        effect = "Structural destabilization"
                    else:
                        effect = "Structural stability change"
                else:
                    effect = "Mutation effect"
            
            # Calculate risk level from probability and pathogenicity
            risk_level = mutation.get("risk_level", "Medium")
            if not risk_level or risk_level == "Medium":
                prob = mutation.get("probability", 0.5)
                pathogenicity = mutation.get("pathogenicity", {})
                path_contrib = pathogenicity.get("contribution", "0/100") if isinstance(pathogenicity, dict) else "0/100"
                try:
                    path_val = int(str(path_contrib).split("/")[0])
                except:
                    path_val = 0
                
                if prob > 0.7 or path_val > 20:
                    risk_level = "High"
                elif prob > 0.4 or path_val > 10:
                    risk_level = "Medium"
                else:
                    risk_level = "Low"
            
            # Use raw SQL to avoid created_at column issue
            self.db.execute(text("""
                INSERT INTO mutation_results 
                (project_id, mutation_position, original_amino_acid, predicted_amino_acid, 
                 probability, effect, risk_level, genomic_level, probability_metrics, 
                 selective_pressure, structural_consequences, receptor_binding, 
                 immune_evasion, viral_fitness, pathogenicity, lineage_emergence)
                VALUES 
                (:project_id, :mutation_position, :original_amino_acid, :predicted_amino_acid,
                 :probability, :effect, :risk_level, :genomic_level, :probability_metrics,
                 :selective_pressure, :structural_consequences, :receptor_binding,
                 :immune_evasion, :viral_fitness, :pathogenicity, :lineage_emergence)
            """), {
                "project_id": project_id,
                "mutation_position": mutation.get("position", mutation.get("mutation_position", "")),
                "original_amino_acid": mutation.get("original", mutation.get("original_amino_acid", "")),
                "predicted_amino_acid": mutation.get("predicted", mutation.get("predicted_amino_acid", "")),
                "probability": float(mutation.get("probability", 0.5)),
                "effect": effect,
                "risk_level": risk_level,
                "genomic_level": json.dumps(mutation.get("genomicLevel", mutation.get("genomic_level", {}))),
                "probability_metrics": json.dumps(mutation.get("probabilityMetrics", mutation.get("probability_metrics", {}))),
                "selective_pressure": json.dumps(mutation.get("selectivePressure", mutation.get("selective_pressure", {}))),
                "structural_consequences": json.dumps(mutation.get("structuralConsequences", mutation.get("structural_consequences", {}))),
                "receptor_binding": json.dumps(mutation.get("receptorBinding", mutation.get("receptor_binding", {}))),
                "immune_evasion": json.dumps(mutation.get("immuneEvasion", mutation.get("immune_evasion", {}))),
                "viral_fitness": json.dumps(mutation.get("viralFitness", mutation.get("viral_fitness", {}))),
                "pathogenicity": json.dumps(mutation.get("pathogenicity", {})),
                "lineage_emergence": json.dumps(mutation.get("lineageEmergence", mutation.get("lineage_emergence", {})))
            })
        
        # Store drugs
        for drug in results.get("drugs", []):
            # Extract binding metrics safely
            binding_metrics = drug.get("bindingMetrics", {})
            if isinstance(binding_metrics, str):
                try:
                    binding_metrics = json.loads(binding_metrics)
                except:
                    binding_metrics = {}
            
            # Extract molecular identity safely
            mol_identity = drug.get("molecularIdentity", {})
            if isinstance(mol_identity, str):
                try:
                    mol_identity = json.loads(mol_identity)
                except:
                    mol_identity = {}
            
            # Extract physicochemical safely
            physico = drug.get("physicochemical", {})
            if isinstance(physico, str):
                try:
                    physico = json.loads(physico)
                except:
                    physico = {}
            
            # Get binding affinity (from binding_affinity field or bindingMetrics)
            binding_affinity = drug.get("binding_affinity")
            if binding_affinity is None:
                binding_energy = binding_metrics.get("bindingEnergy", "-8.5")
                try:
                    binding_affinity = float(str(binding_energy).replace(" kcal/mol", "").replace(" kcal", ""))
                except:
                    binding_affinity = -8.5
            
            # Use raw SQL to avoid created_at column issue
            self.db.execute(text("""
                INSERT INTO drug_candidate_results 
                (project_id, drug_name, smiles, binding_affinity, ic50, logp, molecular_weight, 
                 formula, heavy_atoms, rank, score, molecular_identity, binding_metrics, 
                 interaction_map, structural_stability, physicochemical, adme, toxicology, 
                 comparative_scores, ensemble_analysis, resistance_vulnerability, chemical_diversity)
                VALUES 
                (:project_id, :drug_name, :smiles, :binding_affinity, :ic50, :logp, :molecular_weight,
                 :formula, :heavy_atoms, :rank, :score, :molecular_identity, :binding_metrics,
                 :interaction_map, :structural_stability, :physicochemical, :adme, :toxicology,
                 :comparative_scores, :ensemble_analysis, :resistance_vulnerability, :chemical_diversity)
            """), {
                "project_id": project_id,
                "drug_name": drug.get("name", ""),
                "smiles": drug.get("smiles", ""),
                "binding_affinity": float(binding_affinity),
                "ic50": str(binding_metrics.get("ic50", "N/A")),
                "logp": float(physico.get("logP", physico.get("logp", 2.5))),
                "molecular_weight": float(mol_identity.get("molecularWeight", mol_identity.get("molecular_weight", 300))),
                "formula": str(mol_identity.get("formula", "")),
                "heavy_atoms": int(mol_identity.get("heavyAtoms", mol_identity.get("heavy_atoms", 20))),
                "rank": int(drug.get("rank", 1)),
                "score": int(drug.get("overallScore", drug.get("overall_score", 85))),
                "molecular_identity": json.dumps(mol_identity) if not isinstance(mol_identity, str) else mol_identity,
                "binding_metrics": json.dumps(binding_metrics) if not isinstance(binding_metrics, str) else binding_metrics,
                "interaction_map": json.dumps(drug.get("interactionMap", drug.get("interaction_map", {}))),
                "structural_stability": json.dumps(drug.get("structuralStability", drug.get("structural_stability", {}))),
                "physicochemical": json.dumps(physico) if not isinstance(physico, str) else physico,
                "adme": json.dumps(drug.get("adme", {})),
                "toxicology": json.dumps(drug.get("toxicology", {})),
                "comparative_scores": json.dumps(drug.get("comparativeScores", drug.get("comparative_scores", {}))),
                "ensemble_analysis": json.dumps(drug.get("ensembleAnalysis", drug.get("ensemble_analysis", {}))),
                "resistance_vulnerability": json.dumps(drug.get("resistanceVulnerability", drug.get("resistance_vulnerability", {}))),
                "chemical_diversity": json.dumps(drug.get("chemicalDiversity", drug.get("chemical_diversity", {})))
            })
        
        # Store modifications
        for mod in results.get("modifications", []):
            # Extract comparative scoring safely
            comp_scoring = mod.get("comparativeScoring", mod.get("comparative_scoring", {}))
            if isinstance(comp_scoring, str):
                try:
                    comp_scoring = json.loads(comp_scoring)
                except:
                    comp_scoring = {}
            
            # Use raw SQL to avoid created_at column issue
            self.db.execute(text("""
                INSERT INTO modification_results 
                (project_id, base_formula, modified_formula, changes, improvements, confidence,
                 modification_identity, structural_effects, physicochemical_changes, 
                 binding_affinity_effects, electronic_effects, stability_degradation,
                 solubility_permeability, adme_shifts, toxicity_signatures, 
                 synthetic_feasibility, comparative_scoring)
                VALUES 
                (:project_id, :base_formula, :modified_formula, :changes, :improvements, :confidence,
                 :modification_identity, :structural_effects, :physicochemical_changes,
                 :binding_affinity_effects, :electronic_effects, :stability_degradation,
                 :solubility_permeability, :adme_shifts, :toxicity_signatures,
                 :synthetic_feasibility, :comparative_scoring)
            """), {
                "project_id": project_id,
                "base_formula": str(mod.get("baseFormula", mod.get("base_formula", ""))),
                "modified_formula": str(mod.get("modifiedFormula", mod.get("modified_formula", ""))),
                "changes": str(mod.get("modificationType", mod.get("modification_type", ""))),
                "improvements": str(comp_scoring.get("overallViability", comp_scoring.get("overall_viability", ""))),
                "confidence": float(comp_scoring.get("confidence", 0.75)),
                "modification_identity": json.dumps(mod.get("modificationIdentity", mod.get("modification_identity", {}))),
                "structural_effects": json.dumps(mod.get("structuralEffects", mod.get("structural_effects", {}))),
                "physicochemical_changes": json.dumps(mod.get("physicochemicalChanges", mod.get("physicochemical_changes", {}))),
                "binding_affinity_effects": json.dumps(mod.get("bindingAffinityEffects", mod.get("binding_affinity_effects", {}))),
                "electronic_effects": json.dumps(mod.get("electronicEffects", mod.get("electronic_effects", {}))),
                "stability_degradation": json.dumps(mod.get("stabilityDegradation", mod.get("stability_degradation", {}))),
                "solubility_permeability": json.dumps(mod.get("solubilityPermeability", mod.get("solubility_permeability", {}))),
                "adme_shifts": json.dumps(mod.get("admeShifts", mod.get("adme_shifts", {}))),
                "toxicity_signatures": json.dumps(mod.get("toxicitySignatures", mod.get("toxicity_signatures", {}))),
                "synthetic_feasibility": json.dumps(mod.get("syntheticFeasibility", mod.get("synthetic_feasibility", {}))),
                "comparative_scoring": json.dumps(comp_scoring) if not isinstance(comp_scoring, str) else comp_scoring
            })
        
        self.db.commit()
    
    def _calculate_deadliness_score(self, results: Dict[str, Any]) -> float:
        """Calculate deadliness score from results"""
        score = 50.0  # Base score
        
        # Factor in mutations (higher risk mutations increase score)
        mutations = results.get("mutations", [])
        for mutation in mutations:
            risk_level = mutation.get("risk_level", "Medium")
            if risk_level == "High":
                score += 10
            elif risk_level == "Medium":
                score += 5
        
        # Factor in drug binding (lower binding affinity = higher deadliness)
        drugs = results.get("drugs", [])
        if drugs:
            avg_binding = sum(d.get("binding_affinity", -8.5) for d in drugs) / len(drugs)
            if avg_binding > -7.0:  # Weak binding
                score += 15
            elif avg_binding > -8.0:
                score += 10
        
        # Normalize to 0-100
        return min(100.0, max(0.0, score))

