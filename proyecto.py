from typing import Dict, Any, Optional, List
import json
import os
from datetime import datetime
from dataclasses import asdict
from historial import HistorialDiseños, VersionMalla

class ProyectoMallaTierra:
    """Clase para manejar el guardado y carga de proyectos de malla de tierra"""
    
    def __init__(self, nombre: str, descripcion: str = ""):
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_creacion = datetime.now()
        self.fecha_modificacion = self.fecha_creacion
        self.parametros: Dict[str, Any] = {}
        self.resultados: Dict[str, Any] = {}
        self.configuracion: Dict[str, Any] = {}
        self._historial = HistorialDiseños()
        self.version_actual: Optional[VersionMalla] = None
    
    def guardar(self, ruta: str) -> str:
        """Guarda el proyecto en formato JSON"""
        self.fecha_modificacion = datetime.now()
        datos = {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "fecha_creacion": self.fecha_creacion.isoformat(),
            "fecha_modificacion": self.fecha_modificacion.isoformat(),
            "parametros": self.parametros,
            "resultados": self.resultados,
            "configuracion": self.configuracion
        }
        
        # Asegurar que existe el directorio
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        
        return ruta
    
    @classmethod
    def cargar(cls, ruta: str) -> 'ProyectoMallaTierra':
        """Carga un proyecto desde un archivo JSON"""
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        proyecto = cls(datos["nombre"], datos["descripcion"])
        proyecto.fecha_creacion = datetime.fromisoformat(datos["fecha_creacion"])
        proyecto.fecha_modificacion = datetime.fromisoformat(datos["fecha_modificacion"])
        proyecto.parametros = datos["parametros"]
        proyecto.resultados = datos["resultados"]
        proyecto.configuracion = datos["configuracion"]
        
        return proyecto
    
    def actualizar_parametros(self, **kwargs):
        """Actualiza los parámetros del proyecto"""
        self.parametros.update(kwargs)
        self.fecha_modificacion = datetime.now()
    
    def actualizar_resultados(self, **kwargs):
        """Actualiza los resultados del proyecto"""
        self.resultados.update(kwargs)
        self.fecha_modificacion = datetime.now()
    
    def guardar_version(self, descripcion: str) -> VersionMalla:
        """Guarda una nueva versión del diseño actual"""
        version = self._historial.guardar_version(
            proyecto_id=self.nombre,
            descripcion=descripcion,
            parametros=self.parametros,
            resultados=self.resultados
        )
        self.version_actual = version
        return version
    
    def obtener_versiones(self) -> List[VersionMalla]:
        """Obtiene todas las versiones del proyecto"""
        return self._historial.obtener_versiones(self.nombre)
    
    def cargar_version(self, version_id: str) -> bool:
        """Carga una versión específica del proyecto"""
        version = self._historial.obtener_version(self.nombre, version_id)
        if version:
            self.parametros = version.parametros.copy()
            if version.resultados:
                self.resultados = version.resultados.copy()
            self.version_actual = version
            self.fecha_modificacion = datetime.now()
            return True
        return False
    
    def comparar_con_version(self, version_id: str) -> Dict:
        """Compara la versión actual con una versión específica"""
        version = self._historial.obtener_version(self.nombre, version_id)
        if version and self.version_actual:
            return self._historial.comparar_versiones(version, self.version_actual)
        return {}
