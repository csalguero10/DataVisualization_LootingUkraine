"""
HERMITAGE DATASET CLEANING SCRIPT
Comprehensive data cleaning for Ukrainian objects from the Hermitage collection

Tasks:
1. Remove unnecessary quotes from text columns
2. Clean object names (remove periods between words)
3. Translate Russian measurements to English
4. FIX INVERTED COORDINATES (longitude/latitude were swapped)
5. Split material_technique into material and technique columns
6. Normalize dating column with complex textual dates
7. Extract year for timeline visualization
8. Assign historical period categories based on dates
"""

import pandas as pd
import numpy as np
import re

# ============================================================================
# HISTORICAL PERIODS
# ============================================================================

HISTORICAL_PERIODS = [
    {'name': 'Paleolithic Period', 'start': -1400000, 'end': -10000,
     'label': 'Paleolithic Period'},
    {'name': 'Mesolithic / Epipaleolithic', 'start': -10000, 'end': -7000,
     'label': 'Mesolithic / Epipaleolithic'},
    {'name': 'Pre-Neolithic', 'start': -7000, 'end': -5050,
     'label': 'Pre-Neolithic'},
    {'name': 'Neolithic Period', 'start': -5050, 'end': -2950,
     'label': 'Neolithic Period'},
    {'name': 'Bronze Age', 'start': -4500, 'end': -1950,
     'label': 'Bronze Age'},
    {'name': 'Iron Age', 'start': -1950, 'end': -700,
     'label': 'Iron Age'},
    {'name': 'Scythian-Sarmatian Era', 'start': -700, 'end': -250,
     'label': 'Scythian-Sarmatian Era'},
    {'name': 'Greek and Roman Period', 'start': -250, 'end': 375,
     'label': 'Greek and Roman Period'},
    {'name': 'Migration Period', 'start': 370, 'end': 700,
     'label': 'Migration Period'},
    {'name': 'Early Medieval Period - Bulgar and Khazar Era', 'start': 600, 'end': 900,
     'label': 'Early Medieval Period – Bulgar and Khazar Era'},
    {'name': 'Kievan Rus\' Period', 'start': 839, 'end': 1240,
     'label': 'Kievan Rus\' Period'},
    {'name': 'Mongol Invasion and Domination', 'start': 1239, 'end': 1400,
     'label': 'Mongol Invasion and Domination'},
    {'name': 'Kingdom of Galicia-Volhynia/Ruthenia', 'start': 1197, 'end': 1340,
     'label': 'Kingdom of Galicia-Volhynia / Ruthenia'},
    {'name': 'Lithuanian and Polish Period', 'start': 1340, 'end': 1648,
     'label': 'Lithuanian and Polish Period'},
    {'name': 'Cossack Hetmanate Period', 'start': 1648, 'end': 1764,
     'label': 'Cossack Hetmanate Period'},
    {'name': 'Ukraine under the Russian Empire', 'start': 1764, 'end': 1917,
     'label': 'Ukraine under the Russian Empire'},
    {'name': 'Ukraine\'s First Independence', 'start': 1917, 'end': 1921,
     'label': 'Ukraine\'s First Independence'},
    {'name': 'Soviet Period', 'start': 1921, 'end': 1991,
     'label': 'Soviet Period'},
    {'name': 'Independence Period', 'start': 1991, 'end': 2030,
     'label': 'Independence Period'}
]

# ============================================================================
# ROMAN NUMERAL CONVERSION
# ============================================================================

