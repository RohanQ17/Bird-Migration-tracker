"""
Simple analysis script for Movebank bird migration data.
Works with CSV data from public S3 buckets - no AWS configuration needed!
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from datetime import datetime
from pathlib import Path

def main():
    """Analyze Movebank data and generate comprehensive migration analysis"""
    
    print("🐦 Bird Migration Tracker - Simple Analysis")
    print("=" * 50)
    
    # 1. Find local Movebank data
    data_dir = Path("data/movebank")
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        print("❌ No migration data found in data/movebank/")
        print("💡 Run: python scripts/fetch_movebank_data.py first!")
        return
    
    # Select data file
    if len(csv_files) == 1:
        data_file = csv_files[0]
        print(f"📄 Using data file: {data_file.name}")
    else:
        print("📋 Multiple data files found:")
        for i, file in enumerate(csv_files):
            print(f"   {i+1}. {file.name}")
        
        while True:
            try:
                choice = int(input("Choose file number: ")) - 1
                if 0 <= choice < len(csv_files):
                    data_file = csv_files[choice]
                    break
                else:
                    print("❌ Invalid choice!")
            except ValueError:
                print("❌ Please enter a number!")
    
    print(f"🔍 Analyzing: {data_file}")
    
    try:
        # 2. Load the data
        print("📊 Loading migration data...")
        df = pd.read_csv(data_file)
        print(f"✅ Loaded {len(df):,} migration records")
        
        # 3. Basic data exploration with actual column names
        print("\n📋 Data Overview:")
        print(f"   • Total records: {len(df):,}")
        print(f"   • Columns: {len(df.columns)}")
        
        # Check for key migration data columns
        key_columns = {
            'individual-local-identifier': 'Individual ID',
            'individual-taxon-canonical-name': 'Species',
            'location-lat': 'Latitude',
            'location-long': 'Longitude',
            'timestamp': 'Timestamp',
            'study-name': 'Study'
        }
        
        print("\n📊 Available data:")
        for col, desc in key_columns.items():
            if col in df.columns:
                if col == 'individual-local-identifier':
                    print(f"   ✅ {desc}: {df[col].nunique():,} unique individuals")
                elif col == 'individual-taxon-canonical-name':
                    print(f"   ✅ {desc}: {df[col].nunique()} species")
                elif col == 'study-name':
                    print(f"   ✅ {desc}: {df[col].nunique()} studies")
                elif col in ['location-lat', 'location-long']:
                    print(f"   ✅ {desc}: Range {df[col].min():.2f} to {df[col].max():.2f}")
                elif col == 'timestamp':
                    print(f"   ✅ {desc}: {df[col].min()} to {df[col].max()}")
                else:
                    print(f"   ✅ {desc}: Available")
            else:
                print(f"   ❌ {desc}: Not found")
        
        # 4. Generate visualizations
        print("\n📈 Generating visualizations...")
        
        # Create figures directory
        figures_dir = Path("figures")
        figures_dir.mkdir(exist_ok=True)
        
        # Analysis timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create comprehensive analysis plot
        plt.figure(figsize=(20, 15))
        
        # Plot 1: Location map
        plt.subplot(2, 3, 1)
        if 'location-lat' in df.columns and 'location-long' in df.columns:
            # Sample data for better performance if dataset is large
            if len(df) > 10000:
                sample_df = df.sample(10000)
                plt.scatter(sample_df['location-long'], sample_df['location-lat'], 
                           alpha=0.5, s=1, c='red')
                plt.title(f'Migration Locations\n(Sample of 10,000 points)')
            else:
                plt.scatter(df['location-long'], df['location-lat'], 
                           alpha=0.5, s=1, c='red')
                plt.title('Migration Locations')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            plt.grid(True, alpha=0.3)
        else:
            plt.text(0.5, 0.5, 'Location data\nnot available', ha='center', va='center')
            plt.title('Migration Map')
        
        # Plot 2: Species distribution
        plt.subplot(2, 3, 2)
        if 'individual-taxon-canonical-name' in df.columns:
            species_counts = df['individual-taxon-canonical-name'].value_counts().head(10)
            species_counts.plot(kind='bar')
            plt.title('Top 10 Species by Records')
            plt.xlabel('Species')
            plt.ylabel('Number of Records')
            plt.xticks(rotation=45)
        else:
            plt.text(0.5, 0.5, 'Species data\nnot available', ha='center', va='center')
            plt.title('Species Distribution')
        
        # Plot 3: Individual activity
        plt.subplot(2, 3, 3)
        if 'individual-local-identifier' in df.columns:
            individual_counts = df['individual-local-identifier'].value_counts().head(20)
            individual_counts.plot(kind='bar')
            plt.title('Top 20 Most Tracked Individuals')
            plt.xlabel('Individual ID')
            plt.ylabel('Number of Records')
            plt.xticks(rotation=45)
        else:
            plt.text(0.5, 0.5, 'Individual ID\nnot available', ha='center', va='center')
            plt.title('Individual Activity')
        
        # Plot 4: Study distribution
        plt.subplot(2, 3, 4)
        if 'study-name' in df.columns:
            study_counts = df['study-name'].value_counts().head(5)
            if len(study_counts) > 1:
                study_counts.plot(kind='pie', autopct='%1.1f%%')
                plt.title('Study Distribution')
            else:
                plt.text(0.5, 0.5, f'Single Study:\n{study_counts.index[0][:50]}...', 
                        ha='center', va='center', wrap=True)
                plt.title('Study Information')
        else:
            plt.text(0.5, 0.5, 'Study data\nnot available', ha='center', va='center')
            plt.title('Study Distribution')
        
        # Plot 5: Sensor types
        plt.subplot(2, 3, 5)
        if 'sensor-type' in df.columns:
            sensor_counts = df['sensor-type'].value_counts()
            sensor_counts.plot(kind='bar')
            plt.title('Sensor Types Used')
            plt.xlabel('Sensor Type')
            plt.ylabel('Number of Records')
            plt.xticks(rotation=45)
        else:
            plt.text(0.5, 0.5, 'Sensor type\ndata not available', ha='center', va='center')
            plt.title('Sensor Types')
        
        # Plot 6: Data summary
        plt.subplot(2, 3, 6)
        
        # Calculate values for summary
        individuals_count = df['individual-local-identifier'].nunique() if 'individual-local-identifier' in df.columns else 'Unknown'
        species_count = df['individual-taxon-canonical-name'].nunique() if 'individual-taxon-canonical-name' in df.columns else 'Unknown'
        studies_count = df['study-name'].nunique() if 'study-name' in df.columns else 'Unknown'
        lat_range = f"{df['location-lat'].min():.2f} to {df['location-lat'].max():.2f}" if 'location-lat' in df.columns else 'N/A'
        lon_range = f"{df['location-long'].min():.2f} to {df['location-long'].max():.2f}" if 'location-long' in df.columns else 'N/A'
        
        summary_text = f"""
