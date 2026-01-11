import pandas as pd

# Cargar el archivo CSV
df = pd.read_csv('hermitage_ukraine_jittered.csv')

# Convertir acquisition_year a datetime (formato date)
df['acquisition_year'] = pd.to_datetime(df['acquisition_year'], format='%Y', errors='coerce')

# Crear nueva columna con formato timestamp ISO 8601 para Kepler.gl
df['year_acquisition_timestamp'] = df['acquisition_year'].dt.strftime('%Y-%m-%dT%H:%M:%S')

# Verificar el cambio
print("Tipo de dato de acquisition_year:")
print(df['acquisition_year'].dtype)
print("\nPrimeras filas de ambas columnas:")
print(df[['acquisition_year', 'year_acquisition_timestamp']].head(10))
print("\nEjemplo de formato timestamp:")
print(df['year_acquisition_timestamp'].iloc[0])

# Verificar valores nulos
print(f"\nValores nulos en acquisition_year: {df['acquisition_year'].isna().sum()}")
print(f"Valores nulos en year_acquisition_timestamp: {df['year_acquisition_timestamp'].isna().sum()}")

# Guardar el archivo modificado
df.to_csv('hermitage_ukraine_timestamp.csv', index=False)
print("\n✓ Archivo guardado como 'hermitage_ukraine_timestamp.csv'")
print("✓ acquisition_year: datetime64 (date)")
print("✓ year_acquisition_timestamp: timestamp ISO 8601 para Kepler.gl")

# Cargar el archivo CSV
df = pd.read_csv('hermitage_ukraine_jittered.csv')

# Convertir acquisition_year a datetime (1 de enero de cada año)
df['acquisition_year'] = pd.to_datetime(df['acquisition_year'], format='%Y', errors='coerce')

# Verificar el cambio
print("Tipo de dato después de la conversión:")
print(df['acquisition_year'].dtype)
print("\nPrimeras filas:")
print(df[['acquisition_year']].head())
print("\nInformación del DataFrame:")
print(df.info())

# Guardar el archivo modificado
df.to_csv('hermitage_ukraine_timestamp.csv', index=False)
print("\nArchivo guardado como 'data_hermitage/hermitage_ukraine_timestamp.csv'")