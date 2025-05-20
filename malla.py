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
        varillas: Optional[List[Varilla]] = None,
        agregar_varillas_perimetro: bool = True
    ):
        # Validar parámetros de entrada
        if ancho <= 0 or largo <= 0:
            raise ValueError("El ancho y largo de la malla deben ser positivos")
        if espaciamiento <= 0:
            raise ValueError("El espaciamiento debe ser positivo")
        if profundidad <= 0:
            raise ValueError("La profundidad debe ser positiva")
            
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
        
        # Agregar varillas en el perímetro si se solicita
        if agregar_varillas_perimetro:
            self._agregar_varillas_perimetro()
            
    def _agregar_varillas_perimetro(self):
        """Agrega varillas en el perímetro de la malla para mejor disipación"""
        # Esquinas
        for x in [0, self.ancho]:
            for y in [0, self.largo]:
                self.agregar_varilla(x, y, longitud=3.0)  # Varillas más largas en las esquinas
        
        # Lados (cada 5 metros o menos)
        spacing_varillas = min(5.0, self.ancho/4)
        
        # Lado inferior y superior
        for x in np.arange(spacing_varillas, self.ancho-0.1, spacing_varillas):
            self.agregar_varilla(x, 0)
            self.agregar_varilla(x, self.largo)
            
        # Lado izquierdo y derecho
        for y in np.arange(spacing_varillas, self.largo-0.1, spacing_varillas):
            self.agregar_varilla(0, y)
            self.agregar_varilla(self.ancho, y)
    
    def validar_posicion(self, x: float, y: float) -> bool:
        """
        Valida si una posición está dentro de los límites de la malla
        y no interfiere con otras varillas
        
        Args:
            x: Coordenada x de la posición a validar
            y: Coordenada y de la posición a validar
            
        Returns:
            bool: True si la posición es válida, False en caso contrario
        """
        # Verificar límites - incluir el perímetro (0 y dimensión máxima son válidos)
        if x < 0 or x > self.ancho or y < 0 or y > self.largo:
            return False
            
        # Si es una posición en el perímetro, siempre es válida
        if x in (0, self.ancho) or y in (0, self.largo):
            return True
            
        # Para posiciones interiores, verificar que coincida con los nodos de la malla
        x_nodos = np.linspace(0, self.ancho, self.n_x)
        y_nodos = np.linspace(0, self.largo, self.n_y)
        
        # Tolerancia para comparación de flotantes
        tolerancia = 0.001
        
        # Verificar si la posición coincide con algún nodo
        x_valida = any(abs(x - x_nodo) < tolerancia for x_nodo in x_nodos)
        y_valida = any(abs(y - y_nodo) < tolerancia for y_nodo in y_nodos)
        
        if not (x_valida and y_valida):
            return False
        
        # Verificar distancia mínima con otras varillas
        for varilla in self.varillas:
            dx = abs(varilla.posicion_x - x)
            dy = abs(varilla.posicion_y - y)
            if dx == 0 and dy == 0:  # Misma posición que una varilla existente
                return False
            if max(dx, dy) < self.espaciamiento * 0.5:  # distancia mínima
                return False
        
        return True
    
    def agregar_varilla(self, x_o_varilla, y=None, longitud=2.4, diametro=16.0):
        """
        Agrega una varilla vertical a la malla.
        
        Args:
            x_o_varilla: Puede ser la coordenada x (float) o un objeto Varilla
            y: Coordenada y (opcional si x_o_varilla es un objeto Varilla)
            longitud: Longitud de la varilla en metros (opcional)
            diametro: Diámetro de la varilla en mm (opcional)
        """
        if isinstance(x_o_varilla, Varilla):
            varilla = x_o_varilla
            if not self.validar_posicion(varilla.posicion_x, varilla.posicion_y):
                raise ValueError(f"Posición inválida para la varilla: ({varilla.posicion_x}, {varilla.posicion_y})")
            self.varillas.append(varilla)
        else:
            if y is None:
                raise ValueError("Se debe proporcionar la coordenada y cuando x es un número")
            if not self.validar_posicion(x_o_varilla, y):
                raise ValueError(f"Posición inválida para la varilla: ({x_o_varilla}, {y})")
            varilla = Varilla(
                posicion_x=x_o_varilla,
                posicion_y=y,
                longitud=longitud,
                diametro=diametro
            )
            self.varillas.append(varilla)
            
    def validar_configuracion(self) -> bool:
        """
        Valida la configuración completa de la malla
        """
        # Verificar dimensiones mínimas
        if self.ancho < 3 or self.largo < 3:
            return False
            
        # Verificar espaciamiento adecuado
        if self.espaciamiento_x < 0.5 or self.espaciamiento_y < 0.5:
            return False
            
        # Verificar profundidad
        if self.profundidad < 0.3 or self.profundidad > 3:
            return False
            
        # Verificar varillas
        for varilla in self.varillas:
            if not self.validar_posicion(varilla.posicion_x, varilla.posicion_y):
                return False
            if varilla.longitud < 1.5 or varilla.longitud > 6:
                return False
                
        return True
        
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
    
    def get_longitud_total_conductores(self) -> float:
        """
        Alias de calcular_longitud_total() para mantener compatibilidad.
        Devuelve la longitud total de conductores en metros.
        """
        return self.calcular_longitud_total()
    
    def tiene_obstaculo(self, x: float, y: float) -> bool:
        """
        Verifica si hay un obstáculo en la posición dada.
        A implementar según necesidades específicas.
        """
        # Por ahora retorna False, pero se puede extender para manejar obstáculos
        return False
