import unittest
from datetime import datetime
import os
import shutil
from malla import Conductor, MallaTierra
from proyecto import ProyectoMallaTierra
from historial import HistorialDiseños, VersionMalla

class TestHistorialDiseños(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.ruta_test = "test_results"
        os.makedirs(self.ruta_test, exist_ok=True)
        self.historial = HistorialDiseños(self.ruta_test)
        self.proyecto_id = "test_proyecto"
        self.parametros_prueba = {
            "ancho": 20.0,
            "largo": 30.0,
            "profundidad": 0.5,
            "resistividad": 100.0,
            "conductor": {
                "tipo": "cobre",
                "seccion": 70.0
            }
        }

    def tearDown(self):
        """Limpieza después de cada prueba"""
        if os.path.exists(self.ruta_test):
            shutil.rmtree(self.ruta_test)

    def test_guardar_version(self):
        """Prueba el guardado de una nueva versión"""
        version = self.historial.guardar_version(
            self.proyecto_id,
            "Versión inicial",
            self.parametros_prueba
        )
        self.assertIsNotNone(version)
        self.assertEqual(version.descripcion, "Versión inicial")
        self.assertEqual(version.parametros, self.parametros_prueba)
        
        # Verificar que el archivo se creó correctamente
        ruta_version = os.path.join(
            self.ruta_test, 
            "historial", 
            self.proyecto_id, 
            f"{version.id}.json"
        )
        self.assertTrue(os.path.exists(ruta_version))

    def test_obtener_versiones(self):
        """Prueba la obtención de versiones guardadas"""
        # Guardar primera versión
        version1 = self.historial.guardar_version(
            self.proyecto_id,
            "Versión inicial",
            self.parametros_prueba.copy()
        )
        
        # Verificar que se guardó
        ruta_version1 = os.path.join(
            self.ruta_test,
            "historial",
            self.proyecto_id,
            f"{version1.id}.json"
        )
        self.assertTrue(os.path.exists(ruta_version1))
        
        # Esperar un momento para asegurar diferentes timestamps
        import time
        time.sleep(0.1)
        
        # Guardar segunda versión
        parametros2 = self.parametros_prueba.copy()
        parametros2["ancho"] = 25.0
        version2 = self.historial.guardar_version(
            self.proyecto_id,
            "Segunda versión",
            parametros2
        )
        
        # Verificar que se guardó
        ruta_version2 = os.path.join(
            self.ruta_test,
            "historial",
            self.proyecto_id,
            f"{version2.id}.json"
        )
        self.assertTrue(os.path.exists(ruta_version2))
        
        # Verificar directorio del proyecto
        ruta_proyecto = os.path.join(self.ruta_test, "historial", self.proyecto_id)
        archivos = [f for f in os.listdir(ruta_proyecto) if f.endswith('.json')]
        self.assertEqual(len(archivos), 2, f"Se esperaban 2 archivos pero se encontraron {len(archivos)}: {archivos}")
        
        # Obtener todas las versiones
        versiones = self.historial.obtener_versiones(self.proyecto_id)
        self.assertEqual(len(versiones), 2, f"Se esperaban 2 versiones pero se obtuvieron {len(versiones)}")
        self.assertEqual(versiones[0].id, version2.id)  # La más reciente primero
        
        # Verificar ordenamiento por fecha
        self.assertTrue(versiones[0].fecha > versiones[1].fecha)

    def test_obtener_version_especifica(self):
        """Prueba la obtención de una versión específica"""
        # Guardar versión
        version_original = self.historial.guardar_version(
            self.proyecto_id,
            "Versión específica",
            self.parametros_prueba
        )
        
        # Obtener la versión
        version_recuperada = self.historial.obtener_version(
            self.proyecto_id,
            version_original.id
        )
        
        self.assertIsNotNone(version_recuperada)
        self.assertEqual(version_original.id, version_recuperada.id)
        self.assertEqual(version_original.parametros, version_recuperada.parametros)

    def test_comparar_versiones(self):
        """Prueba la comparación entre versiones"""
        # Versión base
        version1 = self.historial.guardar_version(
            self.proyecto_id,
            "Versión base",
            self.parametros_prueba
        )
        
        # Versión modificada
        parametros2 = self.parametros_prueba.copy()
        parametros2["ancho"] = 25.0
        parametros2["conductor"]["seccion"] = 95.0
        version2 = self.historial.guardar_version(
            self.proyecto_id,
            "Versión modificada",
            parametros2,
            resultados={"resistencia": 1.5}
        )
        
        # Comparar
        diferencias = self.historial.comparar_versiones(version1, version2)
        
        # Verificar diferencias en parámetros básicos
        self.assertIn("parametros", diferencias)
        self.assertIn("ancho", diferencias["parametros"])
        self.assertEqual(diferencias["parametros"]["ancho"], {
            'anterior': 20.0,
            'actual': 25.0
        })
        
        # Verificar diferencias en conductor
        self.assertIn("conductor", diferencias["parametros"])
        self.assertIn("seccion", diferencias["parametros"]["conductor"])
        self.assertEqual(diferencias["parametros"]["conductor"]["seccion"], {
            'anterior': 70.0,
            'actual': 95.0
        })
        
        # Verificar que el tipo de conductor no cambió
        self.assertNotIn("tipo", diferencias["parametros"]["conductor"])

        # Verificar diferencias en resultados
        self.assertIn("resultados", diferencias)
        self.assertIn("resistencia", diferencias["resultados"])
        self.assertEqual(diferencias["resultados"]["resistencia"], {
            'anterior': None,
            'actual': 1.5
        })

class TestProyectoMallaTierra(unittest.TestCase):
    def setUp(self):
        """Configuración inicial"""
        self.ruta_test = "test_results"
        os.makedirs(self.ruta_test, exist_ok=True)
        
        self.proyecto = ProyectoMallaTierra(
            nombre="test_proyecto",
            descripcion="Proyecto de prueba",
            ruta_historial=self.ruta_test
        )
        self.conductor = Conductor.get_conductor_cobre(10.0)
        
        # Configurar parámetros iniciales
        self.proyecto.actualizar_parametros(
            ancho=20.0,
            largo=30.0,
            profundidad=0.5,
            resistividad=100.0,
            conductor={
                "tipo": "cobre",
                "seccion": 70.0
            }
        )

    def tearDown(self):
        """Limpieza después de cada prueba"""
        if os.path.exists(self.ruta_test):
            shutil.rmtree(self.ruta_test)

    def test_manejo_historial(self):
        """Prueba la integración del historial con el proyecto"""
        # Guardar versión inicial
        version1 = self.proyecto.guardar_version("Versión inicial")
        self.assertIsNotNone(version1)
        self.assertEqual(version1.parametros["ancho"], 20.0)
        
        # Verificar que se guardó el archivo
        ruta_version1 = os.path.join(
            self.ruta_test,
            "historial",
            self.proyecto.nombre,
            f"{version1.id}.json"
        )
        self.assertTrue(os.path.exists(ruta_version1))
        
        # Esperar un momento para asegurar diferentes timestamps
        import time
        time.sleep(0.1)
        
        # Modificar parámetros y guardar nueva versión
        self.proyecto.actualizar_parametros(
            ancho=25.0,
            largo=35.0
        )
        version2 = self.proyecto.guardar_version("Cambio de dimensiones")
        
        # Verificar que se guardó el archivo
        ruta_version2 = os.path.join(
            self.ruta_test,
            "historial",
            self.proyecto.nombre,
            f"{version2.id}.json"
        )
        self.assertTrue(os.path.exists(ruta_version2))
        
        # Obtener versiones
        versiones = self.proyecto.obtener_versiones()
        self.assertEqual(len(versiones), 2)
        self.assertEqual(versiones[0].id, version2.id)  # La más reciente primero
          # Cargar versión anterior
        self.assertTrue(self.proyecto.cargar_version(version1.id))
        self.assertEqual(self.proyecto.parametros["ancho"], 20.0)
        self.assertEqual(self.proyecto.parametros["largo"], 30.0)
        
        # Comparar con la versión más reciente
        diferencias = self.proyecto.comparar_con_version(version2.id)
        self.assertIn("parametros", diferencias)
        
        # Verificar diferencias en ancho (anterior=version1, actual=version2)
        self.assertIn("ancho", diferencias["parametros"])
        self.assertEqual(
            diferencias["parametros"]["ancho"]["anterior"],
            20.0,  # Valor en version1
            "El valor anterior debe ser el de la versión 1 (20.0)"
        )
        self.assertEqual(
            diferencias["parametros"]["ancho"]["actual"],
            25.0,  # Valor en version2
            "El valor actual debe ser el de la versión 2 (25.0)"
        )
        
        # Verificar diferencias en largo (anterior=version1, actual=version2)
        self.assertIn("largo", diferencias["parametros"])
        self.assertEqual(
            diferencias["parametros"]["largo"]["anterior"],
            30.0,  # Valor en version1
            "El valor anterior debe ser el de la versión 1 (30.0)"
        )
        self.assertEqual(
            diferencias["parametros"]["largo"]["actual"],
            35.0,  # Valor en version2
            "El valor actual debe ser el de la versión 2 (35.0)"
        )

    def test_manejo_errores_historial(self):
        """Prueba el manejo de errores en operaciones del historial"""
        # Intento de cargar versión inexistente
        self.assertFalse(
            self.proyecto.cargar_version("version_inexistente")
        )
        
        # Intento de comparar con versión inexistente
        diferencias = self.proyecto.comparar_con_version("version_inexistente")
        self.assertEqual(diferencias, {
            'parametros': {},
            'resultados': {}
        })
        
        # Versión sin resultados
        version = self.proyecto.guardar_version("Sin resultados")
        diferencias = self.proyecto.comparar_con_version(version.id)
        self.assertIn("parametros", diferencias)

if __name__ == '__main__':
    unittest.main()
