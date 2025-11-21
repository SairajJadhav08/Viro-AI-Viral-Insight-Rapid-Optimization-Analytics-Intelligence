"""
Data Cleaning and Validation Utilities for Viro-AI
Ensures data quality, removes duplicates, and validates folder structure
"""

import os
import pandas as pd
import numpy as np
import json
from typing import List, Dict, Tuple, Optional

class DataCleaner:
    """Utility class for cleaning and validating datasets"""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
    
    def clean_dataframe(self, df: pd.DataFrame, 
                       duplicate_subset: Optional[List[str]] = None,
                       drop_na_columns: Optional[List[str]] = None,
                       numeric_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Clean a DataFrame by removing duplicates and handling missing values
        
        Args:
            df: DataFrame to clean
            duplicate_subset: Columns to check for duplicates (None = all columns)
            drop_na_columns: Columns where NA values should be dropped
            numeric_columns: Columns to ensure are numeric
        
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
        
        original_len = len(df)
        df = df.copy()
        
        # Remove duplicates
        if duplicate_subset:
            df = df.drop_duplicates(subset=duplicate_subset, keep='first')
        else:
            df = df.drop_duplicates(keep='first')
        
        duplicates_removed = original_len - len(df)
        if duplicates_removed > 0:
            print(f"    [CLEAN] Removed {duplicates_removed} duplicate rows")
        
        # Handle missing values in critical columns
        if drop_na_columns:
            for col in drop_na_columns:
                if col in df.columns:
                    before = len(df)
                    df = df[df[col].notna()]
                    if len(df) < before:
                        print(f"    [CLEAN] Removed {before - len(df)} rows with missing {col}")
        
        # Ensure numeric columns are numeric
        if numeric_columns:
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # Remove rows where conversion failed
                    before = len(df)
                    df = df[df[col].notna()]
                    if len(df) < before:
                        print(f"    [CLEAN] Removed {before - len(df)} rows with invalid {col}")
        
        return df
    
    def validate_numeric_range(self, df: pd.DataFrame, 
                               column: str, 
                               min_val: Optional[float] = None,
                               max_val: Optional[float] = None) -> pd.DataFrame:
        """Validate numeric column is within range"""
        if column not in df.columns:
            return df
        
        original_len = len(df)
        
        if min_val is not None:
            df = df[df[column] >= min_val]
        if max_val is not None:
            df = df[df[column] <= max_val]
        
        if len(df) < original_len:
            print(f"    [VALIDATE] Removed {original_len - len(df)} rows with {column} out of range")
        
        return df
    
    def clean_ic50_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean IC50 binding data"""
        if df.empty:
            return df
        
        # Remove duplicates based on virus, drug_id, and protein
        df = self.clean_dataframe(
            df,
            duplicate_subset=['virus', 'drug_id', 'protein'] if all(c in df.columns for c in ['virus', 'drug_id', 'protein']) else None,
            drop_na_columns=['ic50_nm', 'virus', 'drug_id'],
            numeric_columns=['ic50_nm', 'pic50', 'ki_nm']
        )
        
        # Validate IC50 range (0.1 nM to 100000 nM)
        df = self.validate_numeric_range(df, 'ic50_nm', min_val=0.1, max_val=100000)
        
        # Ensure pIC50 is calculated if missing
        if 'pic50' not in df.columns and 'ic50_nm' in df.columns:
            df['pic50'] = -np.log10(df['ic50_nm'] * 1e-9)
        
        return df
    
    def clean_genomic_variants(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean genomic variant data"""
        if df.empty:
            return df
        
        # Remove duplicates based on mutation and position
        df = self.clean_dataframe(
            df,
            duplicate_subset=['mutation', 'position', 'virus'] if all(c in df.columns for c in ['mutation', 'position', 'virus']) else None,
            drop_na_columns=['mutation', 'virus'],
            numeric_columns=['position', 'frequency', 'dnds', 'binding_impact', 'fitness']
        )
        
        # Validate ranges
        df = self.validate_numeric_range(df, 'frequency', min_val=0.0, max_val=1.0)
        df = self.validate_numeric_range(df, 'dnds', min_val=0.0, max_val=10.0)
        df = self.validate_numeric_range(df, 'fitness', min_val=0.0, max_val=50.0)
        
        return df
    
    def clean_patient_outcomes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean patient outcome data"""
        if df.empty:
            return df
        
        # Remove duplicates based on patient_id
        df = self.clean_dataframe(
            df,
            duplicate_subset=['patient_id'] if 'patient_id' in df.columns else None,
            drop_na_columns=['patient_id', 'virus', 'outcome'],
            numeric_columns=['age', 'severity_score', 'recovery_days']
        )
        
        # Validate ranges
        df = self.validate_numeric_range(df, 'age', min_val=0, max_val=150)
        df = self.validate_numeric_range(df, 'severity_score', min_val=1, max_val=10)
        if 'recovery_days' in df.columns:
            df = self.validate_numeric_range(df, 'recovery_days', min_val=0, max_val=365)
        
        return df
    
    def clean_geographic_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean geographic spread data"""
        if df.empty:
            return df
        
        # Remove duplicates based on country, date, and virus
        df = self.clean_dataframe(
            df,
            duplicate_subset=['country', 'date', 'virus'] if all(c in df.columns for c in ['country', 'date', 'virus']) else None,
            drop_na_columns=['country', 'virus', 'date'],
            numeric_columns=['cases', 'deaths', 'latitude', 'longitude']
        )
        
        # Validate ranges
        df = self.validate_numeric_range(df, 'cases', min_val=0)
        df = self.validate_numeric_range(df, 'deaths', min_val=0)
        df = self.validate_numeric_range(df, 'latitude', min_val=-90, max_val=90)
        df = self.validate_numeric_range(df, 'longitude', min_val=-180, max_val=180)
        
        return df
    
    def ensure_folder_structure(self, virus: str, data_type: str) -> Dict[str, str]:
        """
        Ensure correct folder structure exists and return paths
        
        Args:
            virus: Virus name
            data_type: Type of data (clinical, genomic, pharma, processed, migrations)
        
        Returns:
            Dictionary of folder paths
        """
        paths = {}
        
        if data_type == "clinical":
            base_path = os.path.join(self.base_dir, "clinical", virus)
            paths['base'] = base_path
            paths['metadata'] = os.path.join(base_path, "metadata")
            paths['outcomes'] = os.path.join(base_path, "outcomes")
            paths['treatments'] = os.path.join(base_path, "treatments")
            
        elif data_type == "genomic":
            base_path = os.path.join(self.base_dir, "genomic", virus)
            paths['base'] = base_path
            paths['raw_sequence'] = os.path.join(base_path, "raw-sequence")
            paths['variants'] = os.path.join(base_path, "variants")
            paths['processed'] = os.path.join(base_path, "processed")
            
        elif data_type == "pharma":
            base_path = os.path.join(self.base_dir, "pharma")
            paths['base'] = base_path
            paths['approved_drugs'] = os.path.join(base_path, "approved-drugs")
            paths['real_world_binding'] = os.path.join(base_path, "real_world_binding")
            
        elif data_type == "processed":
            paths['base'] = os.path.join(self.base_dir, "processed")
            # Processed data doesn't need virus-specific folders
            
        elif data_type == "migrations":
            base_path = os.path.join(self.base_dir, "migrations", virus)
            paths['base'] = base_path
            
        # Create all directories
        for path in paths.values():
            os.makedirs(path, exist_ok=True)
        
        return paths
    
    def validate_file_paths(self, paths: Dict[str, str]) -> bool:
        """Validate that all required paths exist"""
        missing = []
        for name, path in paths.items():
            if not os.path.exists(path):
                missing.append(f"{name}: {path}")
        
        if missing:
            print(f"    [ERROR] Missing paths:")
            for m in missing:
                print(f"      - {m}")
            return False
        return True
    
    def save_cleaned_data(self, df: pd.DataFrame, file_path: str, 
                         index: bool = False, 
                         clean_func=None) -> bool:
        """
        Clean and save DataFrame to file
        
        Args:
            df: DataFrame to save
            file_path: Path to save file
            index: Whether to include index
            clean_func: Optional cleaning function to apply
        
        Returns:
            True if successful
        """
        try:
            # Apply cleaning function if provided
            if clean_func:
                df = clean_func(df)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save file
            df.to_csv(file_path, index=index)
            
            print(f"    [SAVE] Saved {len(df)} records to {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            print(f"    [ERROR] Failed to save {file_path}: {e}")
            return False
    
    def check_existing_data(self, file_path: str) -> Tuple[bool, Optional[pd.DataFrame]]:
        """Check if file exists and load it"""
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                print(f"    [INFO] Found existing file: {os.path.basename(file_path)} ({len(df)} records)")
                return True, df
            except Exception as e:
                print(f"    [WARNING] Could not read existing file: {e}")
                return True, None
        return False, None
    
    def merge_and_deduplicate(self, existing_df: pd.DataFrame, 
                              new_df: pd.DataFrame,
                              duplicate_subset: List[str]) -> pd.DataFrame:
        """Merge existing and new data, removing duplicates"""
        if existing_df.empty:
            return new_df
        if new_df.empty:
            return existing_df
        
        # Combine dataframes
        combined = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Remove duplicates
        before = len(combined)
        combined = combined.drop_duplicates(subset=duplicate_subset, keep='first')
        
        if len(combined) < before:
            print(f"    [MERGE] Removed {before - len(combined)} duplicates after merge")
        
        return combined
    
    def generate_data_quality_report(self, df: pd.DataFrame, 
                                     file_path: str) -> Dict:
        """Generate data quality report"""
        report = {
            'total_records': len(df),
            'columns': list(df.columns),
            'missing_values': {},
            'duplicates': 0,
            'data_types': {}
        }
        
        # Check missing values
        for col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                report['missing_values'][col] = {
                    'count': int(missing),
                    'percentage': round(missing / len(df) * 100, 2)
                }
        
        # Check duplicates
        report['duplicates'] = int(df.duplicated().sum())
        
        # Data types
        for col in df.columns:
            report['data_types'][col] = str(df[col].dtype)
        
        # Save report
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
        
        return report

