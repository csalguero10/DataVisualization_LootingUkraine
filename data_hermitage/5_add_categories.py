import pandas as pd

# Cargar el dataset con materiales capitalizados
df = pd.read_csv('data_hermitage/1_hermitage_ukraine_timestamp.csv')

print("=== ASIGNANDO CATEGORÍAS A MATERIALES ===\n")

# Diccionario de mapeo: material -> categoría
material_to_category = {
    # Metal Products
    'Brass': 'Metal Products',
    'Bronze': 'Metal Products',
    'Copper': 'Metal Products',
    'Gold': 'Metal Products',
    'Iron': 'Metal Products',
    'Lead': 'Metal Products',
    'Silver': 'Metal Products',
    'Metal': 'Metal Products',
    'Slag': 'Metal Products',
    
    # Stone Products
    'Agate': 'Stone Products',
    'Alabaster': 'Stone Products',
    'Carnelian': 'Stone Products',
    'Chalcedony': 'Stone Products',
    'Chalk': 'Stone Products',
    'Cornelian': 'Stone Products',
    'Crystal': 'Stone Products',
    'Flint': 'Stone Products',
    'Gypsum': 'Stone Products',
    'Limestone': 'Stone Products',
    'Marble': 'Stone Products',
    'Mica': 'Stone Products',
    'Pebbles': 'Stone Products',
    'Pomegranate': 'Stone Products',  # Garnet
    'Quartz': 'Stone Products',
    'Sandstone': 'Stone Products',
    'Slate': 'Stone Products',
    'Slate Gray': 'Stone Products',
    'Slate Green': 'Stone Products',
    'Slate Pink': 'Stone Products',
    'Steatite': 'Stone Products',
    'Stone': 'Stone Products',
    
    # Ceramic Products
    'Ceramic': 'Ceramic Products',
    'Clay': 'Ceramic Products',
    'Earthenware': 'Ceramic Products',
    'Engobe': 'Ceramic Products',
    'Faience': 'Ceramic Products',
    'Fired Clay': 'Ceramic Products',
    'Kashin': 'Ceramic Products',
    'Pink Marl': 'Ceramic Products',
    'Terracotta': 'Ceramic Products',
    
    # Glass Products
    'Glass': 'Glass Products',
    'Blue Pasta': 'Glass Products',
    'Pasta': 'Glass Products',
    'Paste': 'Glass Products',
    'White Pasta': 'Glass Products',
    
    # Bone Products
    'Boar Tusk': 'Bone Products',
    'Bone': 'Bone Products',
    'Fang': 'Bone Products',
    'Horn': 'Bone Products',
    'Tooth': 'Bone Products',
    
    # Wood Products
    'Charcoal': 'Wood Products',
    'Coal': 'Wood Products',
    'Lignite': 'Wood Products',
    'Tree': 'Wood Products',
    'Tree Bark': 'Wood Products',
    'Wood': 'Wood Products',
    
    # Leather Products
    'Leather': 'Leather Products',
    
    # Textile & Fiber Products
    'Fabric': 'Textile & Fiber Products',
    'Wool': 'Textile & Fiber Products',
    'Organic': 'Textile & Fiber Products',
    
    # Shell & Marine Products
    'Coral': 'Shell & Marine Products',
    'Pearl': 'Shell & Marine Products',
    'Shell': 'Shell & Marine Products',
    'Sink': 'Shell & Marine Products',
    'Sinks': 'Shell & Marine Products',
    
    # Resin & Amber Products
    'Amber': 'Resin & Amber Products',
    
    # Minerals
    'Realgar': 'Minerals',
    'Sulfur': 'Minerals',
    
    # Construction Materials
    'Plaster': 'Construction Materials',
    'Earth': 'Construction Materials',
    
    # Pigments (no se asignarán categorías, quedarán como None o se pueden excluir)
    'Black Paint': None,
    'Black Paints': None,
    'Blue': None,
    'Blue And Black Paints;Coloring': None,
    'Blue Paint': None,
    'Blush': None,
    'Dye': None,
    'Ocher': None,
    'Paint': None,
    'Paints': None,
    'Pink': None,
    'Pink And Blue Paints': None,
    'Pink Paint': None,
    'Red Paint': None,
    'Traces Of Brown And Pink Paints': None,
    'Traces Of Pink Paint': None,
    'Traces Of Red': None,
    'Yellowish': None,
}

def assign_category(material_string):
    """
    Asigna categoría basada en los materiales.
    Si hay múltiples materiales, toma el primero que no sea pigmento.
    Si todos son pigmentos o ninguno tiene categoría, retorna None.
    """
    if pd.isna(material_string):
        return None
    
    # Separar materiales por coma
    materials = [m.strip() for m in str(material_string).split(',')]
    
    # Buscar el primer material que tenga una categoría válida (no None)
    for material in materials:
        if material in material_to_category:
            category = material_to_category[material]
            if category is not None:  # Ignorar pigmentos
                return category
    
    # Si no se encontró ninguna categoría válida
    return None

# Aplicar la función para crear la columna category
print("Asignando categorías...")
df['category'] = df['material'].apply(assign_category)

# Estadísticas
total_records = len(df)
records_with_category = df['category'].notna().sum()
records_without_category = df['category'].isna().sum()

print(f"\n{'='*60}")
print("ESTADÍSTICAS")
print(f"{'='*60}")
print(f"Total de registros: {total_records}")
print(f"Registros con categoría asignada: {records_with_category}")
print(f"Registros sin categoría (pigmentos/vacíos): {records_without_category}")

# Distribución por categoría
print(f"\n{'='*60}")
print("DISTRIBUCIÓN POR CATEGORÍA")
print(f"{'='*60}")
category_counts = df['category'].value_counts().sort_values(ascending=False)
for category, count in category_counts.items():
    percentage = (count / total_records) * 100
    print(f"{category:.<35} {count:>6} ({percentage:>5.2f}%)")

# Guardar el dataset final
output_file = 'data_hermitage/1_hermitage_ukraine_with_categories.csv'
df.to_csv(output_file, index=False)

print(f"\n{'='*60}")
print(f"✓ Dataset final guardado en:")
print(f"  {output_file}")
print(f"{'='*60}")

# Mostrar algunos ejemplos
print(f"\n{'='*60}")
print("EJEMPLOS DE REGISTROS CON CATEGORÍAS")
print(f"{'='*60}\n")
sample = df[df['category'].notna()][['object_name', 'material', 'category']].head(10)
for idx, row in sample.iterrows():
    print(f"Objeto: {row['object_name']}")
    print(f"Material: {row['material']}")
    print(f"Categoría: {row['category']}")
    print("-" * 60)