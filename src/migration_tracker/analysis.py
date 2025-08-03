"""
Analysis utilities for migration data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

logger = logging.getLogger(__name__)


class MigrationAnalyzer:
    """Analyze migration patterns and trends."""
    
    def __init__(self):
        """Initialize MigrationAnalyzer."""
        self.logger = logging.getLogger(__name__)
    
    def descriptive_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Generate descriptive statistics for migration data.
        
        Args:
            df: Migration dataset
            
        Returns:
            Dictionary containing descriptive statistics
        """
        stats_dict = {
            'shape': df.shape,
            'numeric_summary': df.describe(),
            'missing_values': df.isnull().sum(),
            'data_types': df.dtypes
        }
        
        # Add categorical summaries if any categorical columns exist
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            stats_dict['categorical_summary'] = {}
            for col in categorical_cols:
                stats_dict['categorical_summary'][col] = df[col].value_counts()
        
        self.logger.info("Descriptive statistics generated")
        return stats_dict
    
    def migration_trends(self, df: pd.DataFrame, 
                        time_col: str, 
                        migration_col: str,
                        groupby_col: Optional[str] = None) -> pd.DataFrame:
        """
        Analyze migration trends over time.
        
        Args:
            df: Migration dataset
            time_col: Column containing time/date information
            migration_col: Column containing migration data
            groupby_col: Optional column to group by (e.g., region, country)
            
        Returns:
            DataFrame with trend analysis
        """
        if time_col not in df.columns:
            raise ValueError(f"Time column '{time_col}' not found in dataset")
        if migration_col not in df.columns:
            raise ValueError(f"Migration column '{migration_col}' not found in dataset")
        
        # Ensure time column is datetime
        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col])
        
        if groupby_col:
            trends = df.groupby([groupby_col, df[time_col].dt.year])[migration_col].agg([
                'sum', 'mean', 'count'
            ]).reset_index()
        else:
            trends = df.groupby(df[time_col].dt.year)[migration_col].agg([
                'sum', 'mean', 'count'
            ]).reset_index()
        
        self.logger.info("Migration trends analysis completed")
        return trends
    
    def correlation_analysis(self, df: pd.DataFrame, 
                           target_col: str,
                           feature_cols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Perform correlation analysis between migration and other factors.
        
        Args:
            df: Dataset for analysis
            target_col: Target migration column
            feature_cols: List of feature columns (if None, use all numeric columns)
            
        Returns:
            DataFrame with correlation coefficients
        """
        if feature_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_cols = [col for col in numeric_cols if col != target_col]
        
        correlations = []
        for col in feature_cols:
            if col in df.columns and df[col].dtype in [np.number]:
                corr_coef, p_value = stats.pearsonr(df[target_col].dropna(), 
                                                   df[col].dropna())
                correlations.append({
                    'feature': col,
                    'correlation': corr_coef,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                })
        
        corr_df = pd.DataFrame(correlations)
        corr_df = corr_df.sort_values('correlation', key=abs, ascending=False)
        
        self.logger.info("Correlation analysis completed")
        return corr_df
    
    def migration_clustering(self, df: pd.DataFrame, 
                           feature_cols: List[str],
                           n_clusters: int = 5) -> Tuple[pd.DataFrame, Dict]:
        """
        Perform clustering analysis on migration data.
        
        Args:
            df: Dataset for clustering
            feature_cols: Columns to use for clustering
            n_clusters: Number of clusters
            
        Returns:
            Tuple of (DataFrame with cluster labels, clustering info)
        """
        # Prepare data for clustering
        cluster_data = df[feature_cols].copy()
        cluster_data = cluster_data.dropna()
        
        # Standardize features
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(cluster_data)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(scaled_data)
        
        # Add cluster labels to dataframe
        result_df = cluster_data.copy()
        result_df['cluster'] = cluster_labels
        
        # Generate clustering info
        clustering_info = {
            'n_clusters': n_clusters,
            'inertia': kmeans.inertia_,
            'cluster_centers': kmeans.cluster_centers_,
            'feature_columns': feature_cols,
            'cluster_sizes': pd.Series(cluster_labels).value_counts().sort_index()
        }
        
        self.logger.info(f"Clustering analysis completed with {n_clusters} clusters")
        return result_df, clustering_info
    
    def dimensionality_reduction(self, df: pd.DataFrame,
                               feature_cols: List[str],
                               n_components: int = 2) -> Tuple[pd.DataFrame, Dict]:
        """
        Perform PCA for dimensionality reduction.
        
        Args:
            df: Dataset for PCA
            feature_cols: Columns to use for PCA
            n_components: Number of principal components
            
        Returns:
            Tuple of (DataFrame with PCA components, PCA info)
        """
        # Prepare data
        pca_data = df[feature_cols].copy()
        pca_data = pca_data.dropna()
        
        # Standardize features
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(pca_data)
        
        # Perform PCA
        pca = PCA(n_components=n_components)
        pca_components = pca.fit_transform(scaled_data)
        
        # Create result dataframe
        component_cols = [f'PC{i+1}' for i in range(n_components)]
        result_df = pd.DataFrame(pca_components, columns=component_cols, 
                               index=pca_data.index)
        
        # Generate PCA info
        pca_info = {
            'explained_variance_ratio': pca.explained_variance_ratio_,
            'cumulative_variance_ratio': np.cumsum(pca.explained_variance_ratio_),
            'feature_columns': feature_cols,
            'n_components': n_components,
            'total_variance_explained': np.sum(pca.explained_variance_ratio_)
        }
        
        self.logger.info(f"PCA completed with {n_components} components")
        return result_df, pca_info
    
    def seasonal_analysis(self, df: pd.DataFrame,
                         date_col: str,
                         value_col: str) -> Dict:
        """
        Analyze seasonal patterns in migration data.
        
        Args:
            df: Dataset with time series data
            date_col: Column with date information
            value_col: Column with values to analyze
            
        Returns:
            Dictionary with seasonal analysis results
        """
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Extract temporal features
        df['year'] = df[date_col].dt.year
        df['month'] = df[date_col].dt.month
        df['quarter'] = df[date_col].dt.quarter
        df['day_of_year'] = df[date_col].dt.dayofyear
        
        seasonal_stats = {
            'monthly_avg': df.groupby('month')[value_col].mean(),
            'quarterly_avg': df.groupby('quarter')[value_col].mean(),
            'yearly_avg': df.groupby('year')[value_col].mean(),
            'monthly_std': df.groupby('month')[value_col].std(),
            'seasonal_peaks': df.groupby('month')[value_col].mean().idxmax(),
            'seasonal_lows': df.groupby('month')[value_col].mean().idxmin()
        }
        
        self.logger.info("Seasonal analysis completed")
        return seasonal_stats
