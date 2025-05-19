"""
Presets para instalaciones comunes de mallas de tierra
"""
from typing import Dict, Any

PRESETS_INSTALACIONES: Dict[str, Dict[str, Any]] = {
    "Subestación pequeña": {
        "descripcion": "Subestación de distribución típica",
        "parametros": {
            "ancho": 10.0,
            "largo": 10.0,
            "spacing": 2.0,
            "profundidad": 0.5,
            "n_varillas": 4,
            "longitud_varilla": 2.4,
            "resistividad": 100.0,
            "I_falla": 5000.0,
            "t_c": 0.5
        }
    },
    "Subestación mediana": {
        "descripcion": "Subestación de subtransmisión",
        "parametros": {
            "ancho": 20.0,
            "largo": 30.0,
            "spacing": 3.0,
            "profundidad": 0.7,
            "n_varillas": 8,
            "longitud_varilla": 3.0,
            "resistividad": 200.0,
            "I_falla": 10000.0,
            "t_c": 0.3
        }
    },
    "Subestación grande": {
        "descripcion": "Subestación de transmisión",
        "parametros": {
            "ancho": 50.0,
            "largo": 60.0,
            "spacing": 5.0,
            "profundidad": 1.0,
            "n_varillas": 16,
            "longitud_varilla": 3.6,
            "resistividad": 300.0,
            "I_falla": 20000.0,
            "t_c": 0.2
        }
    },
    "Centro de datos": {
        "descripcion": "Centro de datos con alta exigencia de confiabilidad",
        "parametros": {
            "ancho": 15.0,
            "largo": 20.0,
            "spacing": 2.0,
            "profundidad": 0.8,
            "n_varillas": 12,
            "longitud_varilla": 3.0,
            "resistividad": 150.0,
            "I_falla": 8000.0,
            "t_c": 0.3
        }
    },
    "Industria pequeña": {
        "descripcion": "Planta industrial pequeña",
        "parametros": {
            "ancho": 12.0,
            "largo": 15.0,
            "spacing": 3.0,
            "profundidad": 0.6,
            "n_varillas": 6,
            "longitud_varilla": 2.4,
            "resistividad": 120.0,
            "I_falla": 6000.0,
            "t_c": 0.4
        }
    },
    "Hospital": {
        "descripcion": "Centro hospitalario con sistemas críticos",
        "parametros": {
            "ancho": 25.0,
            "largo": 35.0,
            "spacing": 2.5,
            "profundidad": 0.8,
            "n_varillas": 12,
            "longitud_varilla": 3.0,
            "resistividad": 180.0,
            "I_falla": 12000.0,
            "t_c": 0.25
        }
    },
    "Comercial": {
        "descripcion": "Edificio comercial o centro comercial pequeño",
        "parametros": {
            "ancho": 15.0,
            "largo": 20.0,
            "spacing": 2.5,
            "profundidad": 0.6,
            "n_varillas": 8,
            "longitud_varilla": 2.4,
            "resistividad": 150.0,
            "I_falla": 4000.0,
            "t_c": 0.4
        }
    },
    "Domiciliario": {
        "descripcion": "Instalación residencial o edificio de apartamentos",
        "parametros": {
            "ancho": 8.0,
            "largo": 10.0,
            "spacing": 2.0,
            "profundidad": 0.5,
            "n_varillas": 4,
            "longitud_varilla": 2.4,
            "resistividad": 100.0,
            "I_falla": 2000.0,
            "t_c": 0.5
        }
    }
}
