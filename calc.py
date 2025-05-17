def calc_malla_tierra(I, R_des, sigma, rho, I_falla, L, spacing=0.5):
    """
    Calcula los parámetros de la malla de tierra.
    
    Args:
        I: Intensidad de corriente (A)
        R_des: Resistencia deseada por barra (Ω/km)
        sigma: Conductividad del suelo (S/m)
        rho: Densidad del material de la barra (kg/m³)
        I_falla: Intensidad de corriente de falla (A)
        L: Longitud total de la malla (m)
        spacing: Espaciamiento deseado entre nodos (m)
    """
    # Cálculo de la sección necesaria para las barras de la malla de tierra
    A = (I_falla * rho) / (R_des * sigma)
    
    # Cálculo del número de barras necesarias
    n_barras = max(round(L / spacing) + 1, 3)  # Mínimo 3 barras para formar una malla útil
    
    # Ajustar n_barras para tener una distribución uniforme
    if n_barras % 2 == 0:  # Si es par, agregar uno más para tener simetría
        n_barras += 1
    
    return I, R_des, sigma, rho, I_falla, L, A, n_barras