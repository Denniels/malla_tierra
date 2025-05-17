"""
Funciones auxiliares para el manejo de unidades en la interfaz
"""
from typing import Dict, Any, Tuple
import streamlit as st
from unidades import SistemaUnidades

def obtener_parametros_campo(
    label: str,
    tipo: str,
    valor_base: float,
    min_valor: float,
    max_valor: float,
    paso: float
) -> Dict[str, Any]:
    """
    Obtiene los parámetros para un campo de entrada con unidades
    
    Args:
        label: Etiqueta del campo
        tipo: Tipo de medida (longitud, area, etc.)
        valor_base: Valor base en unidades SI
        min_valor: Valor mínimo en unidades SI
        max_valor: Valor máximo en unidades SI
        paso: Paso en unidades SI
    """
    unidades = st.session_state.sistema_unidades
    sistema = st.session_state.sistema_actual
    factor = unidades.obtener_factor(tipo)
    simbolo = unidades.obtener_simbolo(tipo)
    
    return {
        "label": f"{label} ({simbolo})",
        "min_value": min_valor / factor,
        "max_value": max_valor / factor,
        "value": valor_base / factor,
        "step": paso / factor
    }

def convertir_si_a_actual(valor: float, tipo: str) -> Tuple[float, str]:
    """
    Convierte un valor desde SI al sistema actual
    
    Args:
        valor: Valor en unidades SI
        tipo: Tipo de medida
    """
    unidades = st.session_state.sistema_unidades
    sistema = st.session_state.sistema_actual
    factor = unidades.obtener_factor(tipo)
    simbolo = unidades.obtener_simbolo(tipo)
    
    return valor / factor, simbolo

def convertir_actual_a_si(valor: float, tipo: str) -> float:
    """
    Convierte un valor desde el sistema actual a SI
    
    Args:
        valor: Valor en unidades del sistema actual
        tipo: Tipo de medida
    """
    unidades = st.session_state.sistema_unidades
    sistema = st.session_state.sistema_actual
    factor = unidades.obtener_factor(tipo)
    
    return valor * factor