ROMAN_TO_INT = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8,
    'IX': 9, 'X': 10, 'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
    'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
    'XXI': 21, 'XXII': 22, 'XXIII': 23, 'XXIV': 24, 'XXV': 25,
    'XXVI': 26, 'XXVII': 27, 'XXVIII': 28, 'XXIX': 29, 'XXX': 30,
    'XXXI': 31, 'XXXII': 32, 'XXXIII': 33, 'XXXIV': 34, 'XXXV': 35,
    'XXXVI': 36, 'XXXVII': 37, 'XXXVIII': 38, 'XXXIX': 39, 'XL': 40,
    'XLI': 41, 'XLII': 42, 'XLIII': 43, 'XLIV': 44, 'XLV': 45,
    'XLVI': 46, 'XLVII': 47, 'XLVIII': 48, 'XLIX': 49, 'L': 50,
    'LI': 51, 'LII': 52, 'LIII': 53, 'LIV': 54, 'LV': 55,
    'LVI': 56, 'LVII': 57, 'LVIII': 58, 'LIX': 59, 'LX': 60,
    'LXI': 61, 'LXII': 62, 'LXIII': 63, 'LXIV': 64, 'LXV': 65,
    'LXVI': 66, 'LXVII': 67, 'LXVIII': 68, 'LXIX': 69, 'LXX': 70,
    'LXXI': 71, 'LXXII': 72, 'LXXIII': 73, 'LXXIV': 74, 'LXXV': 75,
    'LXXVI': 76, 'LXXVII': 77, 'LXXVIII': 78, 'LXXIX': 79, 'LXXX': 80,
    'LXXXI': 81, 'LXXXII': 82, 'LXXXIII': 83, 'LXXXIV': 84, 'LXXXV': 85,
    'LXXXVI': 86, 'LXXXVII': 87, 'LXXXVIII': 88, 'LXXXIX': 89, 'XC': 90,
    'XCI': 91, 'XCII': 92, 'XCIII': 93, 'XCIV': 94, 'XCV': 95,
    'XCVI': 96, 'XCVII': 97, 'XCVIII': 98, 'XCIX': 99, 'C': 100,
    'CI': 101, 'CII': 102, 'CIII': 103, 'CIV': 104, 'CV': 105,
    'CVI': 106, 'CVII': 107, 'CVIII': 108, 'CIX': 109, 'CX': 110,
    'CXI': 111, 'CXII': 112, 'CXIII': 113, 'CXIV': 114, 'CXV': 115,
    'CXVI': 116, 'CXVII': 117, 'CXVIII': 118, 'CXIX': 119, 'CXX': 120
}

def roman_to_arabic(roman):
    """Convert Roman numeral to Arabic number"""
    roman = roman.strip().upper()
    return ROMAN_TO_INT.get(roman, None)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def remove_quotes_from_columns(df):
    """Remove unnecessary quotes from text columns"""
    text_columns = ['object_name', 'find_location', 'creation_place_school',
                    'dating', 'material_technique', 'size', 'category',
                    'department_sector', 'region_category']

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x.strip('"') if isinstance(x, str) else x)

    return df


def clean_object_name(name):
    """Remove unnecessary quotes and trailing commas/periods"""
    if pd.isna(name) or name == '':
        return name

    name = str(name).strip()

    # Remove outer quotes if they exist
    if name.startswith('"') and name.endswith('"'):
        name = name[1:-1]

    # Remove trailing comma or period
    name = name.rstrip('.,')

    # Replace period between words with space (e.g., "Coin.Panticapaeum" -> "Coin Panticapaeum")
    name = re.sub(r'\.(?=[A-Z])', ' ', name)  # Period before capital letter
    name = re.sub(r'\.(?=[a-z])', ' ', name)  # Period before lowercase letter

    return name.strip()


def translate_russian_measurements(size_str):
    """
    Translate Russian measurement terms to English and normalize format
    Examples:
    - "Высота: 1.3 см" -> "1.3 cm"
    - "Длина: 5,5 см" -> "5.5 cm"
    - "D-1.7 см" -> "D-1.7 cm"
    """
    if pd.isna(size_str) or size_str == '':
        return ''

    text = str(size_str).strip().strip('"')

    # If it's only Russian labels without values, return empty
    if re.match(r'^(ширина|длина|высота|диаметр|толщина|вес|объем)[:\s]*(ширина|длина|высота|диаметр|толщина|вес|объем)?[:\s]*$', text, re.IGNORECASE):
        return ''

    # Russian to English measurement translations
    translations = {
        'высота': 'Height',
        'длина': 'Length',
        'ширина': 'Width',
        'диаметр': 'Diameter',
        'глубина': 'Depth',
        'толщина': 'Thickness',
        'вес': 'Weight',
        'объем': 'Volume'
    }

    # Replace Russian terms (remove the word and colon, keep only measurement)
    for russian, english in translations.items():
        if russian in text.lower():
            text = re.sub(f'{russian}:\\s*', '', text, flags=re.IGNORECASE)

    # Replace Russian comma with period for decimals
    text = text.replace(',', '.')

    # Clean up extra spaces
    text = ' '.join(text.split())

    # If result is empty or only punctuation, return empty
    if not text or text.strip(':; ') == '':
        return ''

    return text


