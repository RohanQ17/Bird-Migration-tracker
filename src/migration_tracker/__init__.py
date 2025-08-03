"""
Migration Tracker - A data science toolkit for migration analysis.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .data import DataLoader, DataProcessor
from .analysis import MigrationAnalyzer
from .visualization import MigrationVisualizer

__all__ = [
    "DataLoader",
    "DataProcessor", 
    "MigrationAnalyzer",
    "MigrationVisualizer"
]
