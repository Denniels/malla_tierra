# -*- coding: utf-8 -*-
"""
Módulo para manejar diferentes tipos de mallas de tierra
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np

@dataclass
class Conductor:
    """Clase para representar un conductor"""
    diametro: float  # mm
    material: str
    resistividad: float  # Ω⋅m
    capacidad_corriente: float  # A
    temperatura_max: float  # °C
    
    @classmethod
    def get_conductor_cobre(cls, diametro=10.0):
        """Crea un conductor de cobre con valores típicos"""
        return cls(
            diametro=diametro,
            material="Cobre",
            resistividad=1.72e-8,
            capacidad_corriente=200,
            temperatura_max=200
        )
    
    @classmethod
    def get_conductor_acero(cls, diametro=10.0):
        """Crea un conductor de acero con valores típicos"""
        return cls(
            diametro=diametro,
            material="Acero Galvanizado",
            resistividad=11.2e-8,
            capacidad_corriente=150,
            temperatura_max=180
        )

@dataclass
class Varilla:
    """Clase para representar una varilla vertical"""
    longitud: float  # m
    diametro: float  # mm
    posicion_x: float  # m
    posicion_y: float  # m
    material: str = "Cobre"

class MallaTierra:
    """Clase para representar una malla de tierra completa"""
    def __init__(
        self,
        ancho: float,
        largo: float,
        espaciamiento: float,
        conductor: Optional[Conductor] = None,
        profundidad: float = 0.5,
        varillas: Optional[List[Varilla]] = None
    ):
        self.ancho = ancho
        self.largo = largo
        self.espaciamiento = espaciamiento
        self.conductor = conductor or Conductor.get_conductor_cobre()
        self.profundidad = profundidad
        self.varillas = varillas or []
        
        # Calcular número de conductores
        self.n_x = max(round(ancho / espaciamiento) + 1, 3)
        self.n_y = max(round(largo / espaciamiento) + 1, 3)
        
        # Asegurar números impares para centrar la malla
        if self.n_x % 2 == 0: self.n_x += 1
        if self.n_y % 2 == 0: self.n_y += 1
        
        # Recalcular espaciamientos reales
        self.espaciamiento_x = ancho / (self.n_x - 1)
        self.espaciamiento_y = largo / (self.n_y - 1)
    
    def agregar_varilla(self, x: float, y: float, longitud: float = 2.4, diametro: float = 16.0):
        """Agrega una varilla vertical a la malla"""
        # Validar que la posición esté dentro de la malla
        if not (0 <= x <= self.ancho and 0 <= y <= self.largo):
            raise ValueError("La posición de la varilla debe estar dentro de los límites de la malla")
        
        varilla = Varilla(
            longitud=longitud,
            diametro=diametro,
            posicion_x=x,
            posicion_y=y
        )
        self.varillas.append(varilla)
    
    def obtener_nodos(self) -> Tuple[np.ndarray, np.ndarray]:
        """Obtiene las coordenadas de todos los nodos de la malla"""
        x = np.linspace(0, self.ancho, self.n_x)
        y = np.linspace(0, self.largo, self.n_y)
        return np.meshgrid(x, y)
    
    def obtener_varillas(self) -> List[Tuple[float, float, float]]:
        """Obtiene las coordenadas y longitudes de todas las varillas"""
        return [(v.posicion_x, v.posicion_y, v.longitud) for v in self.varillas]
    
    def calcular_longitud_total(self) -> float:
        """Calcula la longitud total de conductores"""
        # Longitud de conductores horizontales y verticales
        l_horizontal = self.ancho * self.n_y
        l_vertical = self.largo * self.n_x
        
        # Longitud de varillas verticales
        l_varillas = sum(v.longitud for v in self.varillas)
        
        return l_horizontal + l_vertical + l_varillas
    
    def tiene_obstaculo(self, x: float, y: float) -> bool:
        """
        Verifica si hay un obstáculo en la posición dada.
        A implementar según necesidades específicas.
        """
        # Por ahora retorna False, pero se puede extender para manejar obstáculos
        return False
