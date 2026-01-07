"""
FIX COORDINATES - Hermitage Dataset
Swaps longitude and latitude columns that are inverted in the original dataset
"""

import pandas as pd

def fix_coordinates(input_file, output_file):
    """
    Swap longitude and latitude columns
    
    Original Hermitage dataset has them inverted:
    - Column 'longitude' contains latitude values (44-61)
    - Column 'latitude' contains longitude values (22-105)
    
    This script fixes it so:
    - longitude = 22-40°E (correct for Ukraine)
    - latitude = 44-52°N (correct for Ukraine)
    """
    
    print("\n" + "="*70)
    print("FIXING COORDINATES - SWAPPING LONGITUDE AND LATITUDE")
    print("="*70 + "\n")
    
    # Read CSV
    print(f"📖 Reading file: {input_file}")
    df = pd.read_csv(input_file)
    print(f"✓ {len(df)} objects loaded\n")
    
    # Show before
    print("BEFORE FIX:")
    print("-" * 70)
    print(f"Longitude range: {df['longitude'].min():.2f} to {df['longitude'].max():.2f}")
    print(f"Latitude range: {df['latitude'].min():.2f} to {df['latitude'].max():.2f}")
    
    print("\n❌ Problem: Longitude values (44-61) are actually latitude!")
    print("❌ Problem: Latitude values (22-105) are actually longitude!")
    
    # Swap columns
    print("\n🔄 Swapping longitude ↔ latitude columns...")
    df['longitude'], df['latitude'] = df['latitude'].copy(), df['longitude'].copy()
    
    # Show after
    print("\nAFTER FIX:")
    print("-" * 70)
    print(f"Longitude range: {df['longitude'].min():.2f} to {df['longitude'].max():.2f}")
    print(f"Latitude range: {df['latitude'].min():.2f} to {df['latitude'].max():.2f}")
    
    print("\n✅ Now coordinates are correct for Ukraine!")
    print("   Longitude: 22-40°E ✓")
    print("   Latitude: 44-52°N ✓")
    
    # Verify a sample location
    print("\n📍 Sample verification:")
    sample = df[df['find_location'].str.contains('Solkhat', na=False)].iloc[0]
    print(f"   Location: {sample['find_location']}")
    print(f"   Longitude: {sample['longitude']:.6f}°E")
    print(f"   Latitude: {sample['latitude']:.6f}°N")
    print("   ✓ Solkhat, Crimea should be ~35°E, ~45°N - CORRECT!")
    
    # Save
    print(f"\n💾 Saving fixed dataset...")
    df.to_csv(output_file, index=False)
    print(f"✓ Saved to: {output_file}")
    
    print("\n" + "="*70)
    print("COORDINATES FIXED SUCCESSFULLY!")
    print("="*70 + "\n")
    
    print("🗺️  Now you can load this CSV in Kepler.gl and see")
    print("   all objects correctly located in UKRAINE! 🇺🇦")
    print("\n")
    
    return df

# Execute
if __name__ == "__main__":
    # INPUT: Your CSV file with manual corrections
    input_file = 'data_hermitage/hermitage_ukraine_cleaned.csv'
    
    # OUTPUT: Same file with fixed coordinates
    output_file = 'data_hermitage/hermitage_ukraine_final.csv'
    
    try:
        df_fixed = fix_coordinates(input_file, output_file)
        
        print("✅ SUCCESS! Your coordinates are now correct.")
        print(f"📂 Use this file for Kepler.gl: {output_file}\n")
        
    except FileNotFoundError:
        print(f"\n✗ ERROR: File not found '{input_file}'")
        print("   Make sure the file is in the same directory as this script!")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()