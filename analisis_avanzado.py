# -*- coding: utf-8 -*-
"""
Módulo para análisis avanzado de mallas de tierra:
- Suelos multicapa
- Análisis de costos
- Optimización
- Análisis de ciclo de vida
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
from datetime import datetime, timedelta

@dataclass
class CapaSuelo:
    """Representa una capa de suelo"""
    profundidad: float  # m
    resistividad: float  # Ohm-m
    descripcion: str = ""

class SueloMulticapa:
    """Clase para modelar suelos con múltiples capas"""
    
    def __init__(self, capas: List[CapaSuelo]):
        """Inicializa el modelo de suelo multicapa"""
        self.capas = sorted(capas, key=lambda x: x.profundidad)
    
    def get_resistividad_aparente(self, profundidad: float) -> float:
        """
        Calcula la resistividad aparente a una profundidad dada
        usando el método de Sunde mejorado para múltiples capas
        
        Args:
            profundidad: Profundidad en metros donde se quiere calcular la resistividad
            
        Returns:
            float: Resistividad aparente en Ohm-m
        """
        if not self.capas:
            raise ValueError("No hay capas de suelo definidas")
            
        if profundidad <= 0:
            raise ValueError("La profundidad debe ser positiva")
            
        # Si la profundidad es menor que la primera capa
        if profundidad <= self.capas[0].profundidad:
            return self.capas[0].resistividad
            
        # Si la profundidad es mayor que la última capa
        if profundidad > self.capas[-1].profundidad:
            return self.capas[-1].resistividad
            
        # Encontrar la capa correspondiente y calcular la resistividad aparente
        for i in range(len(self.capas)-1):
            if self.capas[i].profundidad < profundidad <= self.capas[i+1].profundidad:
                rho1 = self.capas[i].resistividad
                rho2 = self.capas[i+1].resistividad
                h1 = self.capas[i].profundidad
                h2 = self.capas[i+1].profundidad
                
                # Factor de posición relativa en la capa
                alpha = (profundidad - h1) / (h2 - h1)
                
                # Factor de reflexión entre capas
                k = (rho2 - rho1) / (rho2 + rho1)
                
                # Resistividad base por interpolación lineal
                rho_base = rho1 * (1 - alpha) + rho2 * alpha
                
                # Factor de corrección de Sunde modificado
                # Este factor considera el efecto de las capas adyacentes
                beta = np.exp(-2 * np.pi * profundidad / (h2 - h1))
                factor_correccion = 1 + k * beta * (1 - alpha)
                
                return rho_base * factor_correccion
        
        return self.capas[-1].resistividad

@dataclass
class MaterialCosto:
    """Representa el costo de un material y sus características de degradación"""
    nombre: str
    costo_unitario: float  # Costo por metro o por unidad
    vida_util: int  # Años
    tasa_degradacion: float  # % anual
    costo_mantenimiento: float  # % del costo inicial por año
    factor_ambiental: float = 1.0  # Factor de corrección por condiciones ambientales

class AnalisisCostos:
    """Clase para análisis económico de la malla"""
    def __init__(self):
        """Inicializa los costos de materiales con valores típicos"""
        self.materiales = {
            "Cobre": MaterialCosto(
                nombre="Conductor de cobre",
                costo_unitario=45.0,  # USD/m - Actualizado a precio de mercado
                vida_util=30,
                tasa_degradacion=0.02,  # 2% anual
                costo_mantenimiento=0.01,  # 1% anual
                factor_ambiental=1.0
            ),
            "Acero": MaterialCosto(
                nombre="Conductor de acero galvanizado",
                costo_unitario=15.0,  # USD/m - Se mantiene
                vida_util=25,
                tasa_degradacion=0.03,  # 3% anual
                costo_mantenimiento=0.015,  # 1.5% anual
                factor_ambiental=1.2  # Mayor afectación por corrosión
            ),
            "Varilla": MaterialCosto(
                nombre="Varilla de cobre",
                costo_unitario=35.0,  # USD/unidad - Actualizado
                vida_util=30,
                tasa_degradacion=0.015,  # 1.5% anual
                costo_mantenimiento=0.005,  # 0.5% anual
                factor_ambiental=1.0
            ),
            "Soldadura": MaterialCosto(
                nombre="Soldadura exotérmica",
                costo_unitario=10.0,  # USD/unión
                vida_util=30,
                tasa_degradacion=0.01,  # 1% anual
                costo_mantenimiento=0.02,  # 2% anual
                factor_ambiental=1.1
            ),
            "Tratamiento": MaterialCosto(
                nombre="Tratamiento de suelo",
                costo_unitario=5.0,  # USD/m²
                vida_util=10,
                tasa_degradacion=0.05,  # 5% anual
                costo_mantenimiento=0.03,  # 3% anual
                factor_ambiental=1.3
            )
        }
    
    def calcular_costo_inicial(self, malla) -> Dict[str, float]:
        """Calcula el costo inicial de la malla"""
        costos = {}
        
        # Costo de conductores
        longitud_total = malla.calcular_longitud_total()
        material = "Cobre" if malla.conductor.material == "Cobre" else "Acero"
        costos["Conductores"] = longitud_total * self.materiales[material].costo_unitario
        
        # Costo de varillas
        n_varillas = len(malla.varillas)
        costos["Varillas"] = n_varillas * self.materiales["Varilla"].costo_unitario
        
        # Costo de soldaduras (uniones)
        n_uniones = n_varillas + malla.n_x * malla.n_y
        costos["Soldaduras"] = n_uniones * self.materiales["Soldadura"].costo_unitario
        
        # Costo de tratamiento de suelo
        area_tratamiento = malla.ancho * malla.largo * 0.3  # 30cm de profundidad
        costos["Tratamiento"] = area_tratamiento * self.materiales["Tratamiento"].costo_unitario
        
        return costos
    
    def calcular_costo_vida_util(self, malla, años: int, tasa_interes: float = 0.05) -> Dict[str, float]:
        """
        Calcula el costo total de la malla considerando su vida útil.
        
        Args:
            malla: Objeto MallaTierra
            años: Período de análisis en años
            tasa_interes: Tasa de interés anual (default 5%)
        
        Returns:
            Dict[str, float]: Desglose de costos en valor presente
        """
        costos_iniciales = self.calcular_costo_inicial(malla)
        costos_totales = {k: v for k, v in costos_iniciales.items()}
        material = "Cobre" if malla.conductor.material == "Cobre" else "Acero"
        
        # Mapeo de nombres de elementos a materiales
        mapeo_materiales = {
            "Conductores": material,
            "Varillas": "Varilla",
            "Soldaduras": "Soldadura",
            "Tratamiento": "Tratamiento"
        }
        
        for item, costo_inicial in costos_iniciales.items():
            material_info = self.materiales[mapeo_materiales[item]]
            
            # Factor de valor presente para anualidades
            factor_vp = (1 - (1 + tasa_interes)**-años) / tasa_interes
            
            # Costos de mantenimiento anuales
            costo_mant_anual = costo_inicial * material_info.costo_mantenimiento
            costos_totales[f"{item}_Mantenimiento"] = costo_mant_anual * factor_vp * material_info.factor_ambiental
            
            # Reemplazos por vida útil
            n_reemplazos = años // material_info.vida_util
            if n_reemplazos > 0:
                for i in range(n_reemplazos):
                    año_reemplazo = (i + 1) * material_info.vida_util
                    if año_reemplazo < años:
                        # Factor de valor presente para costo futuro
                        factor_vp_reemplazo = 1 / ((1 + tasa_interes)**año_reemplazo)
                        # Costo de reemplazo considerando degradación acumulada
                        degradacion_acum = (1 + material_info.tasa_degradacion)**año_reemplazo
                        costo_reemplazo = costo_inicial * degradacion_acum * material_info.factor_ambiental
                        costos_totales[f"{item}_Reemplazo_{i+1}"] = costo_reemplazo * factor_vp_reemplazo
            
            # Ajuste del costo inicial por factor ambiental
            costos_totales[item] *= material_info.factor_ambiental
        
        return costos_totales

class OptimizadorMalla:
    """Clase para optimización automática del diseño"""
    def __init__(self, suelo: SueloMulticapa, analisis_costos: AnalisisCostos):
        self.suelo = suelo
        self.analisis_costos = analisis_costos
    
    def optimizar_diseño(
        self,
        area_min: float,
        area_max: float,
        restricciones: Dict[str, float]
    ) -> Optional[Dict]:
        """
        Optimiza el diseño de la malla considerando restricciones
        y minimizando costos
        """
        mejor_diseno = None
        menor_costo = float("inf")
        
        # Grid search sobre parámetros de diseño
        for ancho in np.linspace(np.sqrt(area_min), np.sqrt(area_max), 10):
            for espaciamiento in [1.0, 2.0, 3.0]:
                for prof in np.linspace(0.5, 2.0, 4):
                    try:
                        malla = self._crear_malla_candidata(
                            ancho=ancho,
                            espaciamiento=espaciamiento,
                            profundidad=prof
                        )
                        
                        if self._cumple_restricciones(malla, restricciones):
                            costo = sum(self.analisis_costos.calcular_costo_inicial(malla).values())
                            
                            if costo < menor_costo:
                                menor_costo = costo
                                mejor_diseno = {
                                    "malla": malla,
                                    "costo": costo,
                                    "parametros": {
                                        "ancho": ancho,
                                        "espaciamiento": espaciamiento,
                                        "profundidad": prof
                                    }
                                }
                    except Exception:
                        continue
        
        return mejor_diseno
    
    def _crear_malla_candidata(self, ancho: float, espaciamiento: float, profundidad: float):
        """Crea una malla candidata para optimización"""
        from malla import MallaTierra, Conductor
        return MallaTierra(
            ancho=ancho,
            largo=ancho,  # Malla cuadrada para simplicidad
            espaciamiento=espaciamiento,
            profundidad=profundidad,
            conductor=Conductor.get_conductor_cobre()
        )
    
    def _cumple_restricciones(self, malla, restricciones: Dict[str, float]) -> bool:
        """Verifica si un diseño cumple con las restricciones dadas"""
        from calc_avanzado import (
            calcular_potencial_paso,
            calcular_potencial_contacto,
            calcular_resistencia_malla
        )
        
        # Obtener resistividad aparente del suelo a la profundidad de la malla
        rho = self.suelo.get_resistividad_aparente(malla.profundidad)
        
        try:
            # Verificar potencial de paso
            E_paso, E_paso_max = calcular_potencial_paso(
                restricciones.get("I_falla", 1000),
                rho,
                malla.ancho,
                malla.n_x,
                malla.profundidad
            )
            if E_paso > E_paso_max:
                return False
            
            # Verificar potencial de contacto
            E_contacto, E_contacto_max = calcular_potencial_contacto(
                restricciones.get("I_falla", 1000),
                rho,
                malla.ancho,
                malla.n_x,
                malla.profundidad
            )
            if E_contacto > E_contacto_max:
                return False
            
            # Verificar resistencia de malla
            R_malla = calcular_resistencia_malla(
                rho,
                malla.ancho,
                malla.n_x,
                malla.profundidad
            )
            if R_malla > restricciones.get("R_max", 5):
                return False
            
            return True
            
        except Exception:
            return False