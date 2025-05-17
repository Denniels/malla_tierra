import streamlit as st
from calc import calc_malla_tierra
from calc_avanzado import (
    calcular_potencial_paso,
    calcular_potencial_contacto,
    calcular_resistencia_malla,
    factor_temperatura_suelo
)
from graph import generate_malla_tierra
from validations import ValidationError
import matplotlib.pyplot as plt

def run_app():
    st.title("Calculadora de Malla de Puesta a Tierra")
    st.write("Diseño según norma IEEE-80")
    
    # Crear pestañas para organizar la interfaz
    tab1, tab2 = st.tabs(["Parámetros Básicos", "Parámetros Avanzados"])
    
    with tab1:
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
            
            # Calcular resistividad del suelo
            resistividad = 1/sigma
            if resistividad > 1000:
                st.warning("⚠️ Resistividad muy alta (>1000 Ω⋅m). Considere tratamiento del suelo.")
            
            # Densidad del material (antes estaba mal etiquetado)
            densidad = st.number_input(
                "Densidad del material conductor (kg/m³)", 
                min_value=1000, 
                value=7800, 
                step=100,
                help="Densidad del material conductor. Cobre: ~8960, Acero: ~7800"
            )
            
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

    with tab2:
        st.subheader("Parámetros Avanzados")
        col3, col4 = st.columns(2)
        
        with col3:
            t_c = st.number_input(
                "Tiempo de despeje de falla (s)",
                min_value=0.03,
                max_value=3.0,
                value=0.5,
                step=0.01,
                help="Tiempo que tarda la protección en despejar la falla"
            )
            
            rho_s = st.number_input(
                "Resistividad capa superficial (Ω⋅m)",
                min_value=100.0,
                max_value=10000.0,
                value=3000.0,
                step=100.0,
                help="Resistividad de la capa superficial (grava, asfalto, etc.)"
            )
            
        with col4:
            T_suelo = st.number_input(
                "Temperatura del suelo (°C)",
                min_value=-20.0,
                max_value=50.0,
                value=25.0,
                step=1.0,
                help="Temperatura del suelo para factor de corrección"
            )
            
            d_conductor = st.number_input(
                "Diámetro del conductor (mm)",
                min_value=8.0,
                max_value=50.0,
                value=10.0,
                step=0.5,
                help="Diámetro del conductor de la malla"
            )

    try:
        # Calcular los parámetros básicos de la malla
        I, R_des, sigma, resistividad, I_falla, L, A, n_barras = calc_malla_tierra(
            I=I,
            R_des=R_des,
            sigma=sigma,
            rho=resistividad,
            I_falla=I_falla,
            L=L,
            spacing=spacing_value,
            h=h
        )
        
        # Calcular parámetros avanzados
        f_temp = factor_temperatura_suelo(T_suelo)
        resistividad_corregida = resistividad * f_temp
        
        E_paso, E_paso_max = calcular_potencial_paso(
            I_falla, resistividad_corregida, L, n_barras, h, t_c, rho_s
        )
        
        E_contacto, E_contacto_max = calcular_potencial_contacto(
            I_falla, resistividad_corregida, L, n_barras, h, t_c, rho_s
        )
        
        R_malla = calcular_resistencia_malla(
            resistividad_corregida, L, n_barras, h, d_conductor/1000
        )

        # Mostrar información básica de la malla
        st.info(f"""
            ### Dimensiones de la malla:
            - Lado: {L}m x {L}m
            - Área total: {L*L}m²
            - Nodos por lado: {n_barras}
            - Total de nodos: {n_barras * n_barras}
            - Espaciamiento real: {L/(n_barras-1):.3f}m
            - Profundidad: {h}m
            
            ### Parámetros eléctricos:
            - Resistividad del suelo: {resistividad:.2f} Ω⋅m
            - Resistividad corregida por temperatura: {resistividad_corregida:.2f} Ω⋅m
            - Conductividad del suelo: {sigma:.3f} S/m
            - Resistencia de la malla: {R_malla:.3f} Ω
        """)
        
        # Mostrar resultados de seguridad
        col5, col6 = st.columns(2)
        with col5:
            st.metric(
                "Potencial de Paso",
                f"{E_paso:.1f} V",
                f"{E_paso_max - E_paso:.1f} V bajo límite",
                delta_color="normal" if E_paso < E_paso_max else "off"
            )
        with col6:
            st.metric(
                "Potencial de Contacto",
                f"{E_contacto:.1f} V",
                f"{E_contacto_max - E_contacto:.1f} V bajo límite",
                delta_color="normal" if E_contacto < E_contacto_max else "off"
            )
        
        if E_paso > E_paso_max or E_contacto > E_contacto_max:
            st.warning("⚠️ Los potenciales de paso y/o contacto superan los límites seguros. Considere:")
            st.write("- Aumentar el área de la malla")
            st.write("- Reducir el espaciamiento entre conductores")
            st.write("- Aumentar la profundidad de enterramiento")
            st.write("- Mejorar la resistividad de la capa superficial")

        # Botón para calcular y graficar
        if st.button("Calcular y graficar"):
            fig, ax = generate_malla_tierra(I, R_des, sigma, resistividad, I_falla, L, A, n_barras)
            st.pyplot(fig)
            
    except ValidationError as e:
        st.error(f"Error de validación: {str(e)}")
    except Exception as e:
        st.error(f"Error en el cálculo: {str(e)}")

if __name__ == "__main__":
    run_app()
