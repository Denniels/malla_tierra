# -*- coding: utf-8 -*-
import numpy as np
from validations import (
    validate_soil_resistivity,
    validate_fault_current,
    validate_grid_spacing,
    ValidationError
)

def calc_malla_tierra(I, R_des, sigma, rho, I_falla, L, spacing=0.5, h=0.5):
    """
    Calcula los parámetros de la malla de tierra según IEEE-80.
    
    Args:
        I (float): Intensidad de corriente (A)
        R_des (float): Resistencia deseada (Ω/km)
        sigma (float): Conductividad del suelo (S/m)
        rho (float): Resistividad del suelo (Ω⋅m)
        I_falla (float): Intensidad de falla (A)
        L (float): Longitud total de la malla (m)
        spacing (float): Espaciamiento entre nodos (m)
        h (float): Profundidad de enterramiento (m)
    
    Returns:
        tuple: (I, R_des, sigma, rho, I_falla, L, A, n_barras)
    
    Raises:
        ValidationError: Si algún parámetro no cumple con IEEE-80
    """
    # Validaciones según IEEE-80
    validate_soil_resistivity(1/sigma)  # Convertir conductividad a resistividad
    validate_fault_current(I_falla)
    validate_grid_spacing(spacing)
    
    # Cálculos
    A = (I_falla * rho) / (R_des * sigma)
    n_barras = max(round(L / spacing) + 1, 3)
    
    # Asegurar número impar de barras para centrar la malla
    if n_barras % 2 == 0:
        n_barras += 1
        
    return I, R_des, sigma, rho, I_falla, L, A, n_barras