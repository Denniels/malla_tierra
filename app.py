import streamlit as st
from calc import calc_malla_tierra
from graph import generate_malla_tierra
import matplotlib.pyplot as plt

def run_app():
    # Parámetros de entrada para la malla de tierra    st.title("Calculadora de Malla de Puesta a Tierra")
    
    # Valores por defecto optimizados para una malla de 2x2m
    col1, col2 = st.columns(2)
    
    with col1:
        I = st.number_input("Intensidad de corriente (A)", 
                            min_value=0.1, value=100.0, step=0.1)
        R_des = st.number_input("Resistencia deseada por barra (Ω/km)", 
                                min_value=0.1, value=0.5, step=0.1)
        sigma = st.number_input("Conductividad del suelo (S/m)", 
                                min_value=1e-3, value=0.01, step=1e-3)
        rho = st.number_input("Densidad del material de la barra (kg/m³)", 
                                min_value=1000, value=7800, step=100)
    
    with col2:
        I_falla = st.number_input("Intensidad de corriente de falla (A)", 
                                    min_value=0.1, value=1000.0, step=0.1)
        L = st.number_input("Longitud total de la malla (m)", 
                            min_value=0.5, value=2.0, step=0.5,
                            help="Para una malla cuadrada, este es el largo de un lado")
        
        spacing_options = {
            "0.25 m (Densidad Alta)": 0.25,
            "0.5 m (Densidad Media)": 0.5,
            "1.0 m (Densidad Baja)": 1.0
        }
        spacing = st.selectbox(
            "Espaciamiento entre nodos",
            options=list(spacing_options.keys()),
            index=1,
            help="Distancia entre nodos consecutivos de la malla"
        )
        spacing_value = spacing_options[spacing]    # Calcular los parámetros de la malla de tierra
    I, R_des, sigma, rho, I_falla, L, A, n_barras = calc_malla_tierra(
        I=I,
        R_des=R_des,
        sigma=sigma,
        rho=rho,
        I_falla=I_falla,
        L=L,
        spacing=spacing_value
    )

    # Mostrar información de la malla
    st.info(f"""
        Dimensiones de la malla:
        - Lado: {L}m x {L}m
        - Área total: {L*L}m²
        - Nodos por lado: {n_barras}
        - Total de nodos: {n_barras * n_barras}
        - Espaciamiento real: {L/(n_barras-1):.2f}m
    """)

    # Botón para calcular y graficar
    if st.button("Calcular y graficar"):
        try:
            fig, ax = generate_malla_tierra(I, R_des, sigma, rho, I_falla, L, A, n_barras)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error al generar el gráfico: {e}")

if __name__ == "__main__":
    run_app()
