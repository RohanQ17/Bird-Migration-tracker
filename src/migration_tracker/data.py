"""
Data loading and processing utilities for migration data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Load migration data from various sources."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize DataLoader.
        
        Args:
            data_dir: Path to the data directory
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.external_dir = self.data_dir / "external"
        
    def load_csv(self, filename: str, data_type: str = "raw") -> pd.DataFrame:
        """
        Load CSV file from specified data directory.
        
        Args:
            filename: Name of the CSV file
            data_type: Type of data ('raw', 'processed', 'external')
            
        Returns:
            DataFrame containing the loaded data
        """
        data_dirs = {
            "raw": self.raw_dir,
            "processed": self.processed_dir,
            "external": self.external_dir
        }
        
        if data_type not in data_dirs:
            raise ValueError(f"Invalid data_type. Must be one of {list(data_dirs.keys())}")
        
        file_path = data_dirs[data_type] / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} not found")
        
        logger.info(f"Loading data from {file_path}")
        return pd.read_csv(file_path)
    
    def load_excel(self, filename: str, sheet_name: Optional[str] = None, 
                   data_type: str = "raw") -> pd.DataFrame:
        """
        Load Excel file from specified data directory.
        
        Args:
            filename: Name of the Excel file
            sheet_name: Name of the sheet to load (optional)
            data_type: Type of data ('raw', 'processed', 'external')
            
        Returns:
            DataFrame containing the loaded data
        """
        data_dirs = {
            "raw": self.raw_dir,
            "processed": self.processed_dir,
            "external": self.external_dir
        }
        
        file_path = data_dirs[data_type] / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} not found")
        
        logger.info(f"Loading data from {file_path}")
        return pd.read_excel(file_path, sheet_name=sheet_name)


class DataProcessor:
    """Process and clean migration data."""
    
    def __init__(self):
        """Initialize DataProcessor."""
        self.logger = logging.getLogger(__name__)
    
    def clean_migration_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean migration dataset.
        
        Args:
            df: Raw migration data
            
        Returns:
            Cleaned DataFrame
        """
        self.logger.info("Starting data cleaning process")
        
        # Make a copy to avoid modifying original data
        cleaned_df = df.copy()
        
        # Remove duplicates
        initial_rows = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        duplicates_removed = initial_rows - len(cleaned_df)
        if duplicates_removed > 0:
            self.logger.info(f"Removed {duplicates_removed} duplicate rows")
        
        # Handle missing values
        missing_info = cleaned_df.isnull().sum()
        if missing_info.sum() > 0:
            self.logger.info("Missing values found:")
            for col, missing_count in missing_info[missing_info > 0].items():
                self.logger.info(f"  {col}: {missing_count} missing values")
        
        return cleaned_df
    
    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names (lowercase, underscores).
        
        Args:
            df: DataFrame with columns to standardize
            
        Returns:
            DataFrame with standardized column names
        """
        df = df.copy()
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
        self.logger.info("Column names standardized")
        return df
    
    def validate_data_types(self, df: pd.DataFrame, 
                          expected_types: Dict[str, str]) -> pd.DataFrame:
        """
        Validate and convert data types.
        
        Args:
            df: DataFrame to validate
            expected_types: Dictionary mapping column names to expected types
            
        Returns:
            DataFrame with corrected data types
        """
        df = df.copy()
        
        for col, expected_type in expected_types.items():
            if col in df.columns:
                try:
                    if expected_type == 'datetime':
                        df[col] = pd.to_datetime(df[col])
                    elif expected_type == 'numeric':
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    elif expected_type == 'category':
                        df[col] = df[col].astype('category')
                    
                    self.logger.info(f"Converted {col} to {expected_type}")
                except Exception as e:
                    self.logger.warning(f"Could not convert {col} to {expected_type}: {e}")
        
        return df
    
    def save_processed_data(self, df: pd.DataFrame, filename: str, 
                          data_dir: str = "data/processed") -> None:
        """
        Save processed data to file.
        
        Args:
            df: DataFrame to save
            filename: Name of the output file
            data_dir: Directory to save the file
        """
        output_path = Path(data_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if filename.endswith('.csv'):
            df.to_csv(output_path, index=False)
        elif filename.endswith('.pkl'):
            df.to_pickle(output_path)
        else:
            raise ValueError("Unsupported file format. Use .csv or .pkl")
        
        self.logger.info(f"Processed data saved to {output_path}")
