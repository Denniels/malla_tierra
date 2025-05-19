# Guía de Troubleshooting - Sistema de Mallas de Tierra

## 1. Problemas Comunes y Soluciones

### 1.1 Resistencia Alta

#### Síntomas:
- R_equiv > R_deseada
- Mensaje "La resistencia equivalente supera la resistencia deseada"

#### Causas Posibles:
1. Área de malla insuficiente
2. Pocas varillas
3. Resistividad del suelo alta

#### Soluciones:
1. Aumentar el área de la malla
2. Agregar varillas verticales
3. Considerar tratamiento químico del suelo
4. Reducir espaciamiento entre conductores

### 1.2 Potenciales Peligrosos

#### Síntomas:
- E_paso > E_paso_max
- E_contacto > E_contacto_max
- Advertencias de potenciales cercanos a límites

#### Causas Posibles:
1. Espaciamiento muy grande
2. Área insuficiente
3. Profundidad inadecuada

#### Soluciones:
1. Reducir espaciamiento entre conductores
2. Aumentar profundidad de enterramiento
3. Mejorar la capa superficial
4. Agregar conductores adicionales

### 1.3 Errores de Cálculo

#### Síntomas:
- Resultados inconsistentes
- Errores de validación
- Mensajes de error en cálculos

#### Soluciones:
1. Verificar unidades de entrada
2. Comprobar rangos de parámetros
3. Validar datos de suelo
4. Actualizar factores de corrección

## 2. Problemas de Optimización

### 2.1 No Converge

#### Síntomas:
- Mensaje "No se encontró solución óptima"
- Iteraciones máximas alcanzadas

#### Causas Posibles:
1. Restricciones muy estrictas
2. Rango de búsqueda inadecuado
3. Conflicto entre objetivos

#### Soluciones:
1. Relajar restricciones
2. Ampliar rango de búsqueda
3. Ajustar parámetros de optimización
4. Dividir el problema en partes

### 2.2 Costos Excesivos

#### Síntomas:
- Costos fuera de presupuesto
- Relación costo-beneficio alta

#### Soluciones:
1. Optimizar geometría
2. Considerar materiales alternativos
3. Reducir redundancia si es posible
4. Analizar diferentes períodos

## 3. Problemas de Visualización

### 3.1 Gráficos Incorrectos

#### Síntomas:
- Visualizaciones distorsionadas
- Escala incorrecta
- Colores inadecuados

#### Soluciones:
1. Ajustar escala de visualización
2. Verificar datos de entrada
3. Cambiar paleta de colores
4. Actualizar límites de ejes

### 3.2 Errores en Reportes

#### Síntomas:
- PDF no se genera
- Datos faltantes
- Formato incorrecto

#### Soluciones:
1. Verificar permisos de archivo
2. Completar datos requeridos
3. Validar plantillas
4. Actualizar configuración

## 4. Problemas de Integración

### 4.1 Importación/Exportación

#### Síntomas:
- Errores al cargar archivos
- Formato de datos incompatible
- Pérdida de información

#### Soluciones:
1. Verificar formato de archivo
2. Validar estructura de datos
3. Actualizar conversores
4. Revisar compatibilidad

### 4.2 Control de Versiones

#### Síntomas:
- Conflictos de versión
- Pérdida de historial
- Datos inconsistentes

#### Soluciones:
1. Restaurar versión anterior
2. Reconciliar cambios
3. Validar integridad de datos
4. Actualizar metadatos

## 5. Procedimiento de Escalamiento

### 5.1 Nivel 1: Usuario Final
1. Consultar documentación
2. Verificar datos de entrada
3. Aplicar soluciones básicas

### 5.2 Nivel 2: Soporte Técnico
1. Análisis detallado de logs
2. Depuración de cálculos
3. Optimización de parámetros

### 5.3 Nivel 3: Desarrollo
1. Corrección de código
2. Actualización de algoritmos
3. Mejoras de rendimiento

## 6. Mantenimiento Preventivo

### 6.1 Diario
- Backup de datos
- Validación de cálculos
- Revisión de logs

### 6.2 Semanal
- Actualización de parámetros
- Limpieza de archivos temporales
- Verificación de integridad

### 6.3 Mensual
- Análisis de rendimiento
- Optimización de base de datos
- Actualización de documentación

## 7. Herramientas de Diagnóstico

### 7.1 Validación de Datos
```python
from validations import validate_all_parameters

try:
    validate_all_parameters(I_falla, rho, L, spacing, h, potentials)
except ValidationError as e:
    print(f"Error de validación: {str(e)}")
```

### 7.2 Pruebas de Consistencia
```python
def verificar_consistencia(malla):
    # Verificar geometría
    assert malla.ancho > 0 and malla.largo > 0
    
    # Verificar conductores
    assert malla.calcular_longitud_total() > 0
    
    # Verificar varillas
    if malla.varillas:
        assert all(v.longitud > 0 for v in malla.varillas)
```

### 7.3 Logging y Monitoreo
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Iniciando cálculos...")
logger.info("Parámetros validados")
logger.warning("Resistencia cerca del límite")
logger.error("Error en optimización")
```
