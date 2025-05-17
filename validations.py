# -*- coding: utf-8 -*-
"""
Módulo de validaciones según IEEE-80 para el diseño de mallas de tierra.
"""

class ValidationError(Exception):
    """Excepción personalizada para errores de validación."""
    pass

def validate_soil_resistivity(rho):
    """
    Valida la resistividad del suelo según IEEE-80.
    
    Args:
        rho (float): Resistividad del suelo en Ω⋅m
        
    Returns:
        bool: True si es válido
        
    Raises:
        ValidationError: Si el valor está fuera de rango
    """
    if not (1 <= rho <= 10000):
        raise ValidationError(
            "La resistividad del suelo debe estar entre 1 y 10000 Ω⋅m. "
            f"Valor actual: {rho} Ω⋅m"
        )
    return True

def validate_fault_current(I_falla):
    """
    Valida la corriente de falla según IEEE-80.
    
    Args:
        I_falla (float): Corriente de falla en amperios
        
    Returns:
        bool: True si es válido
        
    Raises:
        ValidationError: Si el valor está fuera de rango
    """
    if not (0 < I_falla <= 50000):
        raise ValidationError(
            "La corriente de falla debe estar entre 0 y 50000 A. "
            f"Valor actual: {I_falla} A"
        )
    return True

def validate_clearing_time(t_c):
    """
    Valida el tiempo de despeje de falla según IEEE-80.
    
    Args:
        t_c (float): Tiempo de despeje en segundos
        
    Returns:
        bool: True si es válido
        
    Raises:
        ValidationError: Si el valor está fuera de rango
    """
    if not (0.03 <= t_c <= 3.0):
        raise ValidationError(
            "El tiempo de despeje debe estar entre 0.03 y 3.0 segundos. "
            f"Valor actual: {t_c} s"
        )
    return True

def validate_grid_depth(h):
    """
    Valida la profundidad de enterramiento según IEEE-80.
    
    Args:
        h (float): Profundidad en metros
        
    Returns:
        bool: True si es válido
        
    Raises:
        ValidationError: Si el valor está fuera de rango
    """
    if not (0.5 <= h <= 2.5):
        raise ValidationError(
            "La profundidad de enterramiento debe estar entre 0.5 y 2.5 metros. "
            f"Valor actual: {h} m"
        )
    return True

def validate_conductor_diameter(d):
    """
    Valida el diámetro del conductor según IEEE-80.
    
    Args:
        d (float): Diámetro en milímetros
        
    Returns:
        bool: True si es válido
        
    Raises:
        ValidationError: Si el valor está fuera de rango
    """
    if not (8 <= d <= 50):
        raise ValidationError(
            "El diámetro del conductor debe estar entre 8 y 50 mm. "
            f"Valor actual: {d} mm"
        )
    return True

def validate_grid_spacing(spacing):
    """
    Valida el espaciamiento de la malla según IEEE-80.
    
    Args:
        spacing (float): Espaciamiento en metros
        
    Returns:
        bool: True si es válido
        
    Raises:
        ValidationError: Si el valor está fuera de rango
    """
    if not (0.25 <= spacing <= 3.0):
        raise ValidationError(
            "El espaciamiento de la malla debe estar entre 0.25 y 3.0 metros. "
            f"Valor actual: {spacing} m"
        )
    return True
