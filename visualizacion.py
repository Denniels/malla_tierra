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

def generar_vista_3d_multicapa(malla, capas, mostrar_varillas=True, progress_callback=None):
    """
    Genera una visualización 3D de la malla de tierra con múltiples capas usando PyVista
    
    Args:
        malla: Objeto MallaTierra
        capas: Lista de objetos CapaSuelo
        mostrar_varillas: Si se deben mostrar las varillas
        progress_callback: Función para actualizar el progreso (opcional)
    
    Returns:
        str: Ruta al archivo de imagen generado
    """
    import pyvista as pv
    import numpy as np
    from datetime import datetime
    import os
    
    if not capas:
        raise ValueError("No hay capas de suelo definidas para la visualización 3D")
    
    # Notificar inicio
    if progress_callback:
        progress_callback(0.0, "Iniciando visualización 3D...")
    
    # Crear un plotter con configuración optimizada
    plotter = pv.Plotter(off_screen=True)  # off_screen=True para mejor rendimiento
    plotter.set_background('white')
    
    # Colores optimizados para mejor visibilidad
    colores_capas = [
        (0.8, 0.4, 0.4, 0.3),  # Rojo con menos opacidad
        (0.4, 0.4, 0.8, 0.3),  # Azul con menos opacidad
        (0.4, 0.8, 0.4, 0.3),  # Verde con menos opacidad
        (0.8, 0.8, 0.4, 0.3),  # Amarillo con menos opacidad
    ]
    
    # Crear una malla simplificada para cada capa
    total_steps = len(capas) + (1 if mostrar_varillas else 0)
    current_step = 0
    
    for i, capa in enumerate(capas):
        if progress_callback:
            progress_callback((current_step + 0.5) / total_steps, f"Procesando capa {i+1}...")
        
        # Crear puntos para la malla con resolución optimizada
        n_points = min(malla.n_x, 20)  # Limitar el número de puntos para mejor rendimiento
        x = np.linspace(0, malla.ancho, n_points)
        y = np.linspace(0, malla.largo, n_points)
        z = -capa.profundidad
        
        # Crear grilla de conductores con menor densidad
        for yi in y[::2]:  # Tomar un punto cada dos para reducir densidad
            for j in range(0, len(x)-1, 2):  # Reducir densidad de líneas
                line = pv.Line((x[j], yi, z), (x[j+1], yi, z))
                plotter.add_mesh(line, color=colores_capas[i % len(colores_capas)], line_width=2)
        
        # Crear plano semitransparente para la capa
        grid = pv.StructuredGrid()
        grid.points = np.array([(x_, y_, z) for x_ in x for y_ in y])
        grid.dimensions = [len(x), len(y), 1]
        plotter.add_mesh(grid, color=colores_capas[i % len(colores_capas)], opacity=0.2)
        
        # Agregar texto con información
        plotter.add_text(
            f"Capa {i+1}\n{capa.profundidad}m\n{capa.resistividad}Ω⋅m",
            position=(malla.ancho + 1, 0, -capa.profundidad),
            font_size=10,
            color='black'
        )
        
        current_step += 1
    
    # Agregar varillas si se solicita
    if mostrar_varillas and hasattr(malla, 'varillas'):
        if progress_callback:
            progress_callback((current_step + 0.5) / total_steps, "Agregando varillas...")
            
        for varilla in malla.varillas:
            inicio = (varilla.posicion_x, varilla.posicion_y, -capas[0].profundidad)
            fin = (varilla.posicion_x, varilla.posicion_y, 
                  -(capas[0].profundidad + varilla.longitud))
            varilla_line = pv.Line(inicio, fin)
            plotter.add_mesh(varilla_line, color='black', line_width=3)
    
    # Ajustar la cámara y vista
    if progress_callback:
        progress_callback(0.9, "Finalizando visualización...")
        
    plotter.camera_position = 'iso'
    plotter.camera.zoom(1.2)
    
    # Generar imagen
    os.makedirs("reportes", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_salida = os.path.join("reportes", f"malla_3d_{timestamp}.png")
    
    # Guardar con resolución optimizada
    plotter.show(screenshot=ruta_salida, window_size=[800, 600])
    
    if progress_callback:
        progress_callback(1.0, "Visualización completada")
    
    return ruta_salida

def generar_vista_3d_multicapa(
    malla,
    capas,
    mostrar_varillas=True,
    progress_callback=None,
    mostrar_uniones=True,
    tipo_union="Soldadura exotérmica"
):
    """
    Genera una vista 3D de la malla con capas y uniones.
    
    Args:
        malla: Objeto MallaTierra
        capas: Lista de objetos CapaSuelo
        mostrar_varillas: Boolean para mostrar varillas
        progress_callback: Función para actualizar progreso
        mostrar_uniones: Boolean para mostrar puntos de unión
        tipo_union: Tipo de unión ("Soldadura exotérmica" o "Conectores mecánicos")
    """
    try:
        import pyvista as pv
        import tempfile
        import numpy as np
        
        if progress_callback:
            progress_callback(0.1, "Iniciando visualización 3D...")
        
        # Crear plotter con mejor calidad
        plotter = pv.Plotter(off_screen=True, window_size=[1920, 1080])
        plotter.set_background('white')
        
        # Configurar iluminación
        plotter.add_light(pv.Light(position=(0, 0, 1), intensity=0.8))
        plotter.add_light(pv.Light(position=(1, 1, -1), intensity=0.3))
        
        # Calcular dimensiones totales para los límites
        x_min, x_max = -malla.ancho * 0.1, malla.ancho * 1.1
        y_min, y_max = -malla.largo * 0.1, malla.largo * 1.1
        z_min = -max(capa.profundidad for capa in capas) * 1.1
        z_max = malla.ancho * 0.1
        
        # Establecer los límites explícitamente como una tupla de 6 elementos
        plotter.set_bounds((x_min, x_max, y_min, y_max, z_min, z_max))
        
        # Crear una caja invisible que define los límites
        box = pv.Box([x_min, y_min, z_min], [x_max, y_max, z_max])
        plotter.add_mesh(box, opacity=0.0)
        
        # Crear grid de referencia en la superficie
        x = np.linspace(0, malla.ancho, 20)
        y = np.linspace(0, malla.largo, 20)
        z = np.zeros((20, 20))
        x_grid, y_grid = np.meshgrid(x, y)
        grid = pv.StructuredGrid(x_grid, y_grid, z)
        plotter.add_mesh(grid, color='lightgray', opacity=0.3)
        
        # Variables para el cálculo de resistencias equivalentes
        resistencias_capas = []
        resistencia_total = 0
        
        # Panel de información
        info_panel = []
        info_panel.append("INFORMACIÓN DE CAPAS")
        info_panel.append("-----------------")
        
        # Dibujar capas del suelo y sus mallas
        for i, capa in enumerate(capas):
            # Calcular resistencia de esta capa
            area = malla.ancho * malla.largo
            espesor = capa.profundidad - (capas[i-1].profundidad if i > 0 else 0)
            resistencia_capa = capa.resistividad * espesor / area
            resistencias_capas.append(resistencia_capa)
            
            # Calcular resistencia equivalente hasta esta capa
            if i == 0:
                resistencia_total = resistencia_capa
            else:
                resistencia_total = 1 / (1/resistencia_total + 1/resistencia_capa)
            
            # Actualizar panel de información
            info_panel.append(f"\nCapa {i+1}:")
            info_panel.append(f"Prof: {capa.profundidad}m")
            info_panel.append(f"Espesor: {espesor:.2f}m")
            info_panel.append(f"ρ: {capa.resistividad}Ω⋅m")
            info_panel.append(f"R capa: {resistencia_capa:.2f}Ω")
            info_panel.append(f"R equiv: {resistencia_total:.2f}Ω")
            
            # Dibujar capa de suelo
            box = pv.Box([0, 0, -capa.profundidad],
                        [malla.ancho, malla.largo, espesor])
            
            # Color basado en la resistividad (más rojo = más resistivo)
            intensidad_rojo = min(1.0, capa.resistividad / 1000)
            color = f'#{int(255*intensidad_rojo):02x}{int(255*(1-intensidad_rojo)):02x}{int(255*(1-intensidad_rojo)):02x}'
            
            # Agregar capa con bordes
            plotter.add_mesh(box, opacity=0.3, color=color,
                           label=f'Capa {i+1}',
                           show_edges=True,
                           edge_color='black',
                           line_width=1)
            
            # Dibujar malla en esta capa
            x_nodos, y_nodos = malla.obtener_nodos()
            
            # Conductores horizontales y verticales con mayor grosor
            for j in range(len(x_nodos)):
                line = pv.Line([x_nodos[j,0], y_nodos[j,0], -capa.profundidad],
                             [x_nodos[j,-1], y_nodos[j,-1], -capa.profundidad])
                plotter.add_mesh(line, color='blue', line_width=4)
            
            for j in range(len(x_nodos[0])):
                line = pv.Line([x_nodos[0,j], y_nodos[0,j], -capa.profundidad],
                             [x_nodos[-1,j], y_nodos[-1,j], -capa.profundidad])
                plotter.add_mesh(line, color='blue', line_width=4)
            
            # Mostrar conexiones entre capas
            if i < len(capas) - 1:
                for x, y in zip(x_nodos.flatten(), y_nodos.flatten()):
                    # Línea de conexión
                    conexion = pv.Line([x, y, -capa.profundidad],
                                     [x, y, -capas[i+1].profundidad])
                    plotter.add_mesh(conexion, color='purple', line_width=2)
                    
                    if mostrar_uniones:
                        # Uniones en ambos extremos
                        for z in [-capa.profundidad, -capas[i+1].profundidad]:
                            sphere = pv.Sphere(radius=0.12, center=(x, y, z))
                            color = 'orange' if tipo_union == "Soldadura exotérmica" else 'green'
                            plotter.add_mesh(sphere, color=color)
            
            if progress_callback:
                progress_callback(0.2 + 0.6*i/len(capas), f"Dibujando capa {i+1}...")
        
        # Agregar panel de información completo
        info_panel.append("\nRESISTENCIA TOTAL")
        info_panel.append("-----------------")
        info_panel.append(f"R total: {resistencia_total:.2f}Ω")
        
        # Calcular y mostrar las resistencias entre capas
        info_text = "Resistencias entre capas:\n"
        for i in range(len(capas)-1):
            capa_actual = capas[i]
            capa_siguiente = capas[i+1]
            resistencia = (capa_actual.resistividad + capa_siguiente.resistividad) / 2 * \
                         (capa_siguiente.profundidad - capa_actual.profundidad) / \
                         (malla.ancho * malla.largo)
            info_text += f"Capa {i+1} → {i+2}: {resistencia:.2f}Ω\n"
        
        # Añadir el panel de información
        plotter.add_text(info_text, position='upper_left', font_size=12)
        
        # Configurar la vista final
        plotter.view_isometric()
        plotter.show_grid()
        
        # Guardar imagen con alta calidad
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        plotter.screenshot(temp_file.name, transparent_background=True, window_size=[1920, 1080])
        
        if progress_callback:
            progress_callback(1.0, "¡Visualización completada!")
        
        return temp_file.name
        
    except ImportError as e:
        raise ImportError("Se requiere PyVista para la visualización 3D") from e

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
