'''import plotly.graph_objects as go

def plot_malla_tierra(I, R_des, sigma, rho, I_falla, L, A, n_barras):
    print("Entrando en plot_malla_tierra")

    # Coordenadas de las barras en la malla
    x_coords = [i * 100 for i in range(n_barras + 1)] # Agregué un valor adicional para incluir el final de la malla
    y_coords_vert = [-A, -A] + [0] * (n_barras - 1) + [A, A]
    z_coords_vert = [[-A, A]] * n_barras

    # Coordenadas de los conectores horizontales entre barras verticales
    y_coords_horz = [A] * n_barras
    z_coords_horz = [[0, 0]] * n_barras

    # Datos de las barras para el gráfico de Plotly
    traces = []

    for i in range(n_barras + 1): # Agregué un valor adicional para incluir el final de la malla
        if i < n_barras: # Barras verticales
            traces.append(go.Scatter3d(
                x=x_coords[i:i+2],
                y=y_coords_vert[i*2:i*2+4],
                z=z_coords_vert[i*2:i*2+4],
                mode='lines',
                line=dict(color='green', width=2)
            ))

        if i < n_barras: # Conectores horizontales entre barras verticales
            traces.append(go.Scatter3d(
                x=[x_coords[i], x_coords[i+1]],
                y=y_coords_horz[i:i+2],
                z=z_coords_horz[i:i+2],
                mode='lines',
                line=dict(color='green', width=2)
            ))

    # Diseño del gráfico de Plotly
    layout = go.Layout(
        title='Malla de tierra',
        scene=dict(
            xaxis_title='Distancia (m)',
            yaxis_title='Profundidad (m)',
            zaxis_title='Altitud (m)'
        )
    )

    # Creación del gráfico de Plotly
    fig = go.Figure(data=traces, layout=layout)

    print("Fig antes de devolver:", fig)

    return fig'''


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import Delaunay

def generate_malla_tierra(I, R_des, sigma, rho, I_falla, L, A, n_barras):
    """
    Genera la malla de tierra y devuelve la figura con el gráfico.
    """
    # Crear la figura
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Crear la cuadrícula de la malla
    x = np.linspace(0, L, n_barras)  # Distribución uniforme de puntos
    y = np.linspace(0, L, n_barras)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)  # La malla está en el plano z=0
    
    # Dibujar las líneas de la malla
    for i in range(n_barras):
        # Líneas horizontales
        ax.plot(x, [y[i]]*len(x), np.zeros_like(x), 'b-', linewidth=2, 
                label='Conductores' if i == 0 else None)
        # Líneas verticales
        ax.plot([x[i]]*len(y), y, np.zeros_like(y), 'b-', linewidth=2)
    
    # Dibujar los nodos (intersecciones)
    ax.scatter(X.flatten(), Y.flatten(), Z.flatten(), 
                c='red', marker='o', s=100, label='Nodos de conexión')
    
    # Agregar una superficie semitransparente para mejor visualización
    ax.plot_surface(X, Y, Z, alpha=0.1, color='gray')
    
    # Configurar el gráfico
    ax.set_xlabel('Distancia (m)')
    ax.set_ylabel('Distancia (m)')
    ax.set_zlabel('Profundidad (m)')
    espaciamiento = L / (n_barras - 1) if n_barras > 1 else L
    title = f'Malla de Puesta a Tierra\n{n_barras}x{n_barras} nodos, {espaciamiento:.2f}m entre nodos'
    ax.set_title(title)
    
    # Ajustar límites y vista
    margin = L * 0.1
    ax.set_xlim(-margin, L + margin)
    ax.set_ylim(-margin, L + margin)
    ax.set_zlim(-margin, margin)
    ax.view_init(elev=30, azim=45)
    
    # Agregar leyenda y grid
    ax.legend(loc='upper right')
    ax.grid(True)
    
    return fig, ax
