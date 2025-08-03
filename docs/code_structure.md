# 💻 Code Structure - Understanding the Implementation

## 🎯 Learning Objectives

This document explains how the code is organized and why, designed to teach programming concepts through the Bird Migration Tracker implementation.

## 📁 File Organization Strategy

### **Why Two Main Scripts?**

```
scripts/
├── fetch_movebank_data.py    # Handles data acquisition
└── analyze_migration_data.py # Handles data analysis
```

**Design Principle: Single Responsibility**
- Each script has ONE clear job
- Easy to understand, test, and modify
- Follows Unix philosophy: "Do one thing and do it well"

**Real-world Parallel**: Like having separate kitchen tools for cutting and cooking - each tool excels at its specific task.

## 🔍 Script 1: Data Fetcher (`fetch_movebank_data.py`)

### **High-Level Structure**

```python
# 1. Import libraries
import requests, pandas, json, os
from datetime import datetime

# 2. Configuration
CSV_URL = "https://arctic-shoebird-migration.s3.us-east-1.amazonaws.com/..."
OUTPUT_DIR = "data/movebank/"

# 3. Core functions
def download_csv_from_url(url, filename)
def analyze_downloaded_data(filepath)
def generate_summary_report(data, filepath)

# 4. Main execution
if __name__ == "__main__":
    main()
```

### **Function-by-Function Breakdown**

**Function 1: `download_csv_from_url()`**
```python
def download_csv_from_url(url, output_path):
    """Download CSV file from URL with error handling"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raises exception for bad status codes
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save file
        with open(output_path, 'wb') as f:
            f.write(response.content)
            
        return True
    except Exception as e:
        print(f"Error downloading: {e}")
        return False
```

**Teaching Points:**
- **Error Handling**: `try/except` blocks for robust code
- **HTTP Requests**: Using `requests` library for web data
- **File I/O**: Writing binary data to files
- **Directory Management**: Creating folders automatically

**Function 2: `analyze_downloaded_data()`**
```python
def analyze_downloaded_data(filepath):
    """Load and analyze the downloaded CSV"""
    # Load data into pandas DataFrame
    data = pd.read_csv(filepath)
    
    # Basic statistics
    stats = {
        'total_records': len(data),
        'columns': list(data.columns),
        'unique_individuals': data['individual-local-identifier'].nunique(),
        'unique_species': data['individual-taxon-canonical-name'].nunique(),
        'date_range': {
            'start': data['timestamp'].min(),
            'end': data['timestamp'].max()
        }
    }
    
    return data, stats
```

**Teaching Points:**
- **pandas Usage**: Loading and analyzing CSV data
- **Dictionary Structure**: Organizing results in key-value pairs
- **Data Exploration**: Getting basic information about datasets
- **Statistical Functions**: `nunique()`, `min()`, `max()`, `len()`

### **User Interface Design**

```python
def main():
    print("🐦 Bird Migration Tracker - Public Data Fetcher")
    print("=" * 50)
    
    # Interactive menu
    print("📡 Data source options:")
    print("1. 🐦 Use Arctic Shorebird Migration data (default)")
    print("2. 🔗 Enter your own S3 URL")
    
    choice = input("Enter choice (1 or 2, default=1): ").strip() or "1"
```

**Teaching Points:**
- **User Experience**: Clear prompts and visual formatting
- **Input Validation**: Default values and error handling
- **Console Output**: Using emojis and formatting for clarity

## 🔍 Script 2: Data Analyzer (`analyze_migration_data.py`)

### **High-Level Structure**

```python
# 1. Import visualization libraries
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# 2. Configuration
plt.style.use('seaborn-v0_8')  # Set visual style
FIGURE_SIZE = (18, 12)         # Dashboard dimensions

# 3. Analysis functions
def load_and_validate_data()
def create_migration_dashboard()
def generate_analysis_report()

# 4. Visualization functions  
def plot_migration_map()
def plot_species_distribution()
def plot_individual_analysis()
def plot_data_quality()
def plot_temporal_patterns()
def plot_summary_statistics()
```

### **Data Loading and Validation**

```python
def load_and_validate_data(filepath):
    """Load CSV and perform data quality checks"""
    
    # Load data
    data = pd.read_csv(filepath)
    print(f"✅ Loaded {len(data)} migration records")
    
    # Required columns for migration analysis
    required_columns = [
        'timestamp', 'location-lat', 'location-long',
        'individual-local-identifier', 'individual-taxon-canonical-name'
    ]
    
    # Validate required columns exist
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Data type conversions
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['location-lat'] = pd.to_numeric(data['location-lat'])
    data['location-long'] = pd.to_numeric(data['location-long'])
    
    return data
```

**Teaching Points:**
- **Data Validation**: Checking for required columns
- **Type Conversion**: Converting strings to dates and numbers
- **Error Handling**: Raising meaningful exceptions
- **Data Quality**: Ensuring data is analysis-ready

### **Visualization Architecture**

**Dashboard Layout Strategy:**
```python
def create_migration_dashboard(data):
    """Create 6-panel analysis dashboard"""
    
    # Set up 2x3 grid of subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Bird Migration Analysis Dashboard', fontsize=16, fontweight='bold')
    
    # Panel 1: Migration route map
    plot_migration_map(data, axes[0, 0])
    
    # Panel 2: Species distribution
    plot_species_distribution(data, axes[0, 1])
    
    # Panel 3: Individual tracking
    plot_individual_analysis(data, axes[0, 2])
    
    # Panel 4: Data quality metrics
    plot_data_quality(data, axes[1, 0])
    
    # Panel 5: Temporal patterns
    plot_temporal_patterns(data, axes[1, 1])
    
    # Panel 6: Summary statistics
    plot_summary_statistics(data, axes[1, 2])
    
    # Adjust layout and save
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"figures/migration_analysis_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    
    return filename
```

**Teaching Points:**
- **Subplot Management**: Creating multi-panel layouts
- **Code Organization**: Separate functions for each visualization
- **File Naming**: Timestamp-based unique filenames
- **Image Quality**: High DPI for publication-ready output

### **Individual Plot Functions**

**Migration Map Implementation:**
```python
def plot_migration_map(data, ax):
    """Plot GPS points on world map"""
    
    # Set up map boundaries based on data
    lat_min, lat_max = data['location-lat'].min() - 5, data['location-lat'].max() + 5
    lon_min, lon_max = data['location-long'].min() - 5, data['location-long'].max() + 5
    
    # Plot GPS points
    scatter = ax.scatter(data['location-long'], data['location-lat'], 
                        c=range(len(data)), cmap='viridis', 
                        alpha=0.7, s=50)
    
    # Customize map
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Migration Route')
    ax.grid(True, alpha=0.3)
    
    # Add colorbar for time progression
    plt.colorbar(scatter, ax=ax, label='Time Progression')
```

**Teaching Points:**
- **Data-Driven Scaling**: Map boundaries based on actual data
- **Color Mapping**: Using color to show temporal progression
- **Visual Design**: Grid lines, labels, and legends
- **Coordinate Systems**: Working with latitude/longitude

**Statistical Analysis Implementation:**
```python
def plot_summary_statistics(data, ax):
    """Display key migration statistics"""
    
    # Calculate statistics
    total_records = len(data)
    unique_individuals = data['individual-local-identifier'].nunique()
    unique_species = data['individual-taxon-canonical-name'].nunique()
    
    # Geographic extent
    lat_range = data['location-lat'].max() - data['location-lat'].min()
    lon_range = data['location-long'].max() - data['location-long'].min()
    
    # Time span
    time_span = data['timestamp'].max() - data['timestamp'].min()
    
    # Create text summary
    stats_text = f"""
    Migration Analysis Summary
    
    📊 Data Overview:
    • Total GPS Records: {total_records:,}
    • Individuals Tracked: {unique_individuals}
    • Species: {unique_species}
    
    🌍 Geographic Coverage:
    • Latitude Span: {lat_range:.2f}°
    • Longitude Span: {lon_range:.2f}°
    
    ⏰ Temporal Coverage:
    • Duration: {time_span.days} days
    • Start: {data['timestamp'].min().strftime('%Y-%m-%d')}
    • End: {data['timestamp'].max().strftime('%Y-%m-%d')}
    """
    
    # Display as text
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, 
            fontsize=10, verticalalignment='top', fontfamily='monospace')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
```