Migration Data Summary
---------------------
Total Records: {len(df):,}
Columns: {len(df.columns)}

Individuals: {individuals_count}
Species: {species_count}
Studies: {studies_count}

Location Range:
Lat: {lat_range}
Lon: {lon_range}
        """
        plt.text(0.05, 0.95, summary_text, fontsize=10, verticalalignment='top', 
                horizontalalignment='left', transform=plt.gca().transAxes)
        plt.axis('off')
        plt.title('Analysis Summary')
        
        plt.tight_layout()
        analysis_file = figures_dir / f"migration_analysis_{timestamp}.png"
        plt.savefig(analysis_file, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"📊 Analysis saved to: {analysis_file}")
        
        # 5. Create detailed report
        report_data = {
            "analysis_timestamp": timestamp,
            "data_file": str(data_file),
            "total_records": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "individuals": df['individual-local-identifier'].nunique() if 'individual-local-identifier' in df.columns else None,
            "species": df['individual-taxon-canonical-name'].nunique() if 'individual-taxon-canonical-name' in df.columns else None,
            "studies": df['study-name'].nunique() if 'study-name' in df.columns else None,
            "location_data": {
                "has_coordinates": 'location-lat' in df.columns and 'location-long' in df.columns,
                "lat_range": [float(df['location-lat'].min()), float(df['location-lat'].max())] if 'location-lat' in df.columns else None,
                "lon_range": [float(df['location-long'].min()), float(df['location-long'].max())] if 'location-long' in df.columns else None
            },
            "data_quality": {
                "missing_values": df.isnull().sum().to_dict(),
                "duplicate_records": int(df.duplicated().sum())
            }
        }
        
        # Save report
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        report_file = reports_dir / f"migration_analysis_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"📄 Detailed report saved to: {report_file}")
        
        # 6. Display key insights
        print("\n📈 Key Insights:")
        print("=" * 30)
        
        if 'individual-taxon-canonical-name' in df.columns:
            top_species = df['individual-taxon-canonical-name'].value_counts().iloc[0]
            print(f"🐦 Most tracked species: {df['individual-taxon-canonical-name'].value_counts().index[0]}")
            print(f"   ({top_species:,} records)")
        
        if 'individual-local-identifier' in df.columns:
            avg_records = len(df) / df['individual-local-identifier'].nunique()
            print(f"📊 Average records per individual: {avg_records:.1f}")
            
            top_individual = df['individual-local-identifier'].value_counts().iloc[0]
            print(f"🏆 Most active individual: {df['individual-local-identifier'].value_counts().index[0]}")
            print(f"   ({top_individual:,} records)")
        
        if 'location-lat' in df.columns and 'location-long' in df.columns:
            lat_range = df['location-lat'].max() - df['location-lat'].min()
            lon_range = df['location-long'].max() - df['location-long'].min()
            print(f"🗺️  Geographic coverage:")
            print(f"   Latitude span: {lat_range:.2f}°")
            print(f"   Longitude span: {lon_range:.2f}°")
        
        # 7. Summary
        print("\n🎉 Analysis Complete!")
        print("=" * 50)
        print(f"📊 Visualization: {analysis_file}")
        print(f"📄 Report: {report_file}")
        print(f"📋 Records analyzed: {len(df):,}")
        
        if 'individual-local-identifier' in df.columns:
            print(f"🐦 Unique individuals: {df['individual-local-identifier'].nunique():,}")
        if 'individual-taxon-canonical-name' in df.columns:
            print(f"🔬 Species tracked: {df['individual-taxon-canonical-name'].nunique()}")
        
        print("\n📱 Next steps:")
        print("1. Open Jupyter notebook for interactive analysis")
        print("2. Check reports/ folder for detailed findings")
        print("3. Use figures/ folder for presentations")
        print("4. Share your results with the research community!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check that your CSV file is valid")
        print("2. Ensure required packages are installed: pip install pandas matplotlib seaborn")
        print("3. Check file permissions and disk space")

if __name__ == "__main__":
    main()
