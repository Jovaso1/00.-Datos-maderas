import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
from sklearn.cluster import KMeans
from scipy.stats import entropy

# Función para cargar los datos
def cargar_datos(url):
    """Carga los datos desde un enlace y realiza la interpolación de valores faltantes.
    
    Args:
        url (str): Enlace al archivo CSV.
    
    Returns:
        pd.DataFrame: DataFrame con los datos cargados e interpolados.
    """
    df = pd.read_csv(url)
    df = df.interpolate(method='linear')
    return df

# Función para calcular el índice de Shannon
def indice_shannon(df, grupo):
    """Calcula el índice de diversidad de Shannon para un grupo dado.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos.
        grupo (str): Columna por la cual agrupar (ejemplo: 'DPTO').
    
    Returns:
        pd.DataFrame: DataFrame con el índice de Shannon por grupo.
    """
    def calcular_shannon(grupo_df):
        proporciones = grupo_df['VOLUMEN M3'] / grupo_df['VOLUMEN M3'].sum()
        return entropy(proporciones)
    
    return df.groupby(grupo).apply(calcular_shannon).reset_index(name='Indice de Shannon')

# Streamlit UI
st.title("Análisis de Movilización de Madera en Colombia")

url = st.text_input("Ingrese el enlace del archivo CSV:")

if url:
    df = cargar_datos(url)
    
    # Gráfico de barras - 10 especies con mayor volumen movilizado
    top_especies = df.groupby("ESPECIE")['VOLUMEN M3'].sum().nlargest(10).reset_index()
    fig_especies = px.bar(top_especies, x='ESPECIE', y='VOLUMEN M3', title='Top 10 Especies con Mayor Volumen')
    st.plotly_chart(fig_especies)
    
    # Mapa de calor por departamento
    dpto_volumen = df.groupby("DPTO")['VOLUMEN M3'].sum().reset_index()
    colombia = gpd.read_file("colombia.geojson", driver="GeoJSON")
    dpto_volumen = colombia.merge(dpto_volumen, left_on='NOMBRE_DPT', right_on='DPTO')
    fig_mapa_calor = px.choropleth(dpto_volumen, geojson=dpto_volumen.geometry, locations=dpto_volumen.index, 
                                   color='VOLUMEN M3', title='Distribución de Volumen por Departamento')
    st.plotly_chart(fig_mapa_calor)
    
    # Índice de Shannon por departamento
    shannon_df = indice_shannon(df, 'DPTO')
    st.dataframe(shannon_df)

    # Clustering por departamentos
    df_cluster = df.groupby("DPTO")["VOLUMEN M3"].sum().reset_index()
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(df_cluster[["VOLUMEN M3"]])
    df_cluster["Cluster"] = kmeans.labels_
    st.dataframe(df_cluster)

else:
    st.warning("Ingrese un enlace para cargar los datos.")