**Teaching Points:**
- **Statistical Calculations**: Basic descriptive statistics
- **String Formatting**: Creating readable text summaries
- **Text Visualization**: Displaying data as formatted text
- **Date Handling**: Working with datetime objects

## 🔧 Programming Concepts Demonstrated

### **1. Modular Design**

**Functions with Single Purpose:**
```python
# Good: Each function does one thing
def download_data(url): ...
def validate_data(data): ...
def create_visualization(data): ...

# Avoid: Functions that do everything
def do_everything(): ...
```

### **2. Error Handling Strategies**

**Graceful Degradation:**
```python
try:
    data = pd.read_csv(filepath)
except FileNotFoundError:
    print("❌ Data file not found. Run fetch_movebank_data.py first.")
    return None
except pd.errors.EmptyDataError:
    print("❌ Data file is empty.")
    return None
```

### **3. Configuration Management**

**Constants at Top of File:**
```python
# Configuration - easy to modify
DEFAULT_CSV_URL = "https://..."
OUTPUT_DIRECTORY = "data/movebank/"
FIGURE_SIZE = (18, 12)
DPI = 300
```

### **4. Data Processing Pipeline**

**Sequential Processing:**
```python
# Clear data flow
raw_data = load_csv(filepath)
clean_data = validate_and_clean(raw_data)
statistics = calculate_stats(clean_data)
visualization = create_dashboard(clean_data, statistics)
report = generate_report(statistics)
```

## 📊 Library Usage Patterns

### **pandas for Data Manipulation**

```python
# Common patterns used in the project
data = pd.read_csv(filepath)                    # Load data
data['new_column'] = data['old_column'] * 2     # Create columns
grouped = data.groupby('species').size()        # Group and aggregate
filtered = data[data['lat'] > 0]                # Filter rows
data['date'] = pd.to_datetime(data['timestamp']) # Type conversion
```

### **matplotlib for Visualization**

```python
# Visualization patterns
fig, ax = plt.subplots()                    # Create figure
ax.scatter(x, y)                           # Plot data
ax.set_xlabel('X Label')                   # Add labels
plt.savefig('filename.png', dpi=300)       # Save high-quality image
```

### **requests for Web Data**

```python
# HTTP request pattern
response = requests.get(url, timeout=30)
response.raise_for_status()                # Check for errors
data = response.content                    # Get raw data
```

## 🎓 Code Quality Principles

### **1. Readability**
- Clear variable names (`migration_data` not `d`)
- Descriptive function names (`calculate_migration_distance` not `calc`)
- Comments explaining WHY, not just WHAT

### **2. Reliability**
- Input validation before processing
- Error handling for common failures
- Defensive programming practices

### **3. Maintainability**
- Configuration separated from logic
- Functions kept small and focused
- Consistent coding style throughout

### **4. Usability**
- Clear user prompts and messages
- Progress indicators for long operations
- Helpful error messages with solutions

## 🚀 Extension Points

### **Easy Modifications**

1. **Change Data Source**: Modify URL in configuration
2. **Add New Visualizations**: Create new plot functions
3. **Modify Output Format**: Change file extensions and formats
4. **Add Statistics**: Include new calculations in analysis

### **Advanced Extensions**

1. **Database Integration**: Replace CSV with database queries
2. **Real-time Processing**: Add streaming data capabilities
3. **Web Interface**: Convert scripts to web application
4. **Machine Learning**: Add predictive modeling components

## 🔗 Connections to Software Engineering

### **Design Patterns Used**

1. **Command Pattern**: Scripts as executable commands
2. **Template Method**: Consistent structure across scripts
3. **Strategy Pattern**: Different visualization approaches

### **Best Practices Demonstrated**

1. **Separation of Concerns**: Data vs. visualization vs. reporting
2. **DRY Principle**: Reusable functions for common tasks
3. **KISS Principle**: Simple, straightforward implementation
4. **Documentation**: Comprehensive comments and docstrings

This code structure serves as a practical example of how to organize data science projects for clarity, maintainability, and educational value.
