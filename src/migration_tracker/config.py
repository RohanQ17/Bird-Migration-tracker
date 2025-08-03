# Config file for project settings
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Data processing settings
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
CHUNK_SIZE = 10000  # For processing large files
MAX_FILE_SIZE_MB = 500

# Analysis settings
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

# Visualization settings
FIGURE_DPI = 300
FIGURE_FORMAT = "png"
DEFAULT_FIGSIZE = (10, 6)

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Database settings (to be overridden by environment variables)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///migration_data.db")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/migration_tracker")

# API settings
API_TIMEOUT = 30
MAX_RETRIES = 3
