import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

def cargar_datos(archivo: str):
    """
    Carga los datos desde un archivo CSV o una URL.

    Args:
        archivo (str): Ruta al archivo o URL de los datos.

    Returns:
        pd.DataFrame: DataFrame con los datos cargados.
    """
    return pd.read_csv(archivo)

def rellenar_valores_faltantes(df: pd.DataFrame):
    """
    Rellena los valores faltantes en el DataFrame utilizando interpolación lineal.

    Args:
        df (pd.DataFrame): DataFrame con los datos que contienen valores faltantes.

    Returns:
        pd.DataFrame: DataFrame con los valores faltantes interpolados.
    """
    return df.interpolate(method='linear', axis=0)

def especies_volumen(df: pd.DataFrame):
    """
    Identifica las especies de madera más comunes y los volúmenes asociados a nivel país y por departamento.

    Args:
        df (pd.DataFrame): DataFrame con los datos de la movilización de madera.

    Returns:
        tuple: dos DataFrames:
            - Volumen total por especie a nivel nacional.
            - Volumen total por especie y departamento.
    """
    # Agrupar por especie y calcular el volumen total a nivel nacional
    volumen_nacional = df.groupby('ESPECIE')['VOLUMEN M3'].sum().reset_index()
    volumen_nacional = volumen_nacional.sort_values(by='VOLUMEN M3', ascending=False)
    
    # Agrupar por especie y departamento, calculando el volumen total por departamento
    volumen_departamento = df.groupby(['ESPECIE', 'DPTO'])['VOLUMEN M3'].sum().reset_index()
    volumen_departamento = volumen_departamento.sort_values(by='VOLUMEN M3', ascending=False)
    
    return volumen_nacional, volumen_departamento

def grafico_barras_especies(volumen_nacional: pd.DataFrame):
    """
    Crea un gráfico de barras que muestra las diez especies de madera con mayor volumen movilizado.

    Args:
        volumen_nacional (pd.DataFrame): DataFrame con el volumen total por especie a nivel nacional.
    """
    # Seleccionar las 10 especies con mayor volumen movilizado
    top_10_especies = volumen_nacional.head(10)
    
    # Crear gráfico de barras
    plt.figure(figsize=(10,6))
    plt.barh(top_10_especies['ESPECIE'], top_10_especies['VOLUMEN M3'], color='teal')
    plt.xlabel('Volumen movilizado (m3)')
    plt.ylabel('Especies de madera')
    plt.title('Top 10 Especies de Madera con Mayor Volumen Movilizado')
    plt.gca().invert_yaxis()  # Para que la especie con mayor volumen esté en la parte superior
    plt.show()

def mapa_calor_volumen(df: pd.DataFrame, archivo_geojson: str):
    """
    Crea un mapa de calor mostrando la distribución de los volúmenes de madera por departamento.

    Args:
        df (pd.DataFrame): DataFrame con los volúmenes de madera por departamento.
        archivo_geojson (str): Ruta al archivo geojson con los límites geográficos de los departamentos de Colombia.
    """
    # Cargar el archivo geojson de los departamentos de Colombia
    gdf = gpd.read_file(archivo_geojson)
    
    # Agrupar los datos por departamento y sumar los volúmenes de madera
    volumen_departamento = df.groupby('DPTO')['VOLUMEN M3'].sum().reset_index()
    
    # Unir los datos de volumen con los datos geoespaciales
    gdf = gdf.merge(volumen_departamento, how='left', left_on='NOMBRE_DPT', right_on='DPTO')

    # Crear el mapa de calor
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    gdf.plot(column='VOLUMEN M3', ax=ax, legend=True,
             legend_kwds={'label': "Volumen de Madera por Departamento (m³)",
                          'orientation': "horizontal"},
             cmap='YlOrRd')
    ax.set_title('Distribución de Volúmenes de Madera por Departamento')
    plt.show()

# URL del archivo CSV en GitHub (en formato crudo)
archivo_url = 'https://raw.githubusercontent.com/Jovaso1/VARGASja_Recursos/refs/heads/main/Base_de_datos_relacionada_con_madera_movilizada_proveniente_de_Plantaciones_Forestales_Comerciales_20250217.csv'   # Cambia esta URL a la correcta

# Cargar los datos desde la URL
df = cargar_datos(archivo_url)

# Rellenar valores faltantes
df = rellenar_valores_faltantes(df)

# Obtener el volumen por especie a nivel nacional y por departamento
volumen_nacional, volumen_departamento = especies_volumen(df)

# Mostrar los resultados
print("Volumen total por especie a nivel nacional:")
print(volumen_nacional.head())  # Muestra las primeras 5 especies más comunes

print("\nVolumen total por especie y departamento:")
print(volumen_departamento.head())  # Muestra las primeras filas por departamento

# Crear gráfico de barras para las 10 especies con mayor volumen movilizado
grafico_barras_especies(volumen_nacional)

# Crear mapa de calor para la distribución de volúmenes por departamento
archivo_geojson = 'https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/3aadedf47badbdac823b00dbe259f6bc6d9e1899/colombia.geo.json'  # Cambia esta ruta al archivo geojson
mapa_calor_volumen(df, archivo_geojson)
