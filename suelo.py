"""Módulo para manejar las características del suelo"""

class CapaSuelo:
    """Clase para representar una capa de suelo"""
    def __init__(self, profundidad, resistividad, descripcion=None):
        self.profundidad = profundidad  # m
        self.resistividad = resistividad  # Ω⋅m
        self.descripcion = descripcion
    
    @classmethod
    def get_capa_tipica(cls):
        """Crea una capa de suelo con valores típicos"""
        return cls(
            profundidad=0.5,
            resistividad=100,
            descripcion="Suelo típico"
        )
    
    @classmethod
    def get_capa_superficial(cls):
        """Crea una capa superficial típica con grava"""
        return cls(
            profundidad=0.1,
            resistividad=3000,
            descripcion="Capa superficial de grava"
        )
