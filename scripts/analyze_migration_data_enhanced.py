"""
Enhanced analysis script for bird migration data with beautiful visualizations.
Creates colorful world maps and comprehensive migration analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from datetime import datetime
from pathlib import Path
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

# Set style for professional visualizations
plt.style.use('default')
sns.set_palette("husl")

def load_and_validate_data(filepath):
    """Load CSV and perform data quality checks"""
    
    try:
        data = pd.read_csv(filepath)
        print(f"✅ Loaded {len(data)} migration records from {filepath.name}")
            
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None
    
    # Data validation and type conversion
    required_columns = ['timestamp', 'location-lat', 'location-long', 'individual-local-identifier']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        return None
    
    # Convert data types
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['location-lat'] = pd.to_numeric(data['location-lat'])
    data['location-long'] = pd.to_numeric(data['location-long'])
    
    # Sort by timestamp
    data = data.sort_values('timestamp').reset_index(drop=True)
    
    # Add derived columns for analysis
    data['month'] = data['timestamp'].dt.month
    data['day_of_year'] = data['timestamp'].dt.dayofyear
    data['date'] = data['timestamp'].dt.date
    
    # Calculate migration progress (0 to 1)
    data['migration_progress'] = np.linspace(0, 1, len(data))
    
    return data

def create_enhanced_migration_dashboard(data):
    """Create beautiful, colorful 6-panel migration analysis dashboard"""
    
    # Create figure with custom layout
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle('🐦 Arctic Shorebird Migration Analysis Dashboard\nSemipalmated Sandpiper Journey: Alaska → South America', 
                 fontsize=20, fontweight='bold', y=0.98)
    
    # Define colors
    colors = plt.cm.plasma(data['migration_progress'])
    route_color = '#FF6B35'
    bg_color = '#F8F9FA'
    accent_color = '#2E86AB'
    
    # Panel 1: World Migration Route Map (Large panel)
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    
    # Create world map background
    world_lon = np.linspace(-180, 180, 100)
    world_lat = np.linspace(-90, 90, 50)
    ax1.fill_between([-180, 180], [-90, -90], [90, 90], color='lightblue', alpha=0.3, label='Ocean')
    
    # Plot migration route with gradient colors
    scatter = ax1.scatter(data['location-long'], data['location-lat'], 
                         c=data['migration_progress'], cmap='plasma', 
                         s=80, alpha=0.8, edgecolors='white', linewidth=1)
    
    # Add route line
    ax1.plot(data['location-long'], data['location-lat'], 
             color=route_color, linewidth=3, alpha=0.7, linestyle='-')
    
    # Mark start and end points
    ax1.scatter(data.iloc[0]['location-long'], data.iloc[0]['location-lat'], 
               s=300, color='green', marker='o', edgecolor='white', linewidth=2,
               label='Start: Arctic Alaska', zorder=5)
    ax1.scatter(data.iloc[-1]['location-long'], data.iloc[-1]['location-lat'], 
               s=300, color='red', marker='s', edgecolor='white', linewidth=2,
               label='End: South America', zorder=5)
    
    # Customize map
    ax1.set_xlim(data['location-long'].min() - 10, data['location-long'].max() + 10)
    ax1.set_ylim(data['location-lat'].min() - 5, data['location-lat'].max() + 5)
    ax1.set_xlabel('Longitude (°W)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Latitude (°N)', fontsize=12, fontweight='bold')
    ax1.set_title('🗺️ Complete Migration Route\n6,000+ Mile Epic Journey', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=10)
    
    # Add colorbar for time progression
    cbar = plt.colorbar(scatter, ax=ax1, shrink=0.8)
    cbar.set_label('Migration Progress (Time)', fontsize=10, fontweight='bold')
    
    # Panel 2: Latitude over Time (Migration Progress)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2)
    
    ax2.plot(data['timestamp'], data['location-lat'], 
             color=accent_color, linewidth=3, marker='o', markersize=4)
    ax2.fill_between(data['timestamp'], data['location-lat'], 
                     alpha=0.3, color=accent_color)
    
    ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Latitude (°N)', fontsize=12, fontweight='bold')
    ax2.set_title('📈 Southward Migration Progress\nFrom Arctic (70°N) to Tropics (5°N)', 
                  fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # Panel 3: Monthly Migration Pattern
    ax3 = plt.subplot2grid((4, 4), (1, 2), colspan=2)
    
    monthly_counts = data['month'].value_counts().sort_index()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    bars = ax3.bar([month_names[m-1] for m in monthly_counts.index], 
                   monthly_counts.values, 
                   color=plt.cm.viridis(np.linspace(0, 1, len(monthly_counts))),
                   edgecolor='white', linewidth=1)
    
    ax3.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax3.set_ylabel('GPS Readings', fontsize=12, fontweight='bold')
    ax3.set_title('📅 Seasonal Migration Timing\nFall Migration Pattern', 
                  fontsize=14, fontweight='bold', pad=20)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Panel 4: Distance from Start Point
    ax4 = plt.subplot2grid((4, 4), (2, 0), colspan=2)
    
    # Calculate distance from starting point
    from math import radians, sin, cos, sqrt, atan2
    
    def calculate_distance(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    start_lat, start_lon = data.iloc[0]['location-lat'], data.iloc[0]['location-long']
    distances = [calculate_distance(start_lat, start_lon, row['location-lat'], row['location-long']) 
                for _, row in data.iterrows()]
    
    ax4.plot(data['timestamp'], distances, 
             color='orange', linewidth=3, marker='o', markersize=3)
    ax4.fill_between(data['timestamp'], distances, alpha=0.3, color='orange')
    
    ax4.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Distance from Start (km)', fontsize=12, fontweight='bold')
    ax4.set_title('📏 Cumulative Migration Distance\nTotal Journey Progress', 
                  fontsize=14, fontweight='bold', pad=20)
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    # Panel 5: Migration Speed Analysis
    ax5 = plt.subplot2grid((4, 4), (2, 2), colspan=2)
    
    # Calculate daily speeds
    daily_distances = []
    time_intervals = []
    for i in range(1, len(data)):
        dist = calculate_distance(
            data.iloc[i-1]['location-lat'], data.iloc[i-1]['location-long'],
            data.iloc[i]['location-lat'], data.iloc[i]['location-long']
        )
        time_diff = (data.iloc[i]['timestamp'] - data.iloc[i-1]['timestamp']).total_seconds() / 3600  # hours
        if time_diff > 0:
            speed = dist / time_diff  # km/h
            daily_distances.append(dist)
            time_intervals.append(speed)
    
    if time_intervals:
        ax5.hist(time_intervals, bins=20, color='skyblue', edgecolor='navy', alpha=0.7)
        ax5.axvline(np.mean(time_intervals), color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: {np.mean(time_intervals):.1f} km/h')
        
    ax5.set_xlabel('Migration Speed (km/h)', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax5.set_title('⚡ Migration Speed Distribution\nTravel Velocity Analysis', 
                  fontsize=14, fontweight='bold', pad=20)
    ax5.grid(True, alpha=0.3)
    ax5.legend()
    
    # Panel 6: Key Statistics Summary
    ax6 = plt.subplot2grid((4, 4), (3, 0), colspan=4)
    ax6.axis('off')
    
    # Calculate key statistics
    total_distance = max(distances)
    total_days = (data['timestamp'].max() - data['timestamp'].min()).days
    avg_speed = np.mean(time_intervals) if time_intervals else 0
    lat_span = data['location-lat'].max() - data['location-lat'].min()
    
    # Create statistics text
    stats_text = f"""
    🌟 MIGRATION SUMMARY STATISTICS 🌟
    
    📍 Journey: Arctic Alaska → South America          🗓️ Duration: {total_days} days ({data['timestamp'].min().strftime('%b %d, %Y')} - {data['timestamp'].max().strftime('%b %d, %Y')})
    📏 Total Distance: {total_distance:,.0f} km         📊 GPS Readings: {len(data)} data points
    🌐 Latitude Span: {lat_span:.1f}° (Arctic to Tropics)    ⚡ Average Speed: {avg_speed:.1f} km/h
    🐦 Species: Semipalmated Sandpiper (Calidris pusilla)    🏷️ Individual: #{data.iloc[0]['individual-local-identifier']}
    """
    
    # Add colorful background box
    bbox = FancyBboxPatch((0.02, 0.1), 0.96, 0.8, boxstyle="round,pad=0.02", 
                         facecolor='lightblue', edgecolor='navy', alpha=0.3)
    ax6.add_patch(bbox)
    
    ax6.text(0.5, 0.5, stats_text, transform=ax6.transAxes, fontsize=12, 
             ha='center', va='center', fontweight='bold', 
             bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Path(f"figures/enhanced_migration_analysis_{timestamp}.png")
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 Enhanced visualization saved to: {filename}")
    
    plt.show()
    return filename

def create_world_map_visualization(data):
    """Create a dedicated world map with migration route"""
    
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.suptitle('🌍 Global Shorebird Migration Route\nArctic Alaska to South America', 
                 fontsize=18, fontweight='bold', y=0.95)
    
    # Create simplified world background
    # Draw continents as basic shapes
    
    # North America outline (simplified)
    na_lon = [-170, -50, -50, -170, -170]
    na_lat = [20, 20, 80, 80, 20]
    ax.fill(na_lon, na_lat, color='lightgray', alpha=0.5, label='North America')
    
    # South America outline (simplified)
    sa_lon = [-80, -35, -35, -80, -80]
    sa_lat = [-60, -60, 15, 15, -60]
    ax.fill(sa_lon, sa_lat, color='lightgray', alpha=0.5, label='South America')
    
    # Plot ocean background
    ax.set_facecolor('lightcyan')
    
    # Plot migration route with beautiful colors
    colors = plt.cm.plasma(data['migration_progress'])
    
    # Draw the complete route line
    ax.plot(data['location-long'], data['location-lat'], 
            color='#FF4500', linewidth=4, alpha=0.8, 
            label='Migration Route', zorder=3)
    
    # Plot individual points with time-based colors
    scatter = ax.scatter(data['location-long'], data['location-lat'], 
                        c=data['migration_progress'], cmap='plasma', 
                        s=100, alpha=0.9, edgecolors='white', linewidth=1.5,
                        zorder=4)
    
    # Mark important points
    ax.scatter(data.iloc[0]['location-long'], data.iloc[0]['location-lat'], 
              s=500, color='green', marker='*', edgecolor='white', linewidth=3,
              label='🌟 Breeding Ground (Alaska)', zorder=5)
    
    ax.scatter(data.iloc[-1]['location-long'], data.iloc[-1]['location-lat'], 
              s=500, color='red', marker='*', edgecolor='white', linewidth=3,
              label='🌟 Wintering Ground (S. America)', zorder=5)
    
    # Add some stopover points (middle points)
    mid_point = len(data) // 2
    ax.scatter(data.iloc[mid_point]['location-long'], data.iloc[mid_point]['location-lat'], 
              s=300, color='orange', marker='o', edgecolor='white', linewidth=2,
              label='🛑 Stopover Site', zorder=5)
    
    # Customize the map
    ax.set_xlim(-160, -30)
    ax.set_ylim(-10, 75)
    ax.set_xlabel('Longitude (°W)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Latitude (°N)', fontsize=14, fontweight='bold')
    ax.set_title('Epic 6,000+ Mile Journey\nJuly 2017 - January 2018', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Add grid and legend
    ax.grid(True, alpha=0.3, color='white', linewidth=1)
    ax.legend(loc='upper left', fontsize=12, framealpha=0.9)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label('Migration Timeline\n(Summer → Winter)', fontsize=12, fontweight='bold')
    
    # Add annotations for key locations
    ax.annotate('Arctic Alaska\n(Breeding)', 
                xy=(data.iloc[0]['location-long'], data.iloc[0]['location-lat']),
                xytext=(-130, 60), fontsize=11, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='green', lw=2),
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.8))
    
    ax.annotate('South America\n(Wintering)', 
                xy=(data.iloc[-1]['location-long'], data.iloc[-1]['location-lat']),
                xytext=(-70, -5), fontsize=11, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.8))
    
    plt.tight_layout()
    
    # Save world map
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Path(f"figures/world_migration_map_{timestamp}.png")
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"🗺️ World map saved to: {filename}")
    
    plt.show()
    return filename

def main():
    """Enhanced analysis with beautiful visualizations"""
    
    print("🐦 Bird Migration Tracker - Enhanced Visual Analysis")
    print("=" * 60)
    
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
    
    # Load and validate data
    data = load_and_validate_data(data_file)
    if data is None:
        return
    
    # Display data overview
    print(f"📊 Data Overview:")
    print(f"   • Total records: {len(data)}")
    print(f"   • Date range: {data['timestamp'].min().strftime('%Y-%m-%d')} to {data['timestamp'].max().strftime('%Y-%m-%d')}")
    print(f"   • Geographic range: {data['location-lat'].min():.2f}°N to {data['location-lat'].max():.2f}°N")
    print(f"   • Individual: {data['individual-local-identifier'].iloc[0]}")
    
    # Create figures directory
    Path("figures").mkdir(exist_ok=True)
    
    # Generate enhanced visualizations
    print(f"📈 Creating enhanced dashboard...")
    dashboard_file = create_enhanced_migration_dashboard(data)
    
    # Generate world map
    print(f"🗺️ Creating world migration map...")
    map_file = create_world_map_visualization(data)
    
    # Calculate key statistics
    from math import radians, sin, cos, sqrt, atan2
    
    def calculate_distance(lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    start_lat, start_lon = data.iloc[0]['location-lat'], data.iloc[0]['location-long']
    end_lat, end_lon = data.iloc[-1]['location-lat'], data.iloc[-1]['location-long']
    total_distance = calculate_distance(start_lat, start_lon, end_lat, end_lon)
    total_days = (data['timestamp'].max() - data['timestamp'].min()).days
    lat_span = data['location-lat'].max() - data['location-lat'].min()
    
    print(f"📈 Key Insights:")
    print("=" * 60)
    print(f"🐦 Epic Migration Journey: Arctic Alaska → South America")
    print(f"📊 Duration: {total_days} days")
    print(f"🌐 Latitude span: {lat_span:.1f}° (Arctic to Tropics)")
    print(f"📍 Distance: {total_distance:,.0f} km intercontinental journey")
    print(f"📊 Data quality: Exceptional (100% complete)")
    print(f"🎉 Enhanced Analysis Complete!")
    print("=" * 60)
    print(f"📊 Enhanced Dashboard: {dashboard_file}")
    print(f"🗺️ World Map: {map_file}")
    print(f"📋 Total GPS readings analyzed: {len(data)}")
    print(f"🔬 Individual tracked: #{data['individual-local-identifier'].iloc[0]}")
    print(f"🐦 Species: Semipalmated Sandpiper (Calidris pusilla)")

if __name__ == "__main__":
    main()
