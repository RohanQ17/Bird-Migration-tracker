"""
Visualization utilities for migration data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, List, Dict, Any
import logging

# Set up matplotlib and seaborn styling
plt.style.use('default')
sns.set_palette("husl")

logger = logging.getLogger(__name__)


class MigrationVisualizer:
    """Create visualizations for migration data analysis."""
    
    def __init__(self, style: str = 'default'):
        """
        Initialize MigrationVisualizer.
        
        Args:
            style: Matplotlib style to use
        """
        plt.style.use(style)
        self.logger = logging.getLogger(__name__)
        
        # Default color schemes
        self.color_schemes = {
            'migration': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            'heatmap': 'viridis',
            'sequential': 'Blues'
        }
    
    def plot_migration_trends(self, df: pd.DataFrame,
                            x_col: str,
                            y_col: str,
                            group_col: Optional[str] = None,
                            title: str = "Migration Trends Over Time",
                            interactive: bool = True) -> None:
        """
        Plot migration trends over time.
        
        Args:
            df: Dataset with migration trends
            x_col: Column for x-axis (usually time)
            y_col: Column for y-axis (migration values)
            group_col: Optional column for grouping/coloring lines
            title: Plot title
            interactive: Whether to create interactive plotly chart
        """
        if interactive:
            if group_col:
                fig = px.line(df, x=x_col, y=y_col, color=group_col,
                            title=title,
                            labels={x_col: x_col.replace('_', ' ').title(),
                                   y_col: y_col.replace('_', ' ').title()})
            else:
                fig = px.line(df, x=x_col, y=y_col, title=title,
                            labels={x_col: x_col.replace('_', ' ').title(),
                                   y_col: y_col.replace('_', ' ').title()})
            
            fig.update_layout(
                xaxis_title=x_col.replace('_', ' ').title(),
                yaxis_title=y_col.replace('_', ' ').title(),
                hovermode='x unified'
            )
            fig.show()
        else:
            plt.figure(figsize=(12, 6))
            if group_col:
                for group in df[group_col].unique():
                    group_data = df[df[group_col] == group]
                    plt.plot(group_data[x_col], group_data[y_col], 
                           marker='o', label=group, linewidth=2)
                plt.legend()
            else:
                plt.plot(df[x_col], df[y_col], marker='o', linewidth=2)
            
            plt.title(title, fontsize=16, fontweight='bold')
            plt.xlabel(x_col.replace('_', ' ').title(), fontsize=12)
            plt.ylabel(y_col.replace('_', ' ').title(), fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
        
        self.logger.info("Migration trends plot created")
    
    def plot_correlation_heatmap(self, correlation_matrix: pd.DataFrame,
                               title: str = "Migration Factors Correlation Heatmap",
                               figsize: tuple = (10, 8)) -> None:
        """
        Plot correlation heatmap.
        
        Args:
            correlation_matrix: Correlation matrix to plot
            title: Plot title
            figsize: Figure size
        """
        plt.figure(figsize=figsize)
        
        # Create mask for upper triangle
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        # Generate heatmap
        sns.heatmap(correlation_matrix, 
                   mask=mask,
                   annot=True, 
                   cmap=self.color_schemes['heatmap'],
                   center=0,
                   square=True,
                   fmt='.2f',
                   cbar_kws={"shrink": .8})
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
        self.logger.info("Correlation heatmap created")
    
    def plot_migration_distribution(self, df: pd.DataFrame,
                                  value_col: str,
                                  group_col: Optional[str] = None,
                                  plot_type: str = 'histogram',
                                  title: str = "Migration Distribution") -> None:
        """
        Plot distribution of migration values.
        
        Args:
            df: Dataset
            value_col: Column with values to plot
            group_col: Optional grouping column
            plot_type: Type of plot ('histogram', 'box', 'violin')
            title: Plot title
        """
        plt.figure(figsize=(10, 6))
        
        if plot_type == 'histogram':
            if group_col:
                for group in df[group_col].unique():
                    group_data = df[df[group_col] == group][value_col]
                    plt.hist(group_data, alpha=0.7, label=group, bins=30)
                plt.legend()
            else:
                plt.hist(df[value_col], bins=30, alpha=0.7)
            plt.xlabel(value_col.replace('_', ' ').title())
            plt.ylabel('Frequency')
            
        elif plot_type == 'box':
            if group_col:
                sns.boxplot(data=df, x=group_col, y=value_col)
                plt.xticks(rotation=45)
            else:
                sns.boxplot(y=df[value_col])
            
        elif plot_type == 'violin':
            if group_col:
                sns.violinplot(data=df, x=group_col, y=value_col)
                plt.xticks(rotation=45)
            else:
                sns.violinplot(y=df[value_col])
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
        self.logger.info(f"{plot_type} distribution plot created")
    
    def plot_geographic_migration(self, df: pd.DataFrame,
                                lat_col: str,
                                lon_col: str,
                                size_col: Optional[str] = None,
                                color_col: Optional[str] = None,
                                title: str = "Geographic Migration Patterns") -> None:
        """
        Plot geographic migration patterns.
        
        Args:
            df: Dataset with geographic information
            lat_col: Latitude column
            lon_col: Longitude column
            size_col: Optional column for marker size
            color_col: Optional column for marker color
            title: Plot title
        """
        fig = px.scatter_mapbox(df,
                              lat=lat_col,
                              lon=lon_col,
                              size=size_col,
                              color=color_col,
                              hover_data=df.columns,
                              mapbox_style="open-street-map",
                              title=title,
                              zoom=3)
        
        fig.update_layout(
            height=600,
            margin={"r": 0, "t": 50, "l": 0, "b": 0}
        )
        
        fig.show()
        self.logger.info("Geographic migration plot created")
    
    def plot_seasonal_patterns(self, seasonal_data: Dict,
                             title: str = "Seasonal Migration Patterns") -> None:
        """
        Plot seasonal migration patterns.
        
        Args:
            seasonal_data: Dictionary with seasonal statistics
            title: Plot title
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Monthly averages
        monthly_avg = seasonal_data.get('monthly_avg', pd.Series())
        axes[0, 0].bar(monthly_avg.index, monthly_avg.values, 
                      color=self.color_schemes['migration'][0])
        axes[0, 0].set_title('Monthly Averages')
        axes[0, 0].set_xlabel('Month')
        axes[0, 0].set_ylabel('Average Migration')
        
        # Quarterly averages
        quarterly_avg = seasonal_data.get('quarterly_avg', pd.Series())
        axes[0, 1].bar(quarterly_avg.index, quarterly_avg.values,
                      color=self.color_schemes['migration'][1])
        axes[0, 1].set_title('Quarterly Averages')
        axes[0, 1].set_xlabel('Quarter')
        axes[0, 1].set_ylabel('Average Migration')
        
        # Yearly trends
        yearly_avg = seasonal_data.get('yearly_avg', pd.Series())
        axes[1, 0].plot(yearly_avg.index, yearly_avg.values,
                       marker='o', color=self.color_schemes['migration'][2])
        axes[1, 0].set_title('Yearly Trends')
        axes[1, 0].set_xlabel('Year')
        axes[1, 0].set_ylabel('Average Migration')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Monthly variation (std)
        monthly_std = seasonal_data.get('monthly_std', pd.Series())
        axes[1, 1].bar(monthly_std.index, monthly_std.values,
                      color=self.color_schemes['migration'][3])
        axes[1, 1].set_title('Monthly Variation (Std Dev)')
        axes[1, 1].set_xlabel('Month')
        axes[1, 1].set_ylabel('Standard Deviation')
        
        plt.tight_layout()
        plt.show()
        
        self.logger.info("Seasonal patterns plot created")
    
    def plot_cluster_analysis(self, df: pd.DataFrame,
                            cluster_col: str = 'cluster',
                            feature_cols: Optional[List[str]] = None,
                            title: str = "Migration Clustering Analysis") -> None:
        """
        Plot cluster analysis results.
        
        Args:
            df: Dataset with cluster labels
            cluster_col: Column containing cluster labels
            feature_cols: Features used for clustering
            title: Plot title
        """
        if feature_cols is None:
            feature_cols = [col for col in df.columns if col != cluster_col]
        
        # If we have 2 or more features, create scatter plot
        if len(feature_cols) >= 2:
            plt.figure(figsize=(12, 5))
            
            # 2D scatter plot
            plt.subplot(1, 2, 1)
            scatter = plt.scatter(df[feature_cols[0]], df[feature_cols[1]], 
                                c=df[cluster_col], cmap='viridis', alpha=0.6)
            plt.xlabel(feature_cols[0].replace('_', ' ').title())
            plt.ylabel(feature_cols[1].replace('_', ' ').title())
            plt.title('Cluster Scatter Plot')
            plt.colorbar(scatter)
            
            # Cluster size distribution
            plt.subplot(1, 2, 2)
            cluster_counts = df[cluster_col].value_counts().sort_index()
            plt.bar(cluster_counts.index, cluster_counts.values,
                   color=self.color_schemes['migration'])
            plt.xlabel('Cluster')
            plt.ylabel('Number of Points')
            plt.title('Cluster Size Distribution')
            
            plt.suptitle(title, fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.show()
        
        self.logger.info("Cluster analysis plot created")
    
    def create_dashboard_summary(self, df: pd.DataFrame,
                               migration_col: str,
                               time_col: Optional[str] = None) -> None:
        """
        Create a summary dashboard with key migration metrics.
        
        Args:
            df: Migration dataset
            migration_col: Column with migration values
            time_col: Optional time column for trends
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Migration Distribution', 'Top Regions', 
                          'Monthly Trends', 'Summary Statistics'),
            specs=[[{"type": "histogram"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "table"}]]
        )
        
        # Distribution
        fig.add_trace(
            go.Histogram(x=df[migration_col], name="Distribution"),
            row=1, col=1
        )
        
        # Top regions (if available)
        if 'region' in df.columns:
            top_regions = df.groupby('region')[migration_col].sum().nlargest(10)
            fig.add_trace(
                go.Bar(x=top_regions.index, y=top_regions.values, name="Top Regions"),
                row=1, col=2
            )
        
        # Time trends (if time column available)
        if time_col and time_col in df.columns:
            df_time = df.copy()
            df_time[time_col] = pd.to_datetime(df_time[time_col])
            monthly_trend = df_time.groupby(df_time[time_col].dt.to_period('M'))[migration_col].sum()
            fig.add_trace(
                go.Scatter(x=monthly_trend.index.astype(str), y=monthly_trend.values, 
                          mode='lines+markers', name="Monthly Trend"),
                row=2, col=1
            )
        
        # Summary statistics table
        stats = df[migration_col].describe()
        fig.add_trace(
            go.Table(
                header=dict(values=['Statistic', 'Value']),
                cells=dict(values=[stats.index, [f"{val:.2f}" for val in stats.values]])
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=800, title_text="Migration Data Dashboard", 
                         showlegend=False)
        fig.show()
        
        self.logger.info("Dashboard summary created")
