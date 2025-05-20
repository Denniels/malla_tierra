import unittest
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')  # Usar backend no interactivo para matplotlib
os.environ['DISPLAY'] = ':99'  # Configurar display virtual
try:
    import pyvista as pv
    pv.OFF_SCREEN = True  # Configurar PyVista para modo no interactivo
except ImportError:
    pass

from malla import MallaTierra, Conductor, Varilla
from suelo import CapaSuelo
from visualizacion import (
    generar_vista_3d_multicapa,
    generar_mapa_calor,
    generar_perfil_suelo,
    calcular_potenciales_superficie
)

class TestVisualizacion(unittest.TestCase):
    def setUp(self):
        # Configurar una malla de prueba
        self.conductor = Conductor(
            material="Cobre",
            diametro=13.5,  # mm
            resistividad=1.72e-8,  # Ω⋅m
            capacidad_corriente=200,  # A
            temperatura_max=200  # °C
        )
        self.malla = MallaTierra(
            ancho=20,
            largo=20,
            espaciamiento=5,
            profundidad=0.5,
            conductor=self.conductor
        )
        
        # Agregar algunas varillas
        self.malla.agregar_varilla(Varilla(
            posicion_x=0,
            posicion_y=0,
            longitud=2.4,
            diametro=0.0159
        ))
        self.malla.agregar_varilla(Varilla(
            posicion_x=20,
            posicion_y=20,
            longitud=2.4,
            diametro=0.0159
        ))
        
        # Definir capas de suelo
        self.capas = [
            CapaSuelo(profundidad=0.5, resistividad=100),
            CapaSuelo(profundidad=2.0, resistividad=200),
            CapaSuelo(profundidad=4.0, resistividad=300)
        ]
        
        # Crear directorio para reportes si no existe
        os.makedirs("reportes", exist_ok=True)

    def test_generar_vista_3d_multicapa(self):
        """Prueba la generación de vista 3D de la malla"""
        # Primera prueba: visualización básica
        try:
            vista = generar_vista_3d_multicapa(
                self.malla,
                self.capas,
                mostrar_varillas=True,
                modo_test=True
            )
            self.assertIsNotNone(vista)
        except Exception as e:
            self.fail(f"La generación de vista 3D falló: {str(e)}")
        
        # Segunda prueba: con callback de progreso
        progreso_alcanzado = []
        def progress_callback(progress, message):
            progreso_alcanzado.append(progress)
        
        try:
            vista = generar_vista_3d_multicapa(
                self.malla,
                self.capas,
                mostrar_varillas=True,
                progress_callback=progress_callback,
                modo_test=True
            )
            self.assertIsNotNone(vista)
            self.assertTrue(len(progreso_alcanzado) > 0)
            self.assertGreaterEqual(max(progreso_alcanzado), 1.0)
        except Exception as e:
            self.fail(f"La generación de vista 3D con callback falló: {str(e)}")

    def test_generar_vista_3d_interactiva(self):
        """Prueba la generación de vista 3D interactiva con todas las opciones"""
        try:
            plotter = generar_vista_3d_multicapa(
                self.malla,
                self.capas,
                mostrar_varillas=True,
                mostrar_uniones=True,
                tipo_union="Soldadura exotérmica",
                mostrar_potenciales=True,
                modo_test=True
            )
            self.assertIsNotNone(plotter)
        except Exception as e:
            self.fail(f"La generación de vista 3D interactiva falló: {str(e)}")

    def test_calcular_potenciales_superficie(self):
        """Prueba el cálculo de potenciales en la superficie"""
        I_falla = 1000  # Amperios
        rho = 100  # Ohm-m
        
        potenciales = calcular_potenciales_superficie(self.malla, I_falla, rho)
        
        self.assertIsInstance(potenciales, np.ndarray)
        self.assertEqual(potenciales.shape, (100, 100))  # Verificar dimensiones
        self.assertTrue(np.all(potenciales >= 0))  # Los potenciales deben ser positivos

    def test_generar_mapa_calor(self):
        """Prueba la generación del mapa de calor"""
        I_falla = 1000
        rho = 100
        potenciales = calcular_potenciales_superficie(self.malla, I_falla, rho)
        
        fig, ax = generar_mapa_calor(I_falla, rho, self.malla, potenciales)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)

    def test_generar_perfil_suelo(self):
        """Prueba la generación del perfil del suelo"""
        rho = 100
        h = 0.5
        rho_s = 3000
        
        fig, ax = generar_perfil_suelo(self.malla, rho, h, rho_s)
        
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)

def run_tests():
    unittest.main(module=__name__, verbosity=2)

if __name__ == '__main__':
    run_tests()
