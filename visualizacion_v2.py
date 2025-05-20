#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo mejorado para visualización de mallas de tierra
Implementa múltiples métodos de visualización con fallback automático
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import matplotlib.patches as patches
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass

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
        max_longitud_varilla = 0
        if hasattr(malla, 'varillas') and malla.varillas:
            max_longitud_varilla = max(v.longitud for v in malla.varillas)
            
        return cls(
            x_min=-margen,
            x_max=malla.ancho + margen,
            y_min=-margen,
            y_max=malla.largo + margen,
            z_min=-(malla.profundidad + max_longitud_varilla + margen),
            z_max=margen
        )
    
    def as_tuple(self) -> Tuple[float, float, float, float, float, float]:
        """Convierte los límites a una tupla de 6 elementos"""
        return (self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max)

def generar_vista_2d(malla, capas=None, mostrar_medidas=True, estilo='modern'):
    """
    Genera una vista 2D de la malla usando matplotlib
    
    Args:
        malla: Objeto MallaTierra
        capas: Lista opcional de CapaSuelo
        mostrar_medidas: Si se muestran las dimensiones
        estilo: Estilo de visualización ('modern', 'technical', 'simple')
    
    Returns:
        fig, ax: Objetos de matplotlib
    """
    # Configurar el estilo
    if estilo == 'modern':
        plt.style.use('seaborn')
        color_conductores = '#2C3E50'
        color_varillas = '#E74C3C'
        color_grid = '#BDC3C7'
    elif estilo == 'technical':
        plt.style.use('classic')
        color_conductores = 'black'
        color_varillas = 'red'
        color_grid = 'gray'
    else:  # simple
        plt.style.use('default')
        color_conductores = 'blue'
        color_varillas = 'red'
        color_grid = 'lightgray'
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Dibujar conductores horizontales
    x_nodos, y_nodos = malla.obtener_nodos()
    ax.plot(x_nodos, y_nodos, '-', color=color_conductores, linewidth=2, label='Conductores')
    ax.plot(x_nodos.T, y_nodos.T, '-', color=color_conductores, linewidth=2)
    
    # Dibujar varillas
    if hasattr(malla, 'varillas'):
        for x, y, l in malla.obtener_varillas():
            circle = plt.Circle((x, y), 0.2, color=color_varillas, fill=True, alpha=0.6)
            ax.add_patch(circle)
            ax.plot(x, y, 'o', color=color_varillas, markersize=8)
    
    # Mostrar medidas si se solicita
    if mostrar_medidas:
        # Dimensiones totales
        ax.annotate(f'{malla.ancho}m', 
                   xy=(malla.ancho/2, -0.5),
                   xytext=(malla.ancho/2, -1),
                   ha='center', va='top',
                   arrowprops=dict(arrowstyle='<->'))
                   
        ax.annotate(f'{malla.largo}m',
                   xy=(-0.5, malla.largo/2),
                   xytext=(-1, malla.largo/2),
                   ha='right', va='center',
                   rotation=90,
                   arrowprops=dict(arrowstyle='<->'))
                   
        # Espaciamiento
        if hasattr(malla, 'espaciamiento_x'):
            ax.annotate(f'{malla.espaciamiento_x:.1f}m',
                       xy=(malla.espaciamiento_x/2, 0),
                       xytext=(malla.espaciamiento_x/2, 0.5),
                       ha='center', va='bottom')
    
    # Configurar límites y etiquetas
    margen = 2 if mostrar_medidas else 1
    limites = LimitesVisualizacion.desde_malla(malla, margen=margen)
    ax.set_xlim(limites.x_min, limites.x_max)
    ax.set_ylim(limites.y_min, limites.y_max)
    
    ax.set_xlabel('Distancia (m)')
    ax.set_ylabel('Distancia (m)')
    ax.set_title('Vista Superior de la Malla de Tierra')
    ax.grid(True, linestyle='--', alpha=0.7, color=color_grid)
    ax.set_aspect('equal')
    
    return fig, ax

