"""
Módulo para manejo y conversión de unidades en la aplicación
"""
from typing import Dict, Any, Tuple
from enum import Enum
from dataclasses import dataclass

class SistemaUnidades(Enum):
    """Sistemas de unidades soportados"""
    METRICO = "Métrico (SI)"
    IMPERIAL = "Imperial"
    HIBRIDO = "Híbrido (común en industria)"

@dataclass
class UnidadMedida:
    """Representa una unidad de medida con sus factores de conversión"""
    nombre: str
    simbolo: str
    factor_a_si: float
    factor_desde_si: float = None
    
    def __post_init__(self):
        if self.factor_desde_si is None:
            self.factor_desde_si = 1/self.factor_a_si

class UnidadesMallaTierra:
    """Clase para manejar las unidades en el sistema de malla de tierra"""
    
    def __init__(self, sistema: SistemaUnidades = SistemaUnidades.METRICO):
        self.sistema = sistema
        self._definir_unidades()
        
    def _definir_unidades(self):
        """Define las unidades disponibles para cada sistema"""
        self.unidades = {
            "longitud": {
                SistemaUnidades.METRICO: UnidadMedida("metro", "m", 1.0),
                SistemaUnidades.IMPERIAL: UnidadMedida("pie", "ft", 0.3048),
                SistemaUnidades.HIBRIDO: UnidadMedida("metro", "m", 1.0)
            },
            "area": {
                SistemaUnidades.METRICO: UnidadMedida("metro cuadrado", "m²", 1.0),
                SistemaUnidades.IMPERIAL: UnidadMedida("pie cuadrado", "ft²", 0.092903),
                SistemaUnidades.HIBRIDO: UnidadMedida("metro cuadrado", "m²", 1.0)
            },
            "resistividad": {
                SistemaUnidades.METRICO: UnidadMedida("ohm-metro", "Ω⋅m", 1.0),
                SistemaUnidades.IMPERIAL: UnidadMedida("ohm-pie", "Ω⋅ft", 0.3048),
                SistemaUnidades.HIBRIDO: UnidadMedida("ohm-metro", "Ω⋅m", 1.0)
            },
            "corriente": {
                SistemaUnidades.METRICO: UnidadMedida("amperio", "A", 1.0),
                SistemaUnidades.IMPERIAL: UnidadMedida("amperio", "A", 1.0),
                SistemaUnidades.HIBRIDO: UnidadMedida("amperio", "A", 1.0)
            },
            "temperatura": {
                SistemaUnidades.METRICO: UnidadMedida("Celsius", "°C", 1.0),
                SistemaUnidades.IMPERIAL: UnidadMedida("Fahrenheit", "°F", 5/9),
                SistemaUnidades.HIBRIDO: UnidadMedida("Celsius", "°C", 1.0)
            },
            "diametro": {
                SistemaUnidades.METRICO: UnidadMedida("milímetro", "mm", 0.001),
                SistemaUnidades.IMPERIAL: UnidadMedida("pulgada", "in", 0.0254),
                SistemaUnidades.HIBRIDO: UnidadMedida("milímetro", "mm", 0.001)
            }
        }
    
    def convertir(self, valor: float, tipo: str, desde: SistemaUnidades, hacia: SistemaUnidades) -> Tuple[float, str]:
        """
        Convierte un valor entre sistemas de unidades
        
        Args:
            valor: Valor a convertir
            tipo: Tipo de medida (longitud, area, etc.)
            desde: Sistema de unidades origen
            hacia: Sistema de unidades destino
            
        Returns:
            Tuple con el valor convertido y el símbolo de la unidad
        """
        if desde == hacia:
            return valor, self.unidades[tipo][hacia].simbolo
            
        # Convertir a SI
        valor_si = valor * self.unidades[tipo][desde].factor_a_si
        
        # Convertir desde SI al sistema destino
        valor_convertido = valor_si * self.unidades[tipo][hacia].factor_desde_si
        
        return valor_convertido, self.unidades[tipo][hacia].simbolo
    
    def obtener_simbolo(self, tipo: str) -> str:
        """Obtiene el símbolo de la unidad actual para un tipo de medida"""
        return self.unidades[tipo][self.sistema].simbolo
    
    def obtener_factor(self, tipo: str) -> float:
        """Obtiene el factor de conversión a SI para un tipo de medida"""
        return self.unidades[tipo][self.sistema].factor_a_si
