import streamlit as st
from calc import calc_malla_tierra
from graph import generate_malla_tierra
import matplotlib.pyplot as plt

def run_app():
    # Parámetros de entrada para la malla de tierra
    I = st.number_input("Intensidad de corriente (A)", min_value=0.1, step=0.1)
    R_des = st.number_input("Resistencia deseada por barra (Ω/km)", min_value=0.1, step=0.1)
    sigma = st.number_input("Conductividad del suelo (S/m)", min_value=1e-3, step=1e-3)
    rho = st.number_input("Densidad del material de la barra (kg/m³)", min_value=1000, step=1000)
    I_falla = st.number_input("Intensidad de corriente de falla (A)", min_value=0.1, step=0.1)
    L = st.number_input("Longitud total de la malla (m)", min_value=100, step=1)

    # Calcular los parámetros de la malla de tierra
    I, R_des, sigma, rho, I_falla, L, A, n_barras = calc_malla_tierra(I, R_des, sigma, rho, I_falla, L)

    # Botón para calcular y graficar
    if st.button("Calcular y graficar"):
        try:
            fig, ax = generate_malla_tierra(I, R_des, sigma, rho, I_falla, L, A, n_barras)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error al generar el gráfico: {e}")

if __name__ == "__main__":
    run_app()