def generar_vista_3d_simple(malla, capas=None, mostrar_medidas=True, estilo='modern'):
    """
    Genera una vista 3D simple usando matplotlib
    
    Args:
        malla: Objeto MallaTierra
        capas: Lista opcional de CapaSuelo
        mostrar_medidas: Si se muestran las dimensiones
        estilo: Estilo de visualización ('modern', 'technical', 'simple')
    
    Returns:
        fig, ax: Objetos de matplotlib
    """
    # Configurar el estilo
    if estilo == 'modern':
        plt.style.use('seaborn')
        color_conductores = '#2C3E50'
        color_varillas = '#E74C3C'
        color_suelo = '#ECF0F1'
    else:
        plt.style.use('default')
        color_conductores = 'black'
        color_varillas = 'red'
        color_suelo = 'lightgray'
    
    # Crear figura 3D
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Dibujar superficie del suelo
    x = np.linspace(-1, malla.ancho+1, 100)
    y = np.linspace(-1, malla.largo+1, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    ax.plot_surface(X, Y, Z, alpha=0.2, color=color_suelo)
    
    # Dibujar conductores horizontales
    x_nodos, y_nodos = malla.obtener_nodos()
    z_nodos = np.full_like(x_nodos, -malla.profundidad)
    
    for i in range(x_nodos.shape[0]):
        ax.plot(x_nodos[i], y_nodos[i], z_nodos[i], 
                color=color_conductores, linewidth=2)
    for i in range(x_nodos.shape[1]):
        ax.plot(x_nodos[:, i], y_nodos[:, i], z_nodos[:, i],
                color=color_conductores, linewidth=2)
    
    # Dibujar varillas
    if hasattr(malla, 'varillas'):
        for x, y, l in malla.obtener_varillas():
            ax.plot([x, x], [y, y], 
                    [-malla.profundidad, -malla.profundidad-l],
                    color=color_varillas, linewidth=3)
    
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
    
    return fig, ax

def visualizar_malla(malla, capas=None, modo='2d', mostrar_medidas=True, estilo='modern'):
    """
    Función principal de visualización que selecciona el método apropiado
    
    Args:
        malla: Objeto MallaTierra
        capas: Lista opcional de CapaSuelo
        modo: Tipo de visualización ('2d', '3d-simple', '3d-avanzada')
        mostrar_medidas: Si se muestran las dimensiones
        estilo: Estilo de visualización ('modern', 'technical', 'simple')
    
    Returns:
        fig, ax: Objetos de matplotlib
    """
    if modo == '2d':
        return generar_vista_2d(malla, capas, mostrar_medidas, estilo)
    elif modo == '3d-simple':
        return generar_vista_3d_simple(malla, capas, mostrar_medidas, estilo)
    else:
        try:
            import pyvista as pv
            # La visualización avanzada requiere PyVista, que es opcional
            from visualizacion import generar_vista_3d_avanzada
            return generar_vista_3d_avanzada(malla, capas, mostrar_medidas)
        except ImportError:
            print("PyVista no está disponible. Usando visualización 3D simple.")
            return generar_vista_3d_simple(malla, capas, mostrar_medidas, estilo)

def actualizar_app(st, malla):
    """Actualiza la visualización en la aplicación Streamlit"""
    try:
        modo = st.selectbox('Modo de Visualización', 
                          ['2D', '3D Simple', '3D Avanzada'],
                          key='modo_viz')
                          
        estilo = st.selectbox('Estilo', 
                           ['modern', 'technical', 'simple'],
                           key='estilo_viz')
                           
        mostrar_medidas = st.checkbox('Mostrar Medidas', 
                                   value=True,
                                   key='mostrar_medidas')
        
        # Mapear selección a modo interno
        modo_map = {
            '2D': '2d',
            '3D Simple': '3d-simple',
            '3D Avanzada': '3d-avanzada'
        }
        
        fig, ax = visualizar_malla(
            malla,
            modo=modo_map[modo],
            mostrar_medidas=mostrar_medidas,
            estilo=estilo
        )
        
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"Error en la visualización: {str(e)}")
        raise
