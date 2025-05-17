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
        os.makedirs(self.ruta_historial, exist_ok=True)
        
    def guardar_version(self, proyecto_id: str, descripcion: str, parametros: Dict, resultados: Optional[Dict] = None) -> VersionMalla:
        """Guarda una nueva versión del diseño"""
        version = VersionMalla(
            id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            fecha=datetime.now(),
            descripcion=descripcion,
            parametros=parametros,
            resultados=resultados
        )
        
        ruta_proyecto = os.path.join(self.ruta_historial, proyecto_id)
        os.makedirs(ruta_proyecto, exist_ok=True)
        
        ruta_version = os.path.join(ruta_proyecto, f"{version.id}.json")
        with open(ruta_version, 'w', encoding='utf-8') as f:
            json.dump(version.to_dict(), f, ensure_ascii=False, indent=2)
            
        return version
    
    def obtener_versiones(self, proyecto_id: str) -> List[VersionMalla]:
        """Obtiene todas las versiones de un proyecto ordenadas por fecha"""
        ruta_proyecto = os.path.join(self.ruta_historial, proyecto_id)
        if not os.path.exists(ruta_proyecto):
            return []
            
        versiones = []
        for archivo in os.listdir(ruta_proyecto):
            if archivo.endswith('.json'):
                ruta_version = os.path.join(ruta_proyecto, archivo)
                with open(ruta_version, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    versiones.append(VersionMalla.from_dict(data))
                    
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
        
        # Comparar parámetros
        for key in set(version1.parametros.keys()) | set(version2.parametros.keys()):
            val1 = version1.parametros.get(key)
            val2 = version2.parametros.get(key)
            if val1 != val2:
                diferencias['parametros'][key] = {
                    'anterior': val1,
                    'actual': val2
                }
        
        # Comparar resultados si existen
        if version1.resultados and version2.resultados:
            for key in set(version1.resultados.keys()) | set(version2.resultados.keys()):
                val1 = version1.resultados.get(key)
                val2 = version2.resultados.get(key)
                if val1 != val2:
                    diferencias['resultados'][key] = {
                        'anterior': val1,
                        'actual': val2
                    }
                    
        return diferencias
