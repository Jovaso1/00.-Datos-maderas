import pandas as pd
import streamlit as st
import plotly.express as px

def cargar_datos(archivo):
    """
    Carga un archivo CSV o un enlace con los datos de madera.
    
    Args:
        archivo (str): Ruta del archivo CSV o URL de los datos.
    
    Returns:
        pd.DataFrame: DataFrame con los datos cargados y procesados.
    """
    df = pd.read_csv(archivo)
    df = df.interpolate(method='linear')  # Rellenar valores faltantes con interpolación lineal
    return df

def especies_mas_comunes(df):
    """
    Identifica las especies de madera más comunes y sus volúmenes asociados a nivel país y por departamento.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de madera.
    
    Returns:
        tuple: DataFrames con el resumen de especies más comunes a nivel país y por departamento.
    """
    especies_pais = df.groupby("ESPECIE")["VOLUMEN M3"].sum().reset_index()
    especies_pais = especies_pais.sort_values(by="VOLUMEN M3", ascending=False)
    
    especies_dpto = df.groupby(["DPTO", "ESPECIE"])["VOLUMEN M3"].sum().reset_index()
    especies_dpto = especies_dpto.sort_values(by=["DPTO", "VOLUMEN M3"], ascending=[True, False])
    
    return especies_pais, especies_dpto

def main():
    """
    Aplicación en Streamlit para visualizar las especies de madera más comunes y sus volúmenes.
    """
    st.title("Análisis de Especies de Madera y Volúmenes")
    archivo = st.file_uploader("Suba un archivo CSV con los datos de madera", type=["csv"])
    
    if archivo is not None:
        df = cargar_datos(archivo)
        especies_pais, especies_dpto = especies_mas_comunes(df)
        
        st.subheader("Especies más comunes a nivel país")
        st.dataframe(especies_pais)
        fig1 = px.bar(especies_pais.head(10), x='ESPECIE', y='VOLUMEN M3', title='Top 10 Especies con Mayor Volumen')
        st.plotly_chart(fig1)
        
        st.subheader("Especies más comunes por departamento")
        st.dataframe(especies_dpto)
        fig2 = px.bar(especies_dpto.head(10), x='DPTO', y='VOLUMEN M3', color='ESPECIE', title='Volumen por Departamento y Especie')
        st.plotly_chart(fig2)

if __name__ == "__main__":
    main()
