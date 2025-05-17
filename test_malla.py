# -*- coding: utf-8 -*-
import numpy as np
from calc import calc_malla_tierra
from graph import generate_malla_tierra
import matplotlib.pyplot as plt
import os

def test_diferentes_espaciamientos():
    """
    Prueba la malla con diferentes espaciamientos y muestra los resultados
    """
    print("Iniciando pruebas de malla de tierra...")
    
    # Parametros fijos
    I = 100  # Intensidad de corriente (A)
    R_des = 0.5  # Resistencia deseada (Ohm/km)
    sigma = 0.01  # Conductividad del suelo (S/m)
    rho = 7800  # Densidad del material (kg/m3)
    I_falla = 1000  # Intensidad de falla (A)
    L = 2  # Longitud total (m)
    
    print("\nParametros fijos:")
    print(f"- Intensidad de corriente: {I}A")
    print(f"- Resistencia deseada: {R_des} Ohm/km")
    print(f"- Conductividad del suelo: {sigma}S/m")
    print(f"- Densidad del material: {rho}kg/m3")
    print(f"- Intensidad de falla: {I_falla}A")
    print(f"- Longitud de la malla: {L}m")
    
    # Probar diferentes espaciamientos
    espaciamientos = [0.25, 0.5, 1.0]
    
    # Crear directorio para resultados si no existe
    os.makedirs("test_results", exist_ok=True)
    
    for spacing in espaciamientos:
        print(f"\nPrueba con espaciamiento de {spacing}m:")
        print("-" * 50)
        
        try:
            # Calcular parametros
            I, R_des, sigma, rho, I_falla, L, A, n_barras = calc_malla_tierra(
                I, R_des, sigma, rho, I_falla, L, spacing
            )
            
            print(f"Dimensiones de la malla:")
            print(f"- Lado: {L}m x {L}m")
            print(f"- Area total: {L*L}m2")
            print(f"- Nodos por lado: {n_barras}")
            print(f"- Total de nodos: {n_barras * n_barras}")
            spacing_real = L / (n_barras - 1) if n_barras > 1 else L
            print(f"- Espaciamiento calculado: {spacing_real:.3f}m")
            
            # Generar y guardar el grafico
            print("Generando grafico...")
            fig, ax = generate_malla_tierra(I, R_des, sigma, rho, I_falla, L, A, n_barras)
            
            # Guardar el grafico
            nombre_archivo = f"test_results/malla_spacing_{spacing}m.png"
            plt.savefig(nombre_archivo)
            plt.close()
            print(f"Grafico guardado como: {nombre_archivo}")
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            continue

if __name__ == "__main__":
    test_diferentes_espaciamientos()
