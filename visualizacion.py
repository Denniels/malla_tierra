# -*- coding: utf-8 -*-
"""
Módulo para visualización avanzada y reportes de la malla de tierra
"""
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import seaborn as sns
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import datetime
import os
from suelo import CapaSuelo

@dataclass
class LimitesVisualizacion:
    """Clase para manejar los límites de visualización"""
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float
    
    @classmethod
    def desde_malla(cls, malla, margen: float = 1.0):
        """Crea límites a partir de una malla con margen"""
        return cls(
            x_min=-margen,
            x_max=malla.ancho + margen,
            y_min=-margen,
            y_max=malla.largo + margen,
            z_min=-(malla.profundidad + max([v.longitud for v in malla.varillas] or [0]) + margen),
            z_max=margen
        )
    
    def as_tuple(self) -> Tuple[float, float, float, float, float, float]:
        """Convierte los límites a una tupla de 6 elementos"""
        return (self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max)

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

def generar_vista_3d_multicapa(
    malla,
    capas,
    mostrar_varillas=True,
    progress_callback=None,
    mostrar_uniones=True,
    tipo_union="Soldadura exotérmica",
    mostrar_potenciales=True,
    modo_test=False
):
    """Genera una vista 3D de la malla con múltiples capas"""
    try:
        import pyvista as pv
        # Inicializar el plotter
        plotter = pv.Plotter(off_screen=modo_test)
        
        # Configurar el tema
        plotter.set_background('white')
        
        # Crear conductores
        conductores = []
        for x in np.arange(0, malla.ancho + malla.espaciamiento, malla.espaciamiento):
            for y in np.arange(0, malla.largo + malla.espaciamiento, malla.espaciamiento):
                conductor = pv.Cylinder(
                    center=(x, y, -malla.profundidad),
                    direction=(0, 0, 1),
                    radius=0.01,
                    height=0.1
                )
                conductores.append(conductor)
                
        # Agregar conductores con color correcto
        for conductor in conductores:
            plotter.add_mesh(conductor, color=[0.72, 0.45, 0.20], metallic=1.0)  # Color cobrizo
            
        # Agregar varillas si se solicita
        if mostrar_varillas:
            for x, y, l in malla.obtener_varillas():
                varilla = pv.Cylinder(
                    center=(x, y, -malla.profundidad),
                    direction=(0, 0, -1),
                    radius=0.008,
                    height=l
                )
                plotter.add_mesh(varilla, color=[0.5, 0.5, 0.5])  # Color gris
                  # Configurar la vista
        plotter.view_isometric()
        plotter.camera.zoom(1.2)
        
        # Notificar progreso si hay un callback
        if progress_callback:
            progress_callback(1.0, "Visualización 3D completada")
        
        return plotter
        
    except Exception as e:
        raise ValueError(f"Error en la visualización 3D: {str(e)}")

def calcular_materiales(malla, tipo_union="Soldadura exotérmica"):
    """
    Calcula la cantidad de materiales necesarios para la instalación.
    
    Args:
        malla: Objeto MallaTierra
        tipo_union: Tipo de unión a utilizar
    
    Returns:
        dict: Diccionario con cantidades de materiales
    """
    # Calcular longitud total de conductor
    long_horizontal = (malla.ancho/malla.espaciamiento + 1) * malla.largo + \
                     (malla.largo/malla.espaciamiento + 1) * malla.ancho
    
    # Calcular longitud de varillas
    n_varillas = len(list(malla.obtener_varillas()))
    long_varillas = sum(l for _, _, l in malla.obtener_varillas())
    
    # Calcular número de uniones
    n_uniones_conductores = (int(malla.ancho/malla.espaciamiento) + 1) * \
                           (int(malla.largo/malla.espaciamiento) + 1)
    n_uniones_varillas = n_varillas
    
    return {
        "conductor_horizontal": round(long_horizontal, 2),
        "conductor_vertical": round(long_varillas, 2),
        "varillas": n_varillas,
        "uniones_conductores": n_uniones_conductores,
        "uniones_varillas": n_uniones_varillas,
        "material_union": round((n_uniones_conductores + n_uniones_varillas) * \
                              (0.15 if tipo_union == "Soldadura exotérmica" else 0.1), 2),
        "tipo_union": tipo_union
    }

