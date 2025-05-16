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

'''def generate_malla_tierra(I, R_des, sigma, rho, I_falla, L, A, n_barras):
    # Coordenadas para las barras verticales y conectores horizontales
    x_coords_vert = np.arange(0, L + 100 * n_barras, 100)[:-1]  # Agregué un valor adicional para incluir el final de la malla
    y_coords_vert = -A * np.repeat(1, len(x_coords_vert))
    z_coords_vert = A * np.repeat(1, len(x_coords_vert))

    x_connectors = np.concatenate([x_coords_vert, x_coords_vert[-1] + np.array([100 * i for i in range(n_barras)])])
    y_connectors = -A * np.concatenate([np.ones(len(x_coords_vert)), np.repeat(-2 * A, n_barras)])
    z_connectors = A * np.concatenate([np.repeat(1, len(x_coords_vert)), np.arange(-n_barras + 1, n_barras)])

    # Coordenadas para los nodos
    x_nodes = np.concatenate([x_coords_vert, x_connectors])
    y_nodes = -A * np.repeat(1, len(x_nodes))
    z_nodes = A * np.repeat(1, len(x_nodes))

    # Escalar las coordenadas para manejar mejor los datos con Qhull
    scale_factor = 1.0 / (np.linalg.norm(np.column_stack((x_nodes, y_nodes, z_nodes)), axis=1).max() + 1e-6)
    x_nodes_scaled = x_nodes * scale_factor
    y_nodes_scaled = y_nodes * scale_factor
    z_nodes_scaled = z_nodes * scale_factor

    return x_nodes_scaled, y_nodes_scaled, z_nodes_scaled

def plot_malla_tierra(I, R_des, sigma, rho, I_falla, L, A, n_barras):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Generar la malla
    x_nodes, y_nodes, z_nodes = generate_malla_tierra(I, R_des, sigma, rho, I_falla, L, A, n_barras)

    # Triangulación de Delaunay para los nodos
    points = np.column_stack((x_nodes, y_nodes, z_nodes))
    tri = Delaunay(points)
    triangles = tri.simplices

    # Graficar la superficie triangular de la malla
    ax.plot_trisurf(x_nodes[triangles], y_nodes[triangles], z_nodes[triangles], color='gray', alpha=0.8, label='Malla de tierra')

    # Configuración del gráfico
    ax.set_xlabel('Distancia (m)')
    ax.set_ylabel('Profundidad (m)')
    ax.set_zlabel('Altitud (m)')
    ax.set_title('Malla de tierra')
    ax.legend()

    return fig, ax'''
    
import numpy as np
from scipy.spatial import Delaunay

def generate_regular_grid(L, A, n_barras):
    """
    Genera una malla regular en 2D para la representación gráfica de la tierra.
    """
    # Coordenadas para las barras verticales y conectores horizontales
    x_coords_vert = np.arange(0, L + 100 * n_barras, 100)[:-1]  # Agregué un valor adicional para incluir el final de la malla
    y_coords_vert = -A * np.repeat(1, len(x_coords_vert))
    z_coords_vert = A * np.repeat(1, len(x_coords_vert))

    x_connectors = np.concatenate([x_coords_vert, x_coords_vert[-1] + np.array([100 * i for i in range(n_barras)])])
    y_connectors = -A * np.concatenate([np.ones(len(x_coords_vert)), np.repeat(-2 * A, n_barras)])
    z_connectors = A * np.concatenate([np.zeros(len(x_coords_vert)), 0.71 * np.ones(n_barras)])

    # Coordenadas para los nodos de la malla
    x_nodes = np.concatenate((x_coords_vert, x_connectors))
    y_nodes = np.concatenate((y_coords_vert, y_connectors))
    z_nodes = np.concatenate((z_coords_vert, z_connectors))

    return x_nodes, y_nodes, z_nodes

def generate_malla_tierra(I, R_des, sigma, rho, I_falla, L, A, n_barras):
    """
    Genera la malla de tierra utilizando una triangulación de Delaunay.
    """
    # Generar la malla
    x_nodes, y_nodes, z_nodes = generate_regular_grid(L, A, n_barras)

    # Triangulación de Delaunay para los nodos con opciones adicionales en Qhull
    points = np.column_stack((x_nodes, y_nodes, z_nodes))
    tri = Delaunay(points, qhull_options="QJ QR0")  # Agregué las opciones 'QJ' y 'QR0'
    triangles = tri.simplices

    return x_nodes, y_nodes, z_nodes, triangles