def split_material_technique(mat_tech):
    """
    Split material_technique into materials and techniques
    Materials: clay, iron, bronze, silver, gold, stone, etc.
    Techniques: chipping, blowing, gilding, niello, retouching, etc.
    """
    if pd.isna(mat_tech) or mat_tech == '':
        return '', ''

    text = str(mat_tech).lower()

    # Common materials
    materials = []
    material_keywords = [
        'clay', 'iron', 'bronze', 'silver', 'gold', 'copper', 'brass',
        'stone', 'limestone', 'sandstone', 'marble', 'granite',
        'bone', 'wood', 'leather', 'fabric', 'glass', 'paste',
        'carnelian', 'amber', 'lignite', 'agate', 'chalcedony',
        'gypsum', 'kashin', 'faience', 'fired clay', 'engobe',
        'pebbles', 'flint', 'obsidian', 'ceramic', 'terracotta',
        'ivory', 'horn', 'shell', 'coral', 'pearl', 'sink', 'sinks'
    ]

    # Common techniques
    techniques = []
    technique_keywords = [
        'chipping', 'blowing', 'gilding', 'niello', 'retouching',
        'glaze', 'glazing', 'stamp', 'stamping', 'watering',
        'painting', 'hand modeling', 'modeling', 'imprint',
        'engraving', 'carving', 'polishing', 'varnish',
        'thread', 'weaving', 'forging', 'casting', 'welding',
        'incision', 'relief', 'embossing', 'inlay', 'enameling'
    ]

    # Extract materials
    for material in material_keywords:
        if material in text:
            materials.append(material.title())

    # Extract techniques
    for technique in technique_keywords:
        if technique in text:
            techniques.append(technique.title())

    # Join with commas
    material_str = ', '.join(sorted(set(materials))) if materials else ''
    technique_str = ', '.join(sorted(set(techniques))) if techniques else ''

    # If nothing found, return original as material
    if not material_str and not technique_str:
        material_str = mat_tech.strip()

    return material_str, technique_str