def generar_vista_2d_simple(malla, capas=None):
    """
    Genera una vista 2D simple de la malla usando Matplotlib.
    Esta es la visualización más básica y robusta.
    
    Args:
        malla: Objeto MallaTierra
        capas: Lista opcional de capas de suelo
    
    Returns:
        tuple: (figura, ejes) de matplotlib
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Agregar un fondo suave
    ax.set_facecolor('#f0f0f0')
    
    # Dibujar el perímetro de la malla con un estilo más visible
    ax.fill([0, malla.ancho, malla.ancho, 0],
            [0, 0, malla.largo, malla.largo],
            alpha=0.1, color='blue', label='Área de la malla')
    
    ax.plot([0, malla.ancho, malla.ancho, 0, 0],
            [0, 0, malla.largo, malla.largo, 0],
            'k-', linewidth=2, label='Perímetro')
    
    # Dibujar conductores con mejor estilo
    x = np.arange(0, malla.ancho + malla.espaciamiento, malla.espaciamiento)
    y = np.arange(0, malla.largo + malla.espaciamiento, malla.espaciamiento)
    
    # Conductores horizontales
    for yi in y:
        ax.plot(x, [yi] * len(x), 'b-', linewidth=1.5, alpha=0.7,
                label='Conductor' if yi == 0 else "")
    
    # Dibujar varillas
    for x, y, l in malla.obtener_varillas():
        ax.plot(x, y, 'ro', markersize=8, label='Varilla')
        # Solo etiquetar la primera varilla
        if 'Varilla' in ax.get_legend_handles_labels()[1]:
            ax.plot(x, y, 'ro', markersize=8)
        
    ax.set_xlabel('Distancia (m)')
    ax.set_ylabel('Distancia (m)')
    ax.set_title('Vista Superior de la Malla de Tierra')
    ax.grid(True)
    ax.axis('equal')
    ax.legend()
    
    return fig, ax

def generar_vista_2d(malla, capas=None, mostrar_medidas=True, estilo='modern', mostrar_varillas=True):
    """
    Genera una vista 2D de la malla usando matplotlib.
    
    Args:
        malla: Objeto MallaTierra
        capas: Lista opcional de CapaSuelo (no usado en vista 2D)
        mostrar_medidas: Si se muestran las dimensiones
        estilo: Estilo de visualización ('modern', 'technical', 'simple')
        mostrar_varillas: Si se muestran las varillas de tierra
    
    Returns:
        tuple: (figura, ejes) de matplotlib
    """
    # Configurar el estilo
    if estilo == 'modern':
        plt.style.use('seaborn')
        color_conductores = '#2C3E50'
        color_varillas = '#E74C3C'
        color_grid = '#BDC3C7'
    elif estilo == 'technical':
        plt.style.use('default')
        color_conductores = 'black'
        color_varillas = 'red'
        color_grid = 'gray'
    else:  # simple
        plt.style.use('classic')
        color_conductores = 'blue'
        color_varillas = 'red'
        color_grid = 'lightgray'
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Dibujar grid de fondo
    ax.grid(True, color=color_grid, linestyle='--', alpha=0.5)
    
    # Dibujar conductores
    x_nodos, y_nodos = malla.obtener_nodos()
    
    # Conductores horizontales
    for i in range(x_nodos.shape[0]):
        ax.plot(x_nodos[i], y_nodos[i], 
                color=color_conductores, linewidth=1.5,
                label='Conductor' if i == 0 else "")
                
    # Conductores verticales
    for j in range(x_nodos.shape[1]):
        ax.plot(x_nodos[:, j], y_nodos[:, j], 
                color=color_conductores, linewidth=1.5)
    
    # Dibujar varillas si está habilitado
    if mostrar_varillas:
        for x, y, l in malla.obtener_varillas():
            ax.plot(x, y, 'o', color=color_varillas, markersize=8,
                    label='Varilla de tierra' if x == malla.obtener_varillas()[0][0] else "")
    
    # Agregar medidas si se solicita
    if mostrar_medidas:
        # Dimensiones totales
        ax.annotate(f'{malla.ancho}m', 
                   xy=(malla.ancho/2, -malla.largo*0.05),
                   xycoords='data',
                   ha='center', va='top')
                   
        ax.annotate(f'{malla.largo}m',
                   xy=(-malla.ancho*0.05, malla.largo/2),
                   xycoords='data',
                   ha='right', va='center',
                   rotation=90)
        
        # Espaciamiento
        ax.annotate(f'Esp: {malla.espaciamiento}m',
                   xy=(0, -malla.largo*0.1),
                   xycoords='data',
                   ha='left', va='top')
    
    # Configurar ejes
    ax.set_xlim(-malla.ancho*0.1, malla.ancho*1.1)
    ax.set_ylim(-malla.largo*0.1, malla.largo*1.1)
    ax.set_xlabel('Distancia (m)')
    ax.set_ylabel('Distancia (m)')
    ax.set_title('Vista Superior de la Malla de Tierra')
    
    # Mantener escala 1:1
    ax.set_aspect('equal')
    
    # Agregar leyenda si hay elementos etiquetados
    if len(ax.get_legend_handles_labels()[0]) > 0:
        ax.legend()
    
    return fig, ax

def generar_vista_3d_simple(malla, capas=None, mostrar_medidas=True, estilo='modern', mostrar_varillas=True):
    """
    Genera una vista 3D simple usando matplotlib.
    
    Args:
        malla: Objeto MallaTierra
        capas: Lista opcional de CapaSuelo 
        mostrar_medidas: Si se muestran las dimensiones
        estilo: Estilo de visualización ('modern', 'technical', 'simple')
        mostrar_varillas: Si se muestran las varillas de tierra
    
    Returns:
        tuple: (figura, ejes) de matplotlib
    """
    # Configurar el estilo
    if estilo == 'modern':
        plt.style.use('seaborn')
        color_conductores = '#2C3E50'
        color_varillas = '#E74C3C'
        color_suelo = '#ECF0F1'
    elif estilo == 'technical':
        plt.style.use('default')
        color_conductores = 'black'
        color_varillas = 'red'
        color_suelo = 'lightgray'
    else:  # simple
        plt.style.use('classic')
        color_conductores = 'blue'
        color_varillas = 'red'
        color_suelo = '#F0F0F0'
    
    # Crear figura 3D
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Dibujar superficie del suelo
    x_suelo = np.linspace(-1, malla.ancho+1, 50)
    y_suelo = np.linspace(-1, malla.largo+1, 50)
    X_suelo, Y_suelo = np.meshgrid(x_suelo, y_suelo)
    Z_suelo = np.zeros_like(X_suelo)
    ax.plot_surface(X_suelo, Y_suelo, Z_suelo, alpha=0.2, color=color_suelo)
    
    # Dibujar conductores horizontales
    x_nodos, y_nodos = malla.obtener_nodos()
    z_nodos = np.full_like(x_nodos, -malla.profundidad)
    
    # Conductores en dirección X
    for i in range(x_nodos.shape[0]):
        ax.plot(x_nodos[i], y_nodos[i], z_nodos[i], 
                color=color_conductores, linewidth=2,
                label='Conductor' if i == 0 else None)
    
    # Conductores en dirección Y
    for i in range(x_nodos.shape[1]):
        ax.plot(x_nodos[:, i], y_nodos[:, i], z_nodos[:, i],
                color=color_conductores, linewidth=2)
    
    # Dibujar varillas si está habilitado
    if mostrar_varillas:
        for x, y, l in malla.obtener_varillas():
            ax.plot([x, x], [y, y], 
                    [-malla.profundidad, -malla.profundidad-l],
                    color=color_varillas, linewidth=3,
                    label='Varilla de tierra' if x == malla.obtener_varillas()[0][0] else None)
    
    if mostrar_medidas:
        # Mostrar dimensiones principales
        ax.text(malla.ancho/2, -1, 0, f'{malla.ancho}m',
                horizontalalignment='center')
        ax.text(-1, malla.largo/2, 0, f'{malla.largo}m',
                horizontalalignment='right')
        ax.text(0, -1, -malla.profundidad/2, f'{malla.profundidad}m',
                horizontalalignment='right')
    
    # Configurar vista
    limites = LimitesVisualizacion.desde_malla(malla, margen=1)
    ax.set_xlim(limites.x_min, limites.x_max)
    ax.set_ylim(limites.y_min, limites.y_max)
    ax.set_zlim(limites.z_min, limites.z_max)
    
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title('Vista 3D de la Malla de Tierra')
    
    # Ajustar ángulo de vista
    ax.view_init(elev=20, azim=45)
    
    # Agregar leyenda si hay elementos etiquetados
    if len(ax.get_legend_handles_labels()[0]) > 0:
        ax.legend()
    
    return fig, ax

def visualizar_malla(malla, capas=None, modo='2d', mostrar_medidas=True, estilo='modern', mostrar_varillas=True):
    """
    Función principal de visualización que selecciona el método apropiado
    
    Args:
        malla: Objeto MallaTierra
        capas: Lista opcional de CapaSuelo
        modo: Tipo de visualización ('2d', '3d-simple', '3d-avanzada')
        mostrar_medidas: Si se muestran las dimensiones
        estilo: Estilo de visualización ('modern', 'technical', 'simple')
        mostrar_varillas: Si se muestran las varillas de tierra (True por defecto)
    
    Returns:
        fig, ax: Objetos de matplotlib
    """
    if modo == '2d':
        return generar_vista_2d(malla, capas, mostrar_medidas, estilo, mostrar_varillas)
    elif modo == '3d-simple':
        return generar_vista_3d_simple(malla, capas, mostrar_medidas, estilo, mostrar_varillas)
    else:
        try:
            import pyvista as pv
            return generar_vista_3d_multicapa(
                malla, 
                capas if capas else [CapaSuelo(profundidad=malla.profundidad, resistividad=100)],
                mostrar_varillas=mostrar_varillas,
                mostrar_uniones=True,
                tipo_union="Soldadura exotérmica",
                mostrar_potenciales=True,
                modo_test=True  # Activar modo de prueba para entorno sin interfaz gráfica
            )
        except ImportError:
            print("PyVista no está disponible. Usando visualización 3D simple.")
            return generar_vista_3d_simple(malla, capas, mostrar_medidas, estilo, mostrar_varillas)
