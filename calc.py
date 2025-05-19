# -*- coding: utf-8 -*-
import numpy as np
from validations import (
    validate_soil_resistivity,
    validate_fault_current,
    validate_grid_spacing,
    ValidationError
)
from malla import MallaTierra, Conductor

def calc_malla_tierra(I, R_des, sigma, rho, I_falla, L, spacing=0.5, h=0.5, conductor=None):
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
        conductor (Optional[Conductor]): Conductor a utilizar
    
    Returns:
        tuple: (I, R_des, sigma, rho, I_falla, L, A, n_barras)
    
    Raises:
        ValidationError: Si algún parámetro no cumple con IEEE-80
    """
    # Validaciones según IEEE-80
    validate_soil_resistivity(1/sigma)  # Convertir conductividad a resistividad
    validate_fault_current(I_falla)
    validate_grid_spacing(spacing)
    
    if L <= 0:
        raise ValidationError("La longitud de la malla debe ser positiva")
    
    if h < 0.3 or h > 3.0:
        raise ValidationError("La profundidad de enterramiento debe estar entre 0.3 y 3.0 metros según IEEE-80")
    
    # Cálculos básicos
    # Creamos la malla primero para tener las dimensiones reales
    malla = MallaTierra(
        ancho=L,
        largo=L,
        espaciamiento=spacing,
        conductor=conductor,
        profundidad=h
    )
    
    # El área efectiva es el área real de la malla más un margen de seguridad
    # según IEEE-80 para considerar el área de disipación
    A_real = malla.ancho * malla.largo
    margen = 1.0  # 1 metro de margen según IEEE-80
    A_efectiva = (malla.ancho + 2*margen) * (malla.largo + 2*margen)
    
    # Calcular longitud total de conductores (horizontales y verticales)
    L_total = malla.get_longitud_total_conductores()
    
    # La resistencia equivalente se calcula considerando la longitud total de conductores
    # y el área efectiva según IEEE-80 sección 14.3
    R_equiv = rho * (1/L_total + 1/np.sqrt(20*A_efectiva) * (1 + 1/(1 + h * np.sqrt(20/A_efectiva))))
    
    # Validar que la resistencia equivalente cumpla con el criterio de diseño
    if R_equiv > R_des:
        raise ValidationError(f"La resistencia equivalente ({R_equiv:.2f} Ω) supera la resistencia deseada ({R_des} Ω)")
    
    return I, R_des, sigma, rho, I_falla, L, A_efectiva, malla.n_x