"""
Utility functions for the migration tracker project.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import json
import yaml


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level
        
    Returns:
        Configured logger
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("migration_tracker.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML or JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file {config_path} not found")
    
    with open(config_path, 'r') as file:
        if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
            config = yaml.safe_load(file)
        elif config_path.suffix.lower() == '.json':
            config = json.load(file)
        else:
            raise ValueError("Configuration file must be YAML or JSON format")
    
    return config


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
    """
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)


def validate_dataframe(df: pd.DataFrame, required_columns: list) -> bool:
    """
    Validate that a DataFrame has required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        True if valid, False otherwise
    """
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        logging.warning(f"Missing required columns: {missing_columns}")
        return False
    return True


def memory_usage_mb(df: pd.DataFrame) -> float:
    """
    Calculate memory usage of DataFrame in MB.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Memory usage in MB
    """
    return df.memory_usage(deep=True).sum() / 1024 / 1024


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame dtypes to reduce memory usage.
    
    Args:
        df: DataFrame to optimize
        
    Returns:
        Optimized DataFrame
    """
    df_optimized = df.copy()
    
    # Optimize integer columns
    for col in df_optimized.select_dtypes(include=['int64']).columns:
        col_min = df_optimized[col].min()
        col_max = df_optimized[col].max()
        
        if col_min >= np.iinfo(np.int8).min and col_max <= np.iinfo(np.int8).max:
            df_optimized[col] = df_optimized[col].astype(np.int8)
        elif col_min >= np.iinfo(np.int16).min and col_max <= np.iinfo(np.int16).max:
            df_optimized[col] = df_optimized[col].astype(np.int16)
        elif col_min >= np.iinfo(np.int32).min and col_max <= np.iinfo(np.int32).max:
            df_optimized[col] = df_optimized[col].astype(np.int32)
    
    # Optimize float columns
    for col in df_optimized.select_dtypes(include=['float64']).columns:
        df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')
    
    # Convert object columns to category where appropriate
    for col in df_optimized.select_dtypes(include=['object']).columns:
        if df_optimized[col].nunique() / len(df_optimized) < 0.5:  # Less than 50% unique values
            df_optimized[col] = df_optimized[col].astype('category')
    
    return df_optimized


def create_date_features(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """
    Create additional date-based features from a datetime column.
    
    Args:
        df: DataFrame with date column
        date_col: Name of the date column
        
    Returns:
        DataFrame with additional date features
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Extract date components
    df[f'{date_col}_year'] = df[date_col].dt.year
    df[f'{date_col}_month'] = df[date_col].dt.month
    df[f'{date_col}_day'] = df[date_col].dt.day
    df[f'{date_col}_quarter'] = df[date_col].dt.quarter
    df[f'{date_col}_dayofweek'] = df[date_col].dt.dayofweek
    df[f'{date_col}_dayofyear'] = df[date_col].dt.dayofyear
    df[f'{date_col}_week'] = df[date_col].dt.isocalendar().week
    
    # Cyclical encoding for seasonal patterns
    df[f'{date_col}_month_sin'] = np.sin(2 * np.pi * df[f'{date_col}_month'] / 12)
    df[f'{date_col}_month_cos'] = np.cos(2 * np.pi * df[f'{date_col}_month'] / 12)
    df[f'{date_col}_day_sin'] = np.sin(2 * np.pi * df[f'{date_col}_day'] / 31)
    df[f'{date_col}_day_cos'] = np.cos(2 * np.pi * df[f'{date_col}_day'] / 31)
    
    return df


def detect_outliers(df: pd.DataFrame, columns: list, method: str = 'iqr') -> pd.DataFrame:
    """
    Detect outliers in specified columns.
    
    Args:
        df: DataFrame to analyze
        columns: List of columns to check for outliers
        method: Method to use ('iqr' or 'zscore')
        
    Returns:
        DataFrame with outlier flags
    """
    df_result = df.copy()
    
    for col in columns:
        if col not in df.columns:
            continue
            
        if method == 'iqr':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df_result[f'{col}_outlier'] = (df[col] < lower_bound) | (df[col] > upper_bound)
            
        elif method == 'zscore':
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            df_result[f'{col}_outlier'] = z_scores > 3
    
    return df_result


def export_results(data: Any, filename: str, format: str = 'csv') -> None:
    """
    Export results to various formats.
    
    Args:
        data: Data to export (DataFrame, dict, etc.)
        filename: Output filename
        format: Export format ('csv', 'excel', 'json', 'pickle')
    """
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if isinstance(data, pd.DataFrame):
        if format == 'csv':
            data.to_csv(output_path, index=False)
        elif format == 'excel':
            data.to_excel(output_path, index=False)
        elif format == 'pickle':
            data.to_pickle(output_path)
        elif format == 'json':
            data.to_json(output_path, orient='records', indent=2)
    elif isinstance(data, dict):
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == 'yaml':
            with open(output_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
    
    logging.info(f"Results exported to {output_path}")


def calculate_migration_metrics(df: pd.DataFrame, 
                              origin_col: str, 
                              destination_col: str,
                              migration_col: str) -> Dict[str, Any]:
    """
    Calculate key migration metrics.
    
    Args:
        df: Migration dataset
        origin_col: Column with origin information
        destination_col: Column with destination information
        migration_col: Column with migration values
        
    Returns:
        Dictionary with migration metrics
    """
    metrics = {}
    
    # Total migration
    metrics['total_migration'] = df[migration_col].sum()
    
    # Top origin and destination locations
    metrics['top_origins'] = df.groupby(origin_col)[migration_col].sum().nlargest(10).to_dict()
    metrics['top_destinations'] = df.groupby(destination_col)[migration_col].sum().nlargest(10).to_dict()
    
    # Migration flows
    metrics['top_flows'] = (df.groupby([origin_col, destination_col])[migration_col]
                           .sum().nlargest(10).to_dict())
    
    # Basic statistics
    metrics['mean_migration'] = df[migration_col].mean()
    metrics['median_migration'] = df[migration_col].median()
    metrics['std_migration'] = df[migration_col].std()
    
    # Net migration by location
    outflow = df.groupby(origin_col)[migration_col].sum()
    inflow = df.groupby(destination_col)[migration_col].sum()
    net_migration = inflow.subtract(outflow, fill_value=0)
    metrics['net_migration'] = net_migration.to_dict()
    
    return metrics
