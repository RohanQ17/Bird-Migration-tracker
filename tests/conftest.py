"""
Test utilities and fixtures for migration tracker tests.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytest


@pytest.fixture
def sample_migration_data():
    """Create sample migration data for testing."""
    np.random.seed(42)
    
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='M')
    origins = ['Country_A', 'Country_B', 'Country_C', 'Country_D', 'Country_E']
    destinations = ['Region_1', 'Region_2', 'Region_3', 'Region_4', 'Region_5']
    
    data = []
    for date in dates:
        for origin in origins:
            for dest in destinations:
                if origin != dest:  # No internal migration
                    migration_count = np.random.poisson(50)
                    data.append({
                        'date': date,
                        'origin': origin,
                        'destination': dest,
                        'migration_count': migration_count,
                        'economic_factor': np.random.normal(100, 20),
                        'political_stability': np.random.uniform(0, 10),
                        'distance_km': np.random.uniform(100, 5000)
                    })
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_geographic_data():
    """Create sample geographic data for testing."""
    locations = {
        'Country_A': {'lat': 52.5200, 'lon': 13.4050},  # Berlin
        'Country_B': {'lat': 48.8566, 'lon': 2.3522},   # Paris
        'Country_C': {'lat': 51.5074, 'lon': -0.1278},  # London
        'Country_D': {'lat': 41.9028, 'lon': 12.4964},  # Rome
        'Country_E': {'lat': 40.4168, 'lon': -3.7038},  # Madrid
    }
    
    data = []
    for location, coords in locations.items():
        data.append({
            'location': location,
            'latitude': coords['lat'],
            'longitude': coords['lon'],
            'population': np.random.randint(1000000, 10000000),
            'gdp_per_capita': np.random.uniform(20000, 80000)
        })
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_time_series_data():
    """Create sample time series migration data."""
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    
    # Create seasonal pattern with trend
    trend = np.linspace(100, 200, len(dates))
    seasonal = 50 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
    noise = np.random.normal(0, 10, len(dates))
    
    migration_values = trend + seasonal + noise
    migration_values = np.maximum(migration_values, 0)  # Ensure non-negative
    
    return pd.DataFrame({
        'date': dates,
        'migration_count': migration_values
    })


def create_test_config():
    """Create test configuration dictionary."""
    return {
        'data_sources': {
            'primary': 'test_data.csv',
            'secondary': 'test_external.csv'
        },
        'processing': {
            'chunk_size': 1000,
            'date_format': '%Y-%m-%d'
        },
        'analysis': {
            'random_state': 42,
            'test_size': 0.2
        }
    }


def assert_dataframe_equal(df1, df2, check_dtype=True):
    """Helper function to assert DataFrames are equal."""
    pd.testing.assert_frame_equal(df1, df2, check_dtype=check_dtype)


def assert_migration_data_valid(df):
    """Assert that migration data has required structure."""
    required_columns = ['date', 'origin', 'destination', 'migration_count']
    missing_cols = set(required_columns) - set(df.columns)
    assert not missing_cols, f"Missing required columns: {missing_cols}"
    
    # Check data types
    assert pd.api.types.is_datetime64_any_dtype(df['date']) or pd.api.types.is_object_dtype(df['date'])
    assert pd.api.types.is_numeric_dtype(df['migration_count'])
    
    # Check for negative migration counts
    assert (df['migration_count'] >= 0).all(), "Migration counts should be non-negative"
