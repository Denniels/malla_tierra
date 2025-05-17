# -*- coding: utf-8 -*-
"""
Módulo para visualización avanzada y reportes de la malla de tierra
"""
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from typing import Tuple, Optional
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import datetime
import os

def generar_mapa_calor(
    I_falla: float,
    rho: float,
    malla,
    potenciales: np.ndarray,
    titulo: str = "Distribución de Potenciales"
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Genera un mapa de calor de la distribución de potenciales.
    
    Args:
        I_falla: Corriente de falla (A)
        rho: Resistividad del suelo (Ω⋅m)
        malla: Objeto MallaTierra
        potenciales: Array 2D con los valores de potencial
        titulo: Título del gráfico
    
    Returns:
        tuple: (figura, ejes) de matplotlib
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Crear malla para el mapa de calor
    x = np.linspace(0, malla.ancho, 100)
    y = np.linspace(0, malla.largo, 100)
    X, Y = np.meshgrid(x, y)
    
    # Generar mapa de calor
    im = ax.pcolormesh(X, Y, potenciales, shading='auto', cmap='hot')
    plt.colorbar(im, ax=ax, label='Potencial (V)')
    
    # Dibujar conductores
    x_nodos, y_nodos = malla.obtener_nodos()
    ax.plot(x_nodos, y_nodos, 'k-', linewidth=1)
    ax.plot(x_nodos.T, y_nodos.T, 'k-', linewidth=1)
    
    # Dibujar varillas si existen
    for x, y, _ in malla.obtener_varillas():
        ax.plot(x, y, 'ko', markersize=8)
    
    ax.set_title(titulo)
    ax.set_xlabel('Distancia (m)')
    ax.set_ylabel('Distancia (m)')
    ax.grid(True)
    
    return fig, ax

def generar_perfil_suelo(
    malla,
    rho: float,
    h: float,
    rho_s: Optional[float] = None
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Genera una vista de perfil del suelo y la malla.
    
    Args:
        malla: Objeto MallaTierra
        rho: Resistividad del suelo (Ω⋅m)
        h: Profundidad de enterramiento (m)
        rho_s: Resistividad de la capa superficial (Ω⋅m), si existe
    
    Returns:
        tuple: (figura, ejes) de matplotlib
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Dibujar capas del suelo
    if rho_s:
        ax.axhspan(0, -0.1, color='gray', alpha=0.3, label=f'Capa superficial (ρ={rho_s} Ω⋅m)')
    ax.axhspan(-0.1, -3, color='brown', alpha=0.2, label=f'Suelo (ρ={rho} Ω⋅m)')
    
    # Dibujar conductores enterrados
    ax.axhline(-h, color='k', linestyle='--', alpha=0.5)
    x_nodos = np.linspace(0, malla.ancho, malla.n_x)
    ax.plot(x_nodos, [-h]*len(x_nodos), 'k-', linewidth=2, label='Conductores')
    
    # Dibujar varillas
    for x, _, l in malla.obtener_varillas():
        ax.plot([x, x], [-h, -h-l], 'r-', linewidth=2)
    
    ax.set_ylim(-3, 0.5)
    ax.set_xlabel('Distancia (m)')
    ax.set_ylabel('Profundidad (m)')
    ax.set_title('Perfil del Suelo y Malla de Tierra')
    ax.grid(True)
    ax.legend()
    
    return fig, ax

def generar_reporte_pdf(
    malla,
    parametros: dict,
    resultados: dict,
    nombre_archivo: str = "reporte_malla_tierra.pdf"
) -> str:
    """
    Genera un reporte PDF completo del diseño de la malla.
    
    Args:
        malla: Objeto MallaTierra
        parametros: Diccionario con los parámetros de entrada
        resultados: Diccionario con los resultados calculados
        nombre_archivo: Nombre del archivo PDF a generar
    
    Returns:
        str: Ruta al archivo PDF generado
    """
    # Crear directorio para reportes si no existe
    os.makedirs("reportes", exist_ok=True)
    ruta_pdf = os.path.join("reportes", nombre_archivo)
    
    # Crear PDF
    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    width, height = letter
    
    # Título y fecha
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Reporte de Malla de Puesta a Tierra")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Parámetros de entrada
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 100, "Parámetros de Entrada:")
    c.setFont("Helvetica", 12)
    y = height - 120
    for key, value in parametros.items():
        y -= 20
        c.drawString(70, y, f"{key}: {value}")
    
    # Resultados
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Resultados:")
    c.setFont("Helvetica", 12)
    for key, value in resultados.items():
        y -= 20
        c.drawString(70, y, f"{key}: {value}")
    
    # Agregar gráficos
    for fig, titulo in zip([generar_mapa_calor, generar_perfil_suelo], 
                         ["Distribución de Potenciales", "Perfil del Suelo"]):
        imgdata = io.BytesIO()
        plt.savefig(imgdata, format='png')
        imgdata.seek(0)
        c.drawImage(imgdata, 50, y-300, width=500, height=300)
        y -= 320
    
    c.save()
    return ruta_pdf

def calcular_potenciales_superficie(malla, I_falla: float, rho: float) -> np.ndarray:
    """
    Calcula la matriz de potenciales en la superficie.
    
    Args:
        malla: Objeto MallaTierra
        I_falla: Corriente de falla (A)
        rho: Resistividad del suelo (Ω⋅m)
    
    Returns:
        np.ndarray: Matriz 2D con los potenciales
    """
    x = np.linspace(0, malla.ancho, 100)
    y = np.linspace(0, malla.largo, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    
    # Calcular potencial en cada punto
    for i in range(len(x)):
        for j in range(len(y)):
            Z[j,i] = calcular_potencial_punto(X[j,i], Y[j,i], malla, I_falla, rho)
    
    return Z

def calcular_potencial_punto(x: float, y: float, malla, I_falla: float, rho: float) -> float:
    """
    Calcula el potencial en un punto específico.
    
    Args:
        x, y: Coordenadas del punto
        malla: Objeto MallaTierra
        I_falla: Corriente de falla (A)
        rho: Resistividad del suelo (Ω⋅m)
    
    Returns:
        float: Potencial en el punto
    """
    V = 0
    x_nodos, y_nodos = malla.obtener_nodos()
    
    # Contribución de conductores horizontales y verticales
    for i in range(malla.n_x):
        for j in range(malla.n_y):
            r = np.sqrt((x - x_nodos[j,i])**2 + (y - y_nodos[j,i])**2 + malla.profundidad**2)
            V += I_falla * rho / (4 * np.pi * r)
    
    # Contribución de varillas
    for x_v, y_v, l in malla.obtener_varillas():
        r = np.sqrt((x - x_v)**2 + (y - y_v)**2 + malla.profundidad**2)
        V += I_falla * rho * l / (4 * np.pi * r**2)
    
    return V
