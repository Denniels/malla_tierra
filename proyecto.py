from typing import Dict, Any, Optional, List
import json
import os
from datetime import datetime
from dataclasses import asdict
from historial import HistorialDiseños, VersionMalla

class ProyectoMallaTierra:
    """Clase para manejar el guardado y carga de proyectos de malla de tierra"""
    
    def __init__(self, nombre: str, descripcion: str = "", ruta_historial: str = "reportes"):
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_creacion = datetime.now()
        self.fecha_modificacion = self.fecha_creacion
        self.parametros: Dict[str, Any] = {}
        self.resultados: Dict[str, Any] = {}
        self.configuracion: Dict[str, Any] = {}
        self._historial = HistorialDiseños(ruta_historial)
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
    def cargar(cls, ruta: str, ruta_historial: str = "reportes") -> 'ProyectoMallaTierra':
        """Carga un proyecto desde un archivo JSON"""
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        proyecto = cls(datos["nombre"], datos["descripcion"], ruta_historial)
        proyecto.fecha_creacion = datetime.fromisoformat(datos["fecha_creacion"])
        proyecto.fecha_modificacion = datetime.fromisoformat(datos["fecha_modificacion"])
        proyecto.parametros = datos["parametros"]
        proyecto.resultados = datos["resultados"]
        proyecto.configuracion = datos["configuracion"]
        
        return proyecto
    
    def guardar_version(self, descripcion: str) -> VersionMalla:
        """Guarda una nueva versión del diseño actual"""
        # Crear una copia del estado actual
        version = self._historial.guardar_version(
            proyecto_id=self.nombre,
            descripcion=descripcion,
            parametros=self.parametros.copy(),
            resultados=self.resultados.copy() if self.resultados else None
        )

        # Actualizar estado interno
        self.version_actual = version
        self.fecha_modificacion = datetime.now()
        return version
    
    def obtener_versiones(self) -> List[VersionMalla]:
        """Obtiene todas las versiones del proyecto"""
        return self._historial.obtener_versiones(self.nombre)
    
    def cargar_version(self, version_id: str) -> bool:
        """Carga una versión específica del proyecto"""
        version = self._historial.obtener_version(self.nombre, version_id)
        if not version:
            return False

        # Actualizar el estado del proyecto con la versión cargada
        self.parametros = version.parametros.copy()
        if version.resultados:
            self.resultados = version.resultados.copy()
        self.fecha_modificacion = datetime.now()
        self.version_actual = version
        return True
    
    def actualizar_parametros(self, **kwargs):
        """Actualiza los parámetros del proyecto"""
        # Guardar los cambios
        self.parametros.update(kwargs)
        self.fecha_modificacion = datetime.now()
        # Limpiar la versión actual ya que hemos modificado los parámetros
        self.version_actual = None

    def actualizar_resultados(self, **kwargs):
        """Actualiza los resultados del proyecto"""
        # Guardar los cambios
        self.resultados.update(kwargs)
        self.fecha_modificacion = datetime.now()
        # Limpiar la versión actual ya que hemos modificado los resultados
        self.version_actual = None
    
    def comparar_con_version(self, version_id: str) -> Dict:
        """Compara una versión específica con la versión actual"""
        version_objetivo = self._historial.obtener_version(self.nombre, version_id)
        if not version_objetivo:
            return {
                'parametros': {},
                'resultados': {}
            }        # Crear una versión actual temporal para la comparación
        estado_actual = VersionMalla(
            id=datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            fecha=datetime.now(),
            descripcion="Estado actual",
            parametros=self.parametros.copy(),
            resultados=self.resultados.copy() if self.resultados else None
        )
        
        # Comparar las versiones - la versión actual es la que está cargada en el proyecto
        return self._historial.comparar_versiones(estado_actual, version_objetivo)
