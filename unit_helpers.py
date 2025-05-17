"""
Helper functions for unit conversions in the app
"""
from typing import Dict, Any

def obtener_parametros_unidad(tipo: str) -> Dict[str, Any]:
    """Obtiene los parámetros de unidad para un tipo de medida"""
    from app import st
    unidades = st.session_state.sistema_unidades
    sistema = st.session_state.sistema_actual
    return {
        "simbolo": unidades.obtener_simbolo(tipo),
        "factor": unidades.obtener_factor(tipo)
    }

def ajustar_valor_unidad(valor: float, tipo: str) -> float:
    """Ajusta un valor según el sistema de unidades actual"""
    params = obtener_parametros_unidad(tipo)
    return valor / params["factor"]

def obtener_label_unidad(label: str, tipo: str) -> str:
    """Obtiene la etiqueta con la unidad correcta"""
    params = obtener_parametros_unidad(tipo)
    return f"{label} ({params['simbolo']})"
