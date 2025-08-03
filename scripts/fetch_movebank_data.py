"""
Simple script to download bird migration data from a public S3 bucket.
No AWS configuration required - just provide the public S3 URL!
"""

import pandas as pd
import requests
from pathlib import Path
import json
from datetime import datetime

def main():
    """Download migration data from public S3 URL and prepare for analysis"""
    
    print("🐦 Bird Migration Tracker - Public Data Fetcher")
    print("=" * 50)
    
    # Default S3 URL for Arctic shorebird data
    default_s3_url = "https://arctic-shoebird-migration.s3.us-east-1.amazonaws.com/Arctic+shorebird+migration+tracking+study+-+Semipalmated+Sandpiper.csv"
    
    # Ask user if they want to use the default or provide their own URL
    print("📡 Data source options:")
    print("1. 🐦 Use Arctic Shorebird Migration data (default)")
    print("2. 🔗 Enter your own S3 URL")
    
    choice = input("\nEnter choice (1 or 2, default=1): ").strip()
    
    if choice == '2':
        print("\n📡 Enter your public S3 URL:")
        print("Example: https://your-bucket.s3.amazonaws.com/migration-data.csv")
        s3_url = input("🔗 S3 URL: ").strip()
        
        if not s3_url:
            print("❌ URL is required!")
            return
    else:
        s3_url = default_s3_url
        print(f"\n🐦 Using Arctic Shorebird Migration data")
        print(f"📡 URL: {s3_url}")
        
        confirm = input("\nProceed with download? (y/n, default=y): ").strip().lower()
        if confirm == 'n':
            return
    
    try:
        # 1. Create data directory
        data_dir = Path("data/movebank")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Extract filename from URL
        filename = s3_url.split('/')[-1]
        if not filename.endswith('.csv'):
            filename = "migration_data.csv"
        
        local_file_path = data_dir / filename
        
        # 3. Download the file
        print(f"📥 Downloading data from S3...")
        print(f"� URL: {s3_url}")
        
        response = requests.get(s3_url)
        response.raise_for_status()
        
        # 4. Save to local file
        with open(local_file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded: {local_file_path}")
        
        # 5. Load and analyze the data
        print("� Analyzing downloaded data...")
        df = pd.read_csv(local_file_path)
        
        # 6. Create data summary with actual column names
        summary = {
            "download_info": {
                "timestamp": datetime.now().isoformat(),
                "source_url": s3_url,
                "local_file": str(local_file_path)
            },
            "data_info": {
                "total_records": len(df),
                "total_columns": len(df.columns),
                "column_names": list(df.columns),
                "file_size_mb": round(local_file_path.stat().st_size / (1024 * 1024), 2)
            },
            "migration_data_summary": {
                "unique_individuals": df['individual-local-identifier'].nunique() if 'individual-local-identifier' in df.columns else "Unknown",
                "unique_species": df['individual-taxon-canonical-name'].nunique() if 'individual-taxon-canonical-name' in df.columns else "Unknown",
                "studies": df['study-name'].nunique() if 'study-name' in df.columns else "Unknown",
                "date_range": {
                    "start": str(df['timestamp'].min()) if 'timestamp' in df.columns else "Unknown",
                    "end": str(df['timestamp'].max()) if 'timestamp' in df.columns else "Unknown"
                },
                "location_range": {
                    "lat_min": float(df['location-lat'].min()) if 'location-lat' in df.columns else None,
                    "lat_max": float(df['location-lat'].max()) if 'location-lat' in df.columns else None,
                    "lon_min": float(df['location-long'].min()) if 'location-long' in df.columns else None,
                    "lon_max": float(df['location-long'].max()) if 'location-long' in df.columns else None
                }
            }
        }
        
        # 7. Save summary
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        summary_file = reports_dir / "movebank_data_summary.json"
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # 8. Display summary
        print("\n🎉 SUCCESS! Your migration data is ready!")
        print("=" * 50)
        print(f"📁 Local file: {local_file_path}")
        print(f"📊 Records: {len(df):,}")
        print(f"📋 Columns: {len(df.columns)}")
        print(f"💾 File size: {summary['data_info']['file_size_mb']} MB")
        
        # 9. Show relevant columns for migration analysis
        migration_columns = [
            'event-id', 'timestamp', 'location-long', 'location-lat', 
            'individual-local-identifier', 'individual-taxon-canonical-name', 
            'study-name', 'sensor-type'
        ]
        
        available_columns = [col for col in migration_columns if col in df.columns]
        print(f"\n📊 Key migration data columns found:")
        for col in available_columns:
            print(f"   ✅ {col}")
        
        missing_columns = [col for col in migration_columns if col not in df.columns]
        if missing_columns:
            print(f"\n⚠️  Missing expected columns:")
            for col in missing_columns:
                print(f"   ❌ {col}")
        
        # 10. Show sample data
        print(f"\n📄 Sample data (first 3 rows):")
        print(df.head(3).to_string())
        
        # 11. Migration-specific insights
        if 'individual-taxon-canonical-name' in df.columns:
            print(f"\n🐦 Species in dataset:")
            species_counts = df['individual-taxon-canonical-name'].value_counts()
            for species, count in species_counts.head(5).items():
                print(f"   • {species}: {count:,} records")
        
        if 'individual-local-identifier' in df.columns:
            print(f"\n🏷️  Individual tracking:")
            print(f"   • Total individuals: {df['individual-local-identifier'].nunique():,}")
            print(f"   • Average records per individual: {len(df) / df['individual-local-identifier'].nunique():.1f}")
        
        # 12. Next steps
        print(f"\n🚀 Next Steps:")
        print("1. Run analysis:")
        print("   python scripts/analyze_movebank_data.py")
        print("\n2. Open interactive notebook:")
        print("   jupyter notebook notebooks/movebank_analysis.ipynb")
        print(f"\n3. Data summary saved to:")
        print(f"   {summary_file}")
        
    except requests.RequestException as e:
        print(f"❌ Error downloading from S3: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check that the URL is correct and accessible")
        print("2. Ensure the bucket is public or has public read access")
        print("3. Verify the file exists at that URL")
        print("4. Check your internet connection")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check the CSV file format")
        print("2. Ensure you have write permissions in the data/ folder")
        print("3. Verify the downloaded file is valid CSV")

if __name__ == "__main__":
    main()