def normalize_textual_dates(dating_str):
    """
    Convert complex textual date ranges to approximate years
    Examples:
    - "second half of the 1st-end of the 2nd centuries AD" -> "ca. 125 AD"
    - "first quarter of the 4th century AD" -> "ca. 312 AD"
    - "end of the 3rd – beginning of the 4th century AD" -> "ca. 300 AD"
    """
    if pd.isna(dating_str) or dating_str == '':
        return dating_str

    text = str(dating_str).strip().lower()
    original = dating_str

    # Detect if BC or AD
    is_bc = 'bc' in text
    is_ad = 'ad' in text or 'ce' in text

    # Pattern: "second half of the Xst-end of the Ynd centuries"
    match = re.search(
        r'second half.*?(\d+)(?:st|nd|rd|th).*?end.*?(\d+)(?:st|nd|rd|th)\s+centur', text)
    if match:
        cent1 = int(match.group(1))
        cent2 = int(match.group(2))
        year1 = (cent1 - 1) * 100 + 75 if not is_bc else -(cent1 * 100 - 75)
        year2 = cent2 * 100 if not is_bc else -(cent2 * 100 - 100)
        avg_year = (year1 + year2) // 2
        return f"ca. {abs(avg_year)} {'BC' if is_bc else 'AD'}"

    # Pattern: "first/second/third/fourth quarter of the Xth century"
    quarter_match = re.search(
        r'(first|second|third|fourth)\s+quarter.*?(\d+)(?:st|nd|rd|th)\s+centur', text)
    if quarter_match:
        quarter = quarter_match.group(1)
        century = int(quarter_match.group(2))

        quarter_years = {
            'first': 12,
            'second': 37,
            'third': 62,
            'fourth': 87
        }

        offset = quarter_years.get(quarter, 50)
        if is_bc:
            year = -(century * 100 - offset)
        else:
            year = (century - 1) * 100 + offset

        return f"ca. {abs(year)} {'BC' if is_bc else 'AD'}"

    # Pattern: "first/second half of the Xth century"
    half_match = re.search(
        r'(first|second)\s+half.*?(\d+)(?:st|nd|rd|th)\s+centur', text)
    if half_match:
        half = half_match.group(1)
        century = int(half_match.group(2))

        offset = 25 if half == 'first' else 75
        if is_bc:
            year = -(century * 100 - offset)
        else:
            year = (century - 1) * 100 + offset

        return f"ca. {abs(year)} {'BC' if is_bc else 'AD'}"

    # Pattern: "beginning/middle/end of the Xth century"
    part_match = re.search(
        r'(beginning|middle|end).*?(\d+)(?:st|nd|rd|th)\s+centur', text)
    if part_match:
        part = part_match.group(1)
        century = int(part_match.group(2))

        part_years = {
            'beginning': 10,
            'middle': 50,
            'end': 90
        }

        offset = part_years.get(part, 50)
        if is_bc:
            year = -(century * 100 - offset)
        else:
            year = (century - 1) * 100 + offset

        return f"ca. {abs(year)} {'BC' if is_bc else 'AD'}"

    # Pattern: "end of Xth – beginning of Yth century"
    transition_match = re.search(
        r'end.*?(\d+)(?:st|nd|rd|th).*?beginning.*?(\d+)(?:st|nd|rd|th)\s+centur', text)
    if transition_match:
        cent1 = int(transition_match.group(1))
        if is_bc:
            year = -(cent1 * 100 - 100)
        else:
            year = cent1 * 100

        return f"ca. {abs(year)} {'BC' if is_bc else 'AD'}"

    # If no pattern matched, return original
    return original


def normalize_dating(dating_str):
    """
    Normalize dating strings to standard format
    Examples:
    - "IV centuryBC" -> "IV century BC"
    - "VI - V centuries.BC" -> "VI-V centuries BC"
    - "XIV-early XV centuries" -> "XIV-XV centuries"
    """
    if pd.isna(dating_str) or dating_str == '':
        return ''

    dating = str(dating_str).strip()

    # Handle "Roman time"
    if 'roman time' in dating.lower():
        return 'Roman Period'

    # Remove "early" and "beginning" from century ranges
    dating = re.sub(r'-\s*early\s+', '-', dating, flags=re.IGNORECASE)
    dating = re.sub(r'-\s*beginning\s*', '-', dating, flags=re.IGNORECASE)
    dating = re.sub(r'early\s+', '', dating, flags=re.IGNORECASE)
    dating = re.sub(r'beginning\s+', '', dating, flags=re.IGNORECASE)

    # Remove weird text between roman numerals
    dating = re.sub(r'([IVX]+)-([a-z]{4,})([IVX]+)', r'\1-\3', dating)

    # Convert Arabic numerals to Roman in centuries
    century_conversions = {
        '1st': 'I', '2nd': 'II', '3rd': 'III', '4th': 'IV', '5th': 'V',
        '6th': 'VI', '7th': 'VII', '8th': 'VIII', '9th': 'IX', '10th': 'X',
        '11th': 'XI', '12th': 'XII', '13th': 'XIII', '14th': 'XIV', '15th': 'XV',
        '16th': 'XVI', '17th': 'XVII', '18th': 'XVIII', '19th': 'XIX', '20th': 'XX'
    }

    for arabic, roman in century_conversions.items():
        dating = re.sub(rf'\b{arabic}\s+century',
                        f'{roman} century', dating, flags=re.IGNORECASE)

    # Remove "ca." and "around" prefixes
    dating = re.sub(r'^ca\.\s*', '', dating, flags=re.IGNORECASE)
    dating = re.sub(r'^around\s*', '', dating, flags=re.IGNORECASE)

    # Normalize BC/BCE formatting
    dating = re.sub(r'BC[eE]?\.?', 'BC', dating)
    dating = re.sub(r'A\.?D\.?', 'AD', dating)

    # Add space before BC/AD if missing
    dating = re.sub(r'([IVXLC]+)-([IVXLC]+)\s*(BC|AD)',
                    r'\1-\2 \3', dating, flags=re.IGNORECASE)
    dating = re.sub(r'([IVXLC\d]+)(BC|AD)', r'\1 \2', dating)
    dating = re.sub(r'(century|centuries|millennium)(BC|AD)', r'\1 \2', dating)

    # Remove extra spaces around dashes
    dating = re.sub(r'\s*-\s*', '-', dating)

    # Remove trailing periods
    dating = dating.rstrip('.')

    return dating.strip()


