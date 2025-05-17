from datetime import datetime
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import os

@dataclass
class VersionMalla:
    """Representa una versión del diseño de la malla"""
    id: str
    fecha: datetime
    descripcion: str
    parametros: Dict
    resultados: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'fecha': self.fecha.isoformat(),
            'descripcion': self.descripcion,
            'parametros': self.parametros,
            'resultados': self.resultados
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VersionMalla':
        return cls(
            id=data['id'],
            fecha=datetime.fromisoformat(data['fecha']),
            descripcion=data['descripcion'],
            parametros=data['parametros'],
            resultados=data.get('resultados')
        )

class HistorialDiseños:
    """Gestiona el historial de versiones de diseños de mallas"""
    def __init__(self, ruta_base: str = "reportes"):
        self.ruta_base = ruta_base
        self.ruta_historial = os.path.join(ruta_base, "historial")

    def _asegurar_directorio_proyecto(self, proyecto_id: str) -> str:
        """Crea y retorna la ruta del directorio del proyecto"""
        ruta_proyecto = os.path.join(self.ruta_historial, proyecto_id)
        os.makedirs(ruta_proyecto, exist_ok=True)
        return ruta_proyecto

    def guardar_version(self, proyecto_id: str, descripcion: str, parametros: Dict, resultados: Optional[Dict] = None) -> VersionMalla:
        """Guarda una nueva versión del diseño"""
        # Asegurar que el proyecto_id no está vacío
        if not proyecto_id:
            raise ValueError("El ID del proyecto no puede estar vacío")

        # Crear copia profunda de los datos
        parametros_copia = json.loads(json.dumps(parametros))
        resultados_copia = json.loads(json.dumps(resultados)) if resultados else None

        # Crear la versión con microsegundos para asegurar unicidad
        ahora = datetime.now()
        version = VersionMalla(
            id=ahora.strftime("%Y%m%d_%H%M%S_%f"),
            fecha=ahora,
            descripcion=descripcion,
            parametros=parametros_copia,
            resultados=resultados_copia
        )
        
        # Crear y verificar la estructura de directorios
        ruta_proyecto = self._asegurar_directorio_proyecto(proyecto_id)
        
        # Guardar el archivo
        ruta_version = os.path.join(ruta_proyecto, f"{version.id}.json")
        try:
            datos = version.to_dict()
            with open(ruta_version, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
            
            # Verificar que podemos leer el archivo
            with open(ruta_version, 'r', encoding='utf-8') as f:
                datos_leidos = json.load(f)
                version_leida = VersionMalla.from_dict(datos_leidos)
                if version_leida.id != version.id:
                    raise ValueError("Error en la verificación de la versión guardada")
                
            return version
        except Exception as e:
            # Si algo falla, intentar limpiar
            if os.path.exists(ruta_version):
                try:
                    os.remove(ruta_version)
                except:
                    pass
            raise OSError(f"Error al guardar la versión: {str(e)}")
            
    def obtener_versiones(self, proyecto_id: str) -> List[VersionMalla]:
        """Obtiene todas las versiones de un proyecto ordenadas por fecha"""
        ruta_proyecto = os.path.join(self.ruta_historial, proyecto_id)
        
        if not os.path.exists(ruta_proyecto):
            return []
        
        # Lista todas las versiones
        versiones = []
        archivos = [f for f in os.listdir(ruta_proyecto) if f.endswith('.json')]
        
        for archivo in archivos:
            try:
                ruta_version = os.path.join(ruta_proyecto, archivo)
                with open(ruta_version, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    version = VersionMalla.from_dict(data)
                    versiones.append(version)
            except Exception as e:
                # Si hay un error al leer una versión, la ignoramos
                print(f"Error al cargar versión {archivo}: {str(e)}")
                continue
        
        # Ordenar por fecha en orden descendente (más reciente primero)
        return sorted(versiones, key=lambda v: v.fecha, reverse=True)
        
    def obtener_version(self, proyecto_id: str, version_id: str) -> Optional[VersionMalla]:
        """Obtiene una versión específica de un proyecto"""
        ruta_version = os.path.join(self.ruta_historial, proyecto_id, f"{version_id}.json")
        if not os.path.exists(ruta_version):
            return None
            
        with open(ruta_version, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return VersionMalla.from_dict(data)
    
    def comparar_versiones(self, version1: VersionMalla, version2: VersionMalla) -> Dict:
        """Compara dos versiones y retorna las diferencias"""
        diferencias = {
            'parametros': {},
            'resultados': {}
        }
        
        def comparar_objetos(obj1, obj2, resultado):
            """Compara dos objetos de manera recursiva"""
            if isinstance(obj1, dict) and isinstance(obj2, dict):
                temp = {}
                keys = set(obj1.keys()) | set(obj2.keys())
                for key in keys:
                    val1 = obj1.get(key)
                    val2 = obj2.get(key)
                    if val1 != val2:
                        if isinstance(val1, dict) and isinstance(val2, dict):
                            temp[key] = comparar_objetos(val1, val2, {})
                        else:
                            temp[key] = {
                                'anterior': val1,
                                'actual': val2
                            }
                if temp:
                    resultado.update(temp)
            return resultado

        # Comparar parámetros
        comparar_objetos(version1.parametros, version2.parametros, diferencias['parametros'])

        # Comparar resultados si existen
        v1_resultados = version1.resultados or {}
        v2_resultados = version2.resultados or {}
        comparar_objetos(v1_resultados, v2_resultados, diferencias['resultados'])
            
        return diferencias
