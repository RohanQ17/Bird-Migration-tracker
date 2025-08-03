"""
Tests for data loading and processing functionality.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

# Import the modules we want to test
# Note: These will work once the packages are installed
try:
    from migration_tracker.data import DataLoader, DataProcessor
except ImportError:
    # For testing without installation
    import sys
    sys.path.append(str(Path(__file__).parent.parent / "src"))
    from migration_tracker.data import DataLoader, DataProcessor


class TestDataLoader:
    """Test DataLoader functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_loader = DataLoader(self.temp_dir)
        
        # Create test directories
        self.data_loader.raw_dir.mkdir(parents=True, exist_ok=True)
        self.data_loader.processed_dir.mkdir(parents=True, exist_ok=True)
        
    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_csv_success(self, sample_migration_data):
        """Test successful CSV loading."""
        # Create test CSV file
        test_file = self.data_loader.raw_dir / "test_data.csv"
        sample_migration_data.to_csv(test_file, index=False)
        
        # Load the data
        loaded_data = self.data_loader.load_csv("test_data.csv", "raw")
        
        # Assert data is loaded correctly
        assert len(loaded_data) == len(sample_migration_data)
        assert list(loaded_data.columns) == list(sample_migration_data.columns)
    
    def test_load_csv_file_not_found(self):
        """Test loading non-existent CSV file."""
        with pytest.raises(FileNotFoundError):
            self.data_loader.load_csv("nonexistent.csv", "raw")
    
    def test_load_csv_invalid_data_type(self):
        """Test loading with invalid data type."""
        with pytest.raises(ValueError):
            self.data_loader.load_csv("test.csv", "invalid")


class TestDataProcessor:
    """Test DataProcessor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = DataProcessor()
    
    def test_clean_migration_data(self, sample_migration_data):
        """Test data cleaning functionality."""
        # Add some duplicates and missing values
        dirty_data = sample_migration_data.copy()
        
        # Add duplicate rows
        dirty_data = pd.concat([dirty_data, dirty_data.iloc[:5]], ignore_index=True)
        
        # Add missing values
        dirty_data.loc[0:10, 'migration_count'] = np.nan
        
        # Clean the data
        cleaned_data = self.processor.clean_migration_data(dirty_data)
        
        # Assert duplicates are removed
        assert len(cleaned_data) <= len(dirty_data)
        assert not cleaned_data.duplicated().any()
    
    def test_standardize_column_names(self):
        """Test column name standardization."""
        df = pd.DataFrame({
            'Migration Count': [1, 2, 3],
            'Origin-Country': ['A', 'B', 'C'],
            'DESTINATION REGION': ['X', 'Y', 'Z']
        })
        
        standardized = self.processor.standardize_column_names(df)
        expected_columns = ['migration_count', 'origin_country', 'destination_region']
        
        assert list(standardized.columns) == expected_columns
    
    def test_validate_data_types(self):
        """Test data type validation."""
        df = pd.DataFrame({
            'date': ['2020-01-01', '2020-02-01', '2020-03-01'],
            'count': ['10', '20', '30'],
            'category': ['A', 'B', 'A']
        })
        
        expected_types = {
            'date': 'datetime',
            'count': 'numeric',
            'category': 'category'
        }
        
        validated = self.processor.validate_data_types(df, expected_types)
        
        assert pd.api.types.is_datetime64_any_dtype(validated['date'])
        assert pd.api.types.is_numeric_dtype(validated['count'])
        assert pd.api.types.is_categorical_dtype(validated['category'])
    
    def test_save_processed_data(self, sample_migration_data):
        """Test saving processed data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test CSV saving
            csv_file = "test_output.csv"
            self.processor.save_processed_data(
                sample_migration_data, csv_file, temp_dir
            )
            
            csv_path = Path(temp_dir) / csv_file
            assert csv_path.exists()
            
            # Verify saved data can be loaded
            loaded = pd.read_csv(csv_path)
            assert len(loaded) == len(sample_migration_data)
    
    def test_save_unsupported_format(self, sample_migration_data):
        """Test saving with unsupported format."""
        with pytest.raises(ValueError):
            self.processor.save_processed_data(
                sample_migration_data, "test.txt", "/tmp"
            )
