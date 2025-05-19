# Manual Técnico - Sistema de Diseño de Mallas de Tierra

## 1. Introducción

Este manual técnico describe en detalle la implementación y funcionamiento del sistema de diseño de mallas de tierra, desarrollado según la norma IEEE-80.

### 1.1 Alcance

El sistema permite:
- Diseño de mallas cuadradas y rectangulares
- Análisis de suelos multicapa
- Cálculo de potenciales de paso y contacto
- Análisis económico y optimización
- Generación de reportes y visualizaciones

### 1.2 Arquitectura del Sistema

El sistema está organizado en los siguientes módulos:
- `calc.py`: Cálculos básicos de malla
- `calc_avanzado.py`: Cálculos avanzados (potenciales, resistencia)
- `malla.py`: Definición de estructuras de malla
- `analisis_avanzado.py`: Análisis económico y optimización
- `visualizacion.py`: Generación de gráficos y reportes

## 2. Fundamentos Teóricos

### 2.1 Resistencia de Malla

La resistencia de la malla se calcula según IEEE-80 usando:

```
R = ρ * (1/L_total + 1/√(20A) * (1 + 1/(1 + h * √(20/A))))
```

Donde:
- ρ: Resistividad del suelo (Ω⋅m)
- L_total: Longitud total de conductores (m)
- A: Área efectiva de la malla (m²)
- h: Profundidad de enterramiento (m)

### 2.2 Potenciales de Seguridad

#### 2.2.1 Potencial de Paso
```
E_paso = (ρ * I_f * K_s) / L
```

#### 2.2.2 Potencial de Contacto
```
E_contacto = (ρ * I_f * K_m * K_i) / L
```

## 3. Implementación

### 3.1 Clase MallaTierra

La clase `MallaTierra` es la estructura principal que representa una malla de tierra:

```python
class MallaTierra:
    def __init__(self, ancho, largo, espaciamiento, conductor, profundidad):
        # Inicialización de parámetros básicos
        
    def agregar_varilla(self, x, y, longitud, diametro):
        # Agregar varilla vertical
        
    def calcular_longitud_total(self):
        # Calcular longitud total de conductores
```

### 3.2 Análisis de Costos

El análisis económico considera:
- Costos iniciales de materiales
- Costos de mantenimiento
- Vida útil de componentes
- Factores ambientales
- Valor presente neto

## 4. Validaciones y Restricciones

### 4.1 Rangos Válidos

| Parámetro | Mínimo | Máximo | Unidad |
|-----------|---------|---------|---------|
| Área | 4 | 10000 | m² |
| Espaciamiento | 0.5 | 10 | m |
| Profundidad | 0.3 | 3.0 | m |
| Resistividad | 1 | 5000 | Ω⋅m |
| Corriente de falla | 1 | 50 | kA |

### 4.2 Factores de Seguridad

- Factor de seguridad mínimo: 1.2
- Margen de área efectiva: 1m adicional por lado
- Factor de corrección por temperatura

## 5. Optimización

### 5.1 Algoritmo de Optimización

El sistema utiliza un algoritmo de optimización que:
1. Define un espacio de búsqueda basado en restricciones
2. Evalúa configuraciones candidatas
3. Minimiza costos manteniendo seguridad
4. Considera factores ambientales y económicos

### 5.2 Criterios de Convergencia

- Tolerancia en resistencia: ±5%
- Tolerancia en potenciales: ±10%
- Máximo número de iteraciones: 100

## 6. Integración con Otros Sistemas

### 6.1 Formatos de Entrada/Salida

- Entrada: Archivos JSON de configuración
- Salida: 
  * Reportes PDF
  * Visualizaciones PNG/SVG
  * Datos de malla en formato CAD

### 6.2 API de Integración

```python
from proyecto import ProyectoMallaTierra

# Crear nuevo proyecto
proyecto = ProyectoMallaTierra("nombre")

# Cargar configuración
proyecto.cargar("config.json")

# Ejecutar cálculos
resultados = proyecto.calcular()

# Exportar resultados
proyecto.exportar("reporte.pdf")
```

## 7. Mantenimiento y Actualización

### 7.1 Versionado

El sistema utiliza control de versiones para:
- Seguimiento de cambios en diseños
- Comparación de versiones
- Historial de modificaciones

### 7.2 Actualización de Parámetros

Los presets y parámetros se pueden actualizar mediante:
- Archivos de configuración JSON
- Interfaz de usuario
- API programática

## 8. Referencias

1. IEEE Std 80-2013 - Guide for Safety in AC Substation Grounding
2. IEC 61936-1 - Power installations exceeding 1 kV AC
3. NEC Article 250 - Grounding and Bonding
