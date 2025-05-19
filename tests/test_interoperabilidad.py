import unittest
import os
import json
from tempfile import NamedTemporaryFile
from malla import MallaTierra, Conductor
from interoperabilidad import (
    ExportadorCAD,
    ImportadorMediciones,
    IntegracionSoftware,
    APIIntegracion
)

class TestInteroperabilidad(unittest.TestCase):
    def setUp(self):
        # Crear una malla de prueba
        conductor = Conductor.get_conductor_cobre(0.01)  # 10mm de diámetro
        self.malla = MallaTierra(
            ancho=10,
            largo=10,
            espaciamiento=5,
            conductor=conductor,
            profundidad=0.5
        )
        self.malla.agregar_varilla(x=0, y=0, longitud=3, diametro=0.016)
        self.malla.agregar_varilla(x=10, y=10, longitud=3, diametro=0.016)
    
    def test_exportar_dxf(self):
        """Prueba la exportación a formato DXF"""
        with NamedTemporaryFile(suffix='.dxf', delete=False) as temp:
            temp_path = temp.name
        
        try:
            # Exportar a DXF
            resultado = ExportadorCAD.exportar_dxf(self.malla, temp_path)
            self.assertTrue(resultado)
            
            # Verificar que el archivo existe y tiene contenido
            self.assertTrue(os.path.exists(temp_path))
            with open(temp_path, 'r') as f:
                contenido = f.read()
                self.assertIn('SECTION', contenido)
                self.assertIn('ENTITIES', contenido)
                self.assertIn('LINE', contenido)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_importar_mediciones(self):
        """Prueba la importación de mediciones desde CSV"""
        with NamedTemporaryFile(suffix='.csv', delete=False) as temp:
            temp.write(b"x,y,resistividad,observaciones\n")
            temp.write(b"0,0,100,punto1\n")
            temp.write(b"5,5,120,punto2\n")
            temp_path = temp.name
        
        try:
            datos = ImportadorMediciones.importar_csv(temp_path)
            self.assertEqual(len(datos['x']), 2)
            self.assertEqual(datos['resistividad'], [100.0, 120.0])
            self.assertEqual(datos['observaciones'], ['punto1', 'punto2'])
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_exportar_etap(self):
        """Prueba la exportación a formato ETAP (XML)"""
        with NamedTemporaryFile(suffix='.xml', delete=False) as temp:
            temp_path = temp.name
        
        try:
            resultado = IntegracionSoftware.exportar_etap(self.malla, temp_path)
            self.assertTrue(resultado)
            
            # Verificar que el archivo existe y tiene contenido
            self.assertTrue(os.path.exists(temp_path))
            with open(temp_path, 'r') as f:
                contenido = f.read()
                self.assertIn('<?xml', contenido)
                self.assertIn('<MallaTierra>', contenido)
                self.assertIn('<DatosGenerales>', contenido)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_api_json(self):
        """Prueba la generación y carga de JSON a través de la API"""
        # Generar JSON
        json_data = APIIntegracion.generar_json(self.malla)
        self.assertIsInstance(json_data, str)
        
        # Validar estructura JSON
        data = json.loads(json_data)
        self.assertEqual(data['tipo'], 'malla_tierra')
        self.assertEqual(data['parametros']['ancho'], 10)
        self.assertEqual(len(data['parametros']['varillas']), 2)
        
        # Cargar JSON
        nueva_malla = APIIntegracion.cargar_json(json_data)
        self.assertIsNotNone(nueva_malla)
        self.assertEqual(nueva_malla.ancho, self.malla.ancho)
        self.assertEqual(nueva_malla.largo, self.malla.largo)
        self.assertEqual(len(nueva_malla.varillas), len(self.malla.varillas))

if __name__ == '__main__':
    unittest.main()