def extract_year_from_dating(dating_normalized):
    """Extract a single year value for timeline from normalized dating"""
    if pd.isna(dating_normalized) or dating_normalized == '':
        return np.nan

    text = str(dating_normalized).strip()

    # Handle "Roman Period"
    if 'roman period' in text.lower():
        return 62  # Midpoint of Greek and Roman Period

    # Remove "ca." prefix
    text = re.sub(r'^ca\.\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^around\s*', '', text, flags=re.IGNORECASE)

    # Detect if BC or AD
    is_bc = 'BC' in text.upper()

    # Handle millennium BC (e.g., "I millennium BC" = -500)
    single_millennium = re.search(r'\b([IVX]+)\s+millennium\s+BC', text, re.IGNORECASE)
    if single_millennium:
        mill = roman_to_arabic(single_millennium.group(1))
        if mill:
            return -(mill * 1000 - 500)

    # Pattern: Year ranges with BC/AD (e.g., "66-47 BC", "131-153 AD")
    simple_range = re.search(r'(\d+)\s*-\s*(\d+)s?\s*(BC|AD)', text, re.IGNORECASE)
    if simple_range:
        year1 = int(simple_range.group(1))
        year2 = int(simple_range.group(2))
        is_bc_range = 'BC' in simple_range.group(3).upper()
        return -((year1 + year2) // 2) if is_bc_range else (year1 + year2) // 2

    # Pattern: Single year with BC/AD
    single_year = re.search(r'(\d+)\s*(BC|AD)', text, re.IGNORECASE)
    if single_year:
        year = int(single_year.group(1))
        is_bc_single = 'BC' in single_year.group(2).upper()
        return -year if is_bc_single else year

    # Handle specific year (e.g., "1850", "1920")
    year_match = re.search(r'\b(\d{4})\b', text)
    if year_match:
        return int(year_match.group(1))

    # Handle year range (e.g., "1920-1930")
    range_match = re.search(r'(\d{4})-(\d{4})', text)
    if range_match:
        year1 = int(range_match.group(1))
        year2 = int(range_match.group(2))
        return (year1 + year2) // 2

    # Handle Roman numeral centuries
    single_century = re.search(r'\b([IVX]+)\s+century', text, re.IGNORECASE)
    if single_century:
        century_num = roman_to_arabic(single_century.group(1))
        if century_num:
            if is_bc:
                return -(century_num * 100 - 50)
            else:
                return (century - 1) * 100 + 50

    # Century range (e.g., "VI-V centuries BC")
    century_range = re.search(r'\b([IVX]+)-([IVX]+)\s+centuries', text, re.IGNORECASE)
    if century_range:
        cent1 = roman_to_arabic(century_range.group(1))
        cent2 = roman_to_arabic(century_range.group(2))
        if cent1 and cent2:
            if is_bc:
                year1 = -(cent1 * 100 - 50)
                year2 = -(cent2 * 100 - 50)
            else:
                year1 = (cent1 - 1) * 100 + 50
                year2 = (cent2 - 1) * 100 + 50
            return (year1 + year2) // 2

    return np.nan


def assign_period_category(year):
    """Assign historical period based on year"""
    if pd.isna(year):
        return 'Unknown Period'

    year = float(year)

    # Find matching periods
    matching_periods = [
        p for p in HISTORICAL_PERIODS if p['start'] <= year <= p['end']]

    if not matching_periods:
        if year < -10000:
            return 'Pre-Paleolithic'
        elif year > 2030:
            return 'Contemporary Period'
        else:
            return 'Unknown Period'

    # Handle overlapping periods
    if len(matching_periods) == 1:
        return matching_periods[0]['label']

    period_names = [p['name'] for p in matching_periods]

    # Priority rules
    if 'Neolithic Period' in period_names and 'Bronze Age' in period_names:
        return next(p['label'] for p in matching_periods if p['name'] == 'Neolithic Period')

    if 'Mongol Invasion and Domination' in period_names and 'Kingdom of Galicia-Volhynia/Ruthenia' in period_names:
        if year < 1300:
            return next(p['label'] for p in matching_periods if p['name'] == 'Mongol Invasion and Domination')
        else:
            return next(p['label'] for p in matching_periods if p['name'] == 'Kingdom of Galicia-Volhynia/Ruthenia')

    if 'Kievan Rus\' Period' in period_names and 'Kingdom of Galicia-Volhynia/Ruthenia' in period_names:
        return next(p['label'] for p in matching_periods if p['name'] == 'Kievan Rus\' Period')

    return matching_periods[0]['label']


# ============================================================================
# MAIN CLEANING FUNCTION
# ============================================================================

def clean_hermitage_dataset(input_file, output_file):
    """Main cleaning function"""

    print("\n" + "="*70)
    print("HERMITAGE DATASET CLEANING")
    print("="*70 + "\n")

    # Read CSV
    print(f"📖 Reading file: {input_file}")
    df = pd.read_csv(input_file)
    print(f"✓ {len(df)} objects loaded")
    print(f"✓ Columns: {', '.join(df.columns[:8])}...\n")

    # ========================================
    # STEP 1: Remove quotes from text columns
    # ========================================
    print("🔧 STEP 1: Removing quotes from text columns...")
    df = remove_quotes_from_columns(df)
    print("  ✓ Quotes removed from all text fields\n")

    # ========================================
    # STEP 2: Clean object_name
    # ========================================
    print("🔧 STEP 2: Cleaning object names...")
    df['object_name'] = df['object_name'].apply(clean_object_name)
    print("  ✓ Removed quotes and trailing punctuation")
    print("  ✓ Replaced periods between words with spaces\n")

    # ========================================
    # STEP 3: Translate Russian measurements
    # ========================================
    print("🔧 STEP 3: Translating Russian measurements...")
    df['size'] = df['size'].apply(translate_russian_measurements)

    size_examples = df[df['size'].notna() & (df['size'] != '')]['size'].head(5)
    print("  Examples of normalized measurements:")
    for size in size_examples:
        print(f"    • {size}")
    print()

    # ========================================
    # STEP 4: FIX INVERTED COORDINATES
    # ========================================
    print("🔧 STEP 4: Fixing inverted coordinates...")
    print("  CRITICAL: Longitude and latitude were swapped in the original data!")
    
    # Swap the columns
    df['longitude_temp'] = df['longitude']
    df['longitude'] = df['latitude']
    df['latitude'] = df['longitude_temp']
    df = df.drop('longitude_temp', axis=1)
    
    has_coords = df['latitude'].notna().sum()
    print(f"  ✓ Corrected coordinates for {has_coords} objects")
    if has_coords > 0:
        print(f"  ✓ Latitude range: {df['latitude'].min():.4f} to {df['latitude'].max():.4f}")
        print(f"  ✓ Longitude range: {df['longitude'].min():.4f} to {df['longitude'].max():.4f}")
    print()

    # ========================================
    # STEP 5: Remove inventory_number column
    # ========================================
    print("🔧 STEP 5: Removing inventory_number column...")
    if 'inventory_number' in df.columns:
        df = df.drop('inventory_number', axis=1)
        print("  ✓ inventory_number column removed\n")

    # ========================================
    # STEP 6: Split material_technique
    # ========================================
    print("🔧 STEP 6: Splitting material_technique...")
    df[['material', 'technique']] = df['material_technique'].apply(
        lambda x: pd.Series(split_material_technique(x))
    )

    has_material = df['material'].notna() & (df['material'] != '')
    has_technique = df['technique'].notna() & (df['technique'] != '')
    print(f"  ✓ {has_material.sum()} objects with identified materials")
    print(f"  ✓ {has_technique.sum()} objects with identified techniques\n")

    # Show examples
    print("  Examples of material/technique separation:")
    examples = df[has_material & has_technique][['material_technique', 'material', 'technique']].head(5)
    for idx, row in examples.iterrows():
        print(f"    Original: {row['material_technique']}")
        print(f"    → Material: {row['material']}")
        print(f"    → Technique: {row['technique']}")
        print()

    # ========================================
    # STEP 7: Normalize textual dates
    # ========================================
    print("🔧 STEP 7: Converting complex textual dates...")
    df['dating'] = df['dating'].apply(normalize_textual_dates)

    print("  Examples of textual date conversion:")
    textual_examples = df[df['dating'].str.contains('ca.', na=False)]['dating'].unique()[:5]
    for example in textual_examples:
        print(f"    • {example}")
    print()

    # ========================================
    # STEP 8: Normalize dating format
    # ========================================
    print("🔧 STEP 8: Normalizing dating format...")
    df['date_normalized'] = df['dating'].apply(normalize_dating)

    print("  Examples of normalization:")
    examples = df[df['dating'].notna()][['dating', 'date_normalized']].drop_duplicates('dating').head(5)
    for idx, row in examples.iterrows():
        print(f"    • {row['dating'][:60]}")
        print(f"      → {row['date_normalized']}")
    print()

    # ========================================
    # STEP 9: Extract year for timeline
    # ========================================
    print("🔧 STEP 9: Extracting years for timeline...")
    df['year_for_timeline'] = df['date_normalized'].apply(extract_year_from_dating)

    has_year = df['year_for_timeline'].notna()
    print(f"  ✓ {has_year.sum()} objects with extracted years")
    if has_year.sum() > 0:
        print(f"  ✓ Timeline range: {df['year_for_timeline'].min():.0f} to {df['year_for_timeline'].max():.0f}\n")

    # ========================================
    # STEP 10: Assign historical periods
    # ========================================
    print("🔧 STEP 10: Assigning historical period categories...")
    df['period_category'] = df['year_for_timeline'].apply(assign_period_category)

    has_period = df['period_category'] != 'Unknown Period'
    print(f"  ✓ {has_period.sum()} objects assigned to historical periods")
    
    print("\n  Period distribution (top 5):")
    top_periods = df['period_category'].value_counts().head(5)
    for period, count in top_periods.items():
        print(f"    • {period}: {count} objects")
    print()

    # ========================================
    # SAVE
    # ========================================
    print("💾 Saving cleaned dataset...")
    df.to_csv(output_file, index=False)
    print(f"✓ Saved to: {output_file}")

    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "="*70)
    print("CLEANING SUMMARY")
    print("="*70)
    print(f"\n📊 Final dataset:")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")

    print(f"\n📋 New columns created:")
    print(f"  • material - Extracted materials")
    print(f"  • technique - Extracted techniques")
    print(f"  • date_normalized - Standardized dates")
    print(f"  • year_for_timeline - Numeric year values")
    print(f"  • period_category - Historical periods")

    print(f"\n✅ All transformations completed!")
    print("="*70 + "\n")

    return df


# Execute
if __name__ == "__main__":
    input_file = '1_hermitage_ukraine_english.csv'
    output_file = '2_hermitage_ukraine_cleaned.csv'

    try:
        df_cleaned = clean_hermitage_dataset(input_file, output_file)

        # Preview
        print("\n📝 Preview (first 5 rows, selected columns):")
        print("="*70)
        cols = ['object_name', 'material', 'technique', 'date_normalized', 'period_category']
        available_cols = [col for col in cols if col in df_cleaned.columns]
        print(df_cleaned[available_cols].head(5).to_string(index=False))
        print("\n")

    except FileNotFoundError:
        print(f"\n✗ ERROR: File not found '{input_file}'")
        print("   Place the file in the same directory as this script!")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()