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
    y -= 40
    
    # Generar y guardar gráficos temporales
    temp_files = []
    
    try:
        # Mapa de calor
        fig1, ax1 = generar_mapa_calor(
            resultados.get('I_falla', 1000),
            parametros.get('resistividad', 100),
            malla,
            calcular_potenciales_superficie(
                malla,
                resultados.get('I_falla', 1000),
                parametros.get('resistividad', 100)
            )
        )
        temp_path1 = os.path.join("reportes", f"temp_mapa_calor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.savefig(temp_path1, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig1)
        temp_files.append(temp_path1)
        
        # Perfil del suelo
        fig2, ax2 = generar_perfil_suelo(
            malla,
            parametros.get('resistividad', 100),
            parametros.get('profundidad', 0.5),
            parametros.get('rho_s', 3000)
        )
        temp_path2 = os.path.join("reportes", f"temp_perfil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.savefig(temp_path2, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig2)
        temp_files.append(temp_path2)
        
        # Agregar imágenes al PDF
        c.drawString(50, y, "Distribución de Potenciales:")
        y -= 320
        c.drawImage(temp_path1, 50, y, width=500, height=300, preserveAspectRatio=True)
        
        y -= 40
        c.drawString(50, y, "Perfil del Suelo:")
        y -= 320
        c.drawImage(temp_path2, 50, y, width=500, height=300, preserveAspectRatio=True)
        
        # Finalizar PDF
        c.save()
        
    finally:
        # Limpiar archivos temporales
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
    
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

def generar_reporte_markdown(
    malla,
    parametros: dict,
    resultados: dict,
    imagenes: dict = None
) -> str:
    """
    Genera un reporte detallado en formato Markdown.
    
    Args:
        malla: Objeto MallaTierra
        parametros: Diccionario con parámetros de entrada
        resultados: Diccionario con resultados calculados
        imagenes: Diccionario con rutas a imágenes generadas
    
    Returns:
        str: Contenido del reporte en formato Markdown
    """
    md = []
    
    # Título y fecha
    md.append("# 📊 Reporte de Malla de Puesta a Tierra")
    md.append(f"*Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}*\n")
    
    # Resumen ejecutivo
    md.append("## 📝 1. Resumen Ejecutivo")
    md.append("Este reporte presenta el análisis detallado de una malla de puesta a tierra, ")
    md.append("incluyendo sus características físicas, parámetros eléctricos y evaluación de seguridad.\n")
    
    # Parámetros de diseño
    md.append("## 2. Parámetros de Diseño")
    md.append("### 2.1 Dimensiones Físicas")
    md.append(f"- **Tipo de malla**: {'Rectangular' if malla.ancho != malla.largo else 'Cuadrada'}")
    md.append(f"- **Dimensiones**: {malla.ancho}m × {malla.largo}m")
    md.append(f"- **Área total**: {malla.ancho * malla.largo:.2f} m²")
    md.append(f"- **Profundidad**: {malla.profundidad} m")
    md.append(f"- **Espaciamiento**: {malla.espaciamiento:.2f} m\n")
    
    md.append("### 2.2 Características del Conductor")
    md.append(f"- **Material**: {malla.conductor.material}")
    md.append(f"- **Diámetro**: {malla.conductor.diametro*1000:.1f} mm")
    if hasattr(malla, 'varillas') and malla.varillas:
        md.append(f"- **Número de varillas**: {len(malla.varillas)}")
        md.append(f"- **Longitud de varillas**: {malla.varillas[0].longitud} m")
    md.append("")
    
    # Parámetros eléctricos
    md.append("## 3. Parámetros Eléctricos")
    for key, value in parametros.items():
        md.append(f"- **{key}**: {value}")
    md.append("")
    
    # Resultados y análisis
    md.append("## 4. Resultados del Análisis")
    for key, value in resultados.items():
        md.append(f"- **{key}**: {value}")
    md.append("")
    
    # Evaluación de seguridad
    md.append("## 5. Evaluación de Seguridad")
    if 'Potencial de paso' in resultados and 'Potencial de contacto' in resultados:
        paso = float(resultados['Potencial de paso'].split()[0])
        contacto = float(resultados['Potencial de contacto'].split()[0])
        paso_max = 2881.24  # Valores según IEEE-80
        contacto_max = 843.35
        
        md.append("### 5.1 Potenciales de Seguridad")
        md.append(f"- Potencial de paso: {paso:.2f}V (Máximo permitido: {paso_max}V)")
        md.append(f"  - Estado: {'✅ SEGURO' if paso < paso_max else '⚠️ EXCEDE LÍMITE'}")
        md.append(f"- Potencial de contacto: {contacto:.2f}V (Máximo permitido: {contacto_max}V)")
        md.append(f"  - Estado: {'✅ SEGURO' if contacto < contacto_max else '⚠️ EXCEDE LÍMITE'}\n")
    
    # Recomendaciones
    md.append("## 6. Recomendaciones")
    if paso > paso_max * 0.8 or contacto > contacto_max * 0.8:
        md.append("### Acciones recomendadas para mejorar la seguridad:")
        if paso > paso_max * 0.8:
            md.append("- Reducir el espaciamiento entre conductores")
            md.append("- Considerar aumentar el área de la malla")
        if contacto > contacto_max * 0.8:
            md.append("- Agregar más varillas de puesta a tierra")
            md.append("- Mejorar el tratamiento del suelo")
    else:
        md.append("✅ El diseño cumple con todos los criterios de seguridad.")
        md.append("Se recomienda realizar mantenimiento preventivo periódico:")
        md.append("- Inspección visual anual")
        md.append("- Medición de resistencia cada 2 años")
        md.append("- Verificación de conexiones cada 5 años")
    md.append("")
    
    # Visualizaciones
    md.append("## 7. Visualizaciones")
    if imagenes:
        for titulo, ruta in imagenes.items():
            md.append(f"### {titulo}")
            md.append(f"![{titulo}]({ruta})\n")
    
    return "\n".join(md)
