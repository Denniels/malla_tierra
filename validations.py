# -*- coding: utf-8 -*-
"""
Módulo de validaciones según IEEE-80 para el diseño de mallas de tierra.
"""

from typing import Tuple

class ValidationError(Exception):
    """Error de validación en los cálculos de la malla"""
    pass

def validate_soil_resistivity(rho: float):
    """Valida la resistividad del suelo según IEEE-80"""
    if rho <= 0:
        raise ValidationError("La resistividad del suelo debe ser positiva")
    if rho > 10000:  # 10000 Ω⋅m es un valor muy alto
        raise ValidationError(f"Resistividad del suelo ({rho:.2f} Ω⋅m) es inusualmente alta")

def validate_fault_current(I_falla: float):
    """Valida la corriente de falla según IEEE-80"""
    if I_falla <= 0:
        raise ValidationError("La corriente de falla debe ser positiva")
    if I_falla > 50000:  # 50kA es un valor muy alto
        raise ValidationError(f"Corriente de falla ({I_falla:.2f} A) es inusualmente alta")

def validate_grid_spacing(spacing: float):
    """Valida el espaciamiento de la malla según IEEE-80"""
    if spacing <= 0:
        raise ValidationError("El espaciamiento debe ser positivo")
    if spacing < 0.5:
        raise ValidationError(f"Espaciamiento ({spacing:.2f} m) menor al mínimo recomendado (0.5 m)")
    if spacing > 10:
        raise ValidationError(f"Espaciamiento ({spacing:.2f} m) mayor al máximo recomendado (10 m)")

def validate_potentials(E_paso: float, E_paso_max: float, E_contacto: float, E_contacto_max: float) -> None:
    """
    Valida que los potenciales de paso y contacto estén dentro de límites seguros.
    
    Args:
        E_paso: Potencial de paso calculado (V)
        E_paso_max: Potencial de paso máximo permitido (V)
        E_contacto: Potencial de contacto calculado (V)
        E_contacto_max: Potencial de contacto máximo permitido (V)
    
    Raises:
        ValidationError: Si algún potencial excede los límites seguros
    """
    margen_seguridad = 0.9  # 90% del límite máximo como margen de seguridad
    
    if E_paso > E_paso_max * margen_seguridad:
        raise ValidationError(
            f"Potencial de paso ({E_paso:.2f}V) excede el {margen_seguridad*100}% del límite máximo permitido ({E_paso_max:.2f}V)"
        )
    
    if E_contacto > E_contacto_max * margen_seguridad:
        raise ValidationError(
            f"Potencial de contacto ({E_contacto:.2f}V) excede el {margen_seguridad*100}% del límite máximo permitido ({E_contacto_max:.2f}V)"
        )
        
def validate_all_parameters(
    I_falla: float,
    rho: float,
    L: float,
    spacing: float,
    h: float,
    potentials: Tuple[float, float, float, float]
) -> None:
    """
    Realiza todas las validaciones necesarias para los parámetros de la malla.
    
    Args:
        I_falla: Corriente de falla (A)
        rho: Resistividad del suelo (Ω⋅m)
        L: Longitud del lado de la malla (m)
        spacing: Espaciamiento entre conductores (m)
        h: Profundidad de enterramiento (m)
        potentials: Tupla (E_paso, E_paso_max, E_contacto, E_contacto_max)
    """
    validate_fault_current(I_falla)
    validate_soil_resistivity(rho)
    
    if L <= 0:
        raise ValidationError("La longitud de la malla debe ser positiva")
    if L > 100:
        raise ValidationError(f"Longitud de la malla ({L:.2f} m) es inusualmente grande")
        
    validate_grid_spacing(spacing)
    
    if h < 0.3:
        raise ValidationError("La profundidad debe ser al menos 0.3 m según IEEE-80")
    if h > 3.0:
        raise ValidationError(f"Profundidad ({h:.2f} m) excede el máximo recomendado (3.0 m)")
        
    validate_potentials(*potentials)
