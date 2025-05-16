def calc_malla_tierra(I, R_des, sigma, rho, I_falla, L):
    # Cálculo de la sección necesaria para las barras de la malla de tierra
    A = (I_falla * rho) / (R_des * sigma)

    # Cálculo del número de barras necesarias para cubrir la longitud total
    n_barras = int(L // 100 + 0.5)

    return I, R_des, sigma, rho, I_falla, L, A, n_barras