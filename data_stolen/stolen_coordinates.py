"""
EXTRACT COORDINATES FROM GOOGLE MAPS LINKS
Extracts latitude and longitude from Google Maps URLs and creates new columns
"""

import pandas as pd
import re
from urllib.parse import urlparse, parse_qs

def extract_coordinates_from_google_maps(url):
    """
    Extract latitude and longitude from Google Maps URL
    
    Supports formats:
    - https://maps.google.com/?q=46.629, 32.609&ll=...
    - https://maps.google.com/?q=46.629,32.609
    - https://www.google.com/maps/place/@46.629,32.609
    - https://goo.gl/maps/...
    
    Returns: (latitude, longitude) or (None, None) if not found
    """
    if pd.isna(url) or url == '':
        return None, None
    
    url_str = str(url).strip()
    
    # Pattern 1: ?q=LAT, LON or ?q=LAT,LON
    q_pattern = re.search(r'[?&]q=([0-9.-]+)\s*,\s*([0-9.-]+)', url_str)
    if q_pattern:
        try:
            lat = float(q_pattern.group(1))
            lon = float(q_pattern.group(2))
            return lat, lon
        except:
            pass
    
    # Pattern 2: @LAT,LON (in /place/ URLs)
    at_pattern = re.search(r'@([0-9.-]+),([0-9.-]+)', url_str)
    if at_pattern:
        try:
            lat = float(at_pattern.group(1))
            lon = float(at_pattern.group(2))
            return lat, lon
        except:
            pass
    
    # Pattern 3: ll=LAT,LON
    ll_pattern = re.search(r'll=([0-9.-]+),([0-9.-]+)', url_str)
    if ll_pattern:
        try:
            lat = float(ll_pattern.group(1))
            lon = float(ll_pattern.group(2))
            return lat, lon
        except:
            pass
    
    return None, None

def extract_coordinates_from_csv(input_file, output_file, url_column='google_maps_link'):
    """
    Extract coordinates from Google Maps links in CSV and create latitude/longitude columns
    
    Args:
        input_file: Input CSV file path
        output_file: Output CSV file path
        url_column: Name of column containing Google Maps URLs (default: 'google_maps_link')
    """
    
    print("\n" + "="*70)
    print("EXTRACTING COORDINATES FROM GOOGLE MAPS LINKS")
    print("="*70 + "\n")
    
    # Read CSV
    print(f"📖 Reading file: {input_file}")
    df = pd.read_csv(input_file)
    print(f"✓ {len(df)} objects loaded\n")
    
    # Check if URL column exists
    if url_column not in df.columns:
        print(f"✗ ERROR: Column '{url_column}' not found!")
        print(f"   Available columns: {', '.join(df.columns)}")
        return None
    
    # Count URLs
    url_count = df[url_column].notna().sum()
    print(f"📍 Found {url_count} Google Maps links")
    
    # Extract coordinates
    print("\n🔍 Extracting coordinates...")
    coordinates = df[url_column].apply(extract_coordinates_from_google_maps)
    
    # Split into separate columns
    df['latitude'] = coordinates.apply(lambda x: x[0])
    df['longitude'] = coordinates.apply(lambda x: x[1])
    
    # Count successful extractions
    success_count = df['latitude'].notna().sum()
    print(f"✓ Successfully extracted {success_count} coordinate pairs")
    print(f"✗ Failed to extract {url_count - success_count} coordinates")
    
    # Show statistics
    if success_count > 0:
        print("\n📊 Coordinate Statistics:")
        print("-" * 70)
        print(f"Latitude range:  {df['latitude'].min():.6f} to {df['latitude'].max():.6f}")
        print(f"Longitude range: {df['longitude'].min():.6f} to {df['longitude'].max():.6f}")
        
        # Show sample
        print("\n📍 Sample of extracted coordinates:")
        print("-" * 70)
        sample = df[df['latitude'].notna()][['place_incident', 'latitude', 'longitude']].head(3)
        for idx, row in sample.iterrows():
            print(f"  {row['place_incident']}")
            print(f"    Lat: {row['latitude']:.6f}, Lon: {row['longitude']:.6f}")
        
        # Verify Ukraine range
        print("\n🇺🇦 Ukraine coordinate ranges:")
        print("-" * 70)
        print("Expected: Latitude 44-52°N, Longitude 22-40°E")
        
        ukraine_lat = df[(df['latitude'] >= 44) & (df['latitude'] <= 52)]
        ukraine_lon = df[(df['longitude'] >= 22) & (df['longitude'] <= 40)]
        ukraine_both = df[(df['latitude'] >= 44) & (df['latitude'] <= 52) & 
                          (df['longitude'] >= 22) & (df['longitude'] <= 40)]
        
        print(f"Objects in Ukraine latitude range: {len(ukraine_lat)} ({len(ukraine_lat)/len(df)*100:.1f}%)")
        print(f"Objects in Ukraine longitude range: {len(ukraine_lon)} ({len(ukraine_lon)/len(df)*100:.1f}%)")
        print(f"Objects in both ranges: {len(ukraine_both)} ({len(ukraine_both)/len(df)*100:.1f}%)")
        
        if len(ukraine_both) < success_count * 0.8:
            print("\n⚠️  Warning: Some coordinates may be outside Ukraine")
            print("   This could include occupied territories or objects moved abroad")
    
    # Save
    print(f"\n💾 Saving dataset with coordinates...")
    df.to_csv(output_file, index=False)
    print(f"✓ Saved to: {output_file}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total objects: {len(df)}")
    print(f"Objects with URLs: {url_count}")
    print(f"Coordinates extracted: {success_count}")
    print(f"New columns added: 'latitude', 'longitude'")
    print("="*70 + "\n")
    
    print("✅ SUCCESS! Your CSV now has latitude and longitude columns.")
    print(f"📂 Ready for Kepler.gl: {output_file}\n")
    
    return df

# Execute
if __name__ == "__main__":
    # INPUT: Your CSV file with Google Maps links
    input_file = 'data_stolen/stolen_objects_ukraine_cleaned.csv'
    
    # OUTPUT: Same file with latitude/longitude columns added
    output_file = 'data_stolen/stolen_objects_ukraine_with_coords.csv'
    
    # Column containing Google Maps URLs (change if needed)
    url_column = 'google_maps_link'
    
    try:
        df_with_coords = extract_coordinates_from_csv(input_file, output_file, url_column)
        
        if df_with_coords is not None:
            print("🗺️  You can now load this CSV in Kepler.gl!")
            print("   The map will show the locations of stolen Ukrainian objects.\n")
        
    except FileNotFoundError:
        print(f"\n✗ ERROR: File not found '{input_file}'")
        print("   Make sure the file is in the same directory as this script!")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()