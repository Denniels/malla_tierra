import streamlit as st
from calc import calc_malla_tierra
from graph import generate_malla_tierra
from validations import ValidationError
import matplotlib.pyplot as plt

def run_app():
    st.title("Calculadora de Malla de Puesta a Tierra")
    st.write("Diseño según norma IEEE-80")
    
    # Columnas para parámetros
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parámetros Eléctricos")
        I = st.number_input(
            "Intensidad de corriente (A)", 
            min_value=0.1, 
            value=100.0, 
            step=0.1,
            help="Corriente nominal del sistema"
        )
        
        R_des = st.number_input(
            "Resistencia deseada por barra (Ω/km)", 
            min_value=0.1, 
            value=0.5, 
            step=0.1,
            help="Resistencia máxima deseada para cada barra de la malla"
        )
        
        sigma = st.number_input(
            "Conductividad del suelo (S/m)", 
            min_value=1e-4, 
            value=0.01, 
            step=1e-3,
            help="Conductividad del terreno. Valores típicos: 0.001-0.1 S/m"
        )
        
        if 1/sigma > 1000:
            st.warning("⚠️ Conductividad muy baja. Considere tratamiento del suelo.")
        
        I_falla = st.number_input(
            "Intensidad de corriente de falla (A)", 
            min_value=0.1, 
            value=1000.0, 
            step=0.1,
            help="Corriente máxima de falla esperada"
        )
        
        if I_falla > 10000:
            st.warning("⚠️ Corriente de falla muy alta. Verifique protecciones.")
    
    with col2:
        st.subheader("Parámetros Físicos")
        L = st.number_input(
            "Longitud total de la malla (m)", 
            min_value=0.5, 
            value=2.0, 
            step=0.5,
            help="Para una malla cuadrada, este es el largo de un lado"
        )
        
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
        spacing_value = spacing_options[spacing]
        
        h = st.number_input(
            "Profundidad de enterramiento (m)",
            min_value=0.5,
            max_value=2.5,
            value=0.5,
            step=0.1,
            help="Profundidad a la que se enterrará la malla (IEEE-80: 0.5m - 2.5m)"
        )

    try:
        # Calcular los parámetros de la malla de tierra
        I, R_des, sigma, rho, I_falla, L, A, n_barras = calc_malla_tierra(
            I=I,
            R_des=R_des,
            sigma=sigma,
            rho=rho,
            I_falla=I_falla,
            L=L,
            spacing=spacing_value,
            h=h
        )

        # Mostrar información de la malla
        st.info(f"""
            ### Dimensiones de la malla:
            - Lado: {L}m x {L}m
            - Área total: {L*L}m²
            - Nodos por lado: {n_barras}
            - Total de nodos: {n_barras * n_barras}
            - Espaciamiento real: {L/(n_barras-1):.3f}m
            - Profundidad: {h}m
        """)

        # Botón para calcular y graficar
        if st.button("Calcular y graficar"):
            fig, ax = generate_malla_tierra(I, R_des, sigma, rho, I_falla, L, A, n_barras)
            st.pyplot(fig)
            
    except ValidationError as e:
        st.error(f"Error de validación: {str(e)}")
    except Exception as e:
        st.error(f"Error en el cálculo: {str(e)}")

if __name__ == "__main__":
    run_app()
