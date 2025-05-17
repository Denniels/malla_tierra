# -*- coding: utf-8 -*-
"""
Módulo de cálculos avanzados para malla de tierra según IEEE-80
"""
import numpy as np
from math import pi, log, sqrt, exp

def calcular_potencial_paso(I_falla, rho, L, n_barras, h, t_c=0.5, rho_s=3000):
    """
    Calcula el potencial de paso según IEEE-80.
    
    Args:
        I_falla (float): Corriente de falla (A)
        rho (float): Resistividad del suelo (Ω⋅m)
        L (float): Longitud del lado de la malla (m)
        n_barras (int): Número de barras por lado
        h (float): Profundidad de enterramiento (m)
        t_c (float): Tiempo de despeje de falla (s)
        rho_s (float): Resistividad de la capa superficial (Ω⋅m)
    
    Returns:
        tuple: (E_paso, E_paso_max_permitido)
    """
    # Factor de reducción de la capa superficial
    C_s = 1 - (0.09 * (1 - rho/rho_s))/(2 * h + 0.09)
    
    # Factores de la malla
    K_s = 1/(pi * (2*h + 1))
    
    # Voltaje de paso
    E_paso = (rho * I_falla * K_s) / L
    
    # Voltaje de paso máximo permitido
    E_paso_max = (1000 + 6 * C_s * rho_s) * (0.116/sqrt(t_c))
    
    return E_paso, E_paso_max

def calcular_potencial_contacto(I_falla, rho, L, n_barras, h, t_c=0.5, rho_s=3000):
    """
    Calcula el potencial de contacto según IEEE-80.
    
    Args:
        I_falla (float): Corriente de falla (A)
        rho (float): Resistividad del suelo (Ω⋅m)
        L (float): Longitud del lado de la malla (m)
        n_barras (int): Número de barras por lado
        h (float): Profundidad de enterramiento (m)
        t_c (float): Tiempo de despeje de falla (s)
        rho_s (float): Resistividad de la capa superficial (Ω⋅m)
    
    Returns:
        tuple: (E_contacto, E_contacto_max_permitido)
    """    # Factor de reducción de la capa superficial
    C_s = 1 - (0.09 * (1 - rho/rho_s))/(2 * h + 0.09)
    
    # Factores geométricos
    D = L/(n_barras - 1)  # Espaciamiento entre conductores
    d = 0.01  # Diámetro del conductor (m)
    K_h = sqrt(1 + h/1)
    K_ii = 1
    
    # Factores de la malla
    K_m = 1/(2 * pi) * (log(D**2/(16*h*d) + 1) + K_ii/K_h * log(8/(pi*(2*n_barras-1))))
    K_i = 0.644 + 0.148 * n_barras
    
    E_contacto = (rho * I_falla * K_m * K_i) / L
    
    # Voltaje de contacto máximo permitido
    E_contacto_max = (1000 + 1.5 * C_s * rho_s) * (0.116/sqrt(t_c))
    
    return E_contacto, E_contacto_max

def calcular_resistencia_malla(rho, L, n_barras, h, d=0.01):
    """
    Calcula la resistencia real de la malla según IEEE-80.
    
    Args:
        rho (float): Resistividad del suelo (Ω⋅m)
        L (float): Longitud del lado de la malla (m)
        n_barras (int): Número de barras por lado
        h (float): Profundidad de enterramiento (m)
        d (float): Diámetro del conductor (m)
    
    Returns:
        float: Resistencia de la malla (Ω)
    """
    # Longitud total de conductores
    L_total = 2 * n_barras * L
    
    # Factor de profundidad
    K_1 = 1.43
    K_2 = 5.5
    
    # Resistencia de la malla
    R = rho/(4*L) * (1 + 1/(1 + h * sqrt(20/L)))
    
    return R

def factor_temperatura_suelo(T, T_ref=25):
    """
    Calcula el factor de corrección por temperatura del suelo.
    
    Args:
        T (float): Temperatura del suelo (°C)
        T_ref (float): Temperatura de referencia (°C)
    
    Returns:
        float: Factor de corrección
    """
    alpha = 0.00397  # Coeficiente de temperatura
    return 1 + alpha * (T - T_ref)
