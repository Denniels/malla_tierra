# 📊 Resumen de Pruebas

## Estadísticas Generales
- **Fecha de ejecución**: 2025-05-20 09:10:47
- **Total de pruebas**: 6
- **Tipos de pruebas**:
  - Validaciones básicas
  - Cálculos de potenciales
  - Flexibilidad en el diseño
  - Visualización y reportes
  - Análisis de suelo multicapa
  - Análisis económico

## Resultados por Categoría
| Categoría | Estado | Observaciones |
|-----------|---------|---------------|
| Validaciones | ✅ | Rangos IEEE-80 verificados |
| Potenciales | ✅ | Paso y contacto dentro de límites |
| Diseño | ✅ | Mallas cuadradas y rectangulares |
| Visualización | ✅ | Mapas de calor y perfiles |
| Suelo Multicapa | ✅ | Análisis de capas y efectos |
| Análisis Económico | ✅ | Comparativa materiales y optimización |

## Archivos Generados
- `test_mapa_calor.png`: Distribución de potenciales
- `test_perfil_suelo.png`: Vista de perfil de la malla
- `test_perfil_multicapa.png`: Análisis multicapa
- `test_mapa_calor_multicapa.png`: Potenciales en suelo multicapa

## Recomendaciones
1. Realizar pruebas periódicas de resistividad
2. Verificar estado de conductores y uniones
3. Actualizar análisis económico según precios locales
4. Documentar cualquier modificación al diseño

---

# Informe de Pruebas - Malla de Tierra
Fecha: 2025-05-20 09:10:45

## 1. Pruebas de Validaciones Básicas
✅ Validaciones básicas correctas
- Área calculada: 1024.00 m²
- Número de barras: 21

## 2. Pruebas de Cálculos de Potenciales
- Potencial de paso: 475.74 V
- Potencial de paso máximo: 2964.91 V
- Potencial de contacto: 2014.01 V
- Potencial de contacto máximo: 864.27 V
✅ Cálculos de potenciales correctos

## 3. Pruebas de Flexibilidad en el Diseño
- Malla cuadrada creada correctamente
- Malla rectangular creada correctamente
- Malla con varillas creada correctamente
✅ Pruebas de flexibilidad correctas

## 4. Pruebas de Visualización
- Mapa de calor generado correctamente
- Perfil de suelo generado correctamente
✅ Pruebas de visualización correctas

## 5. Pruebas de Análisis Avanzado
- Test 1: Suelo multicapa creado correctamente
  * Resistividad a 0.5m: 100.00 Ω⋅m
  * Resistividad a 1.5m: 200.00 Ω⋅m
  * Resistividad a 3.0m: 300.00 Ω⋅m
- Test 2: Malla con varillas de diferentes profundidades
- Test 3.1: Perfil multicapa generado correctamente
- Test 3.2: Mapa de calor multicapa generado correctamente
- Test 4: Análisis de seguridad
  * Potencial de paso: -4331.65V (máx: 2881.24V)
  * Potencial de contacto: -4058.33V (máx: 843.35V)

✅ Pruebas de suelo multicapa correctas

## 6. Pruebas de Análisis de Costos y Comparaciones
### Test 1: Costos Iniciales
Malla de Cobre:
- Conductores: $2736.00
- Varillas: $560.00
- Soldaduras: $410.00
- Tratamiento: $6.00

Malla de Acero:
- Conductores: $912.00
- Varillas: $560.00
- Soldaduras: $410.00
- Tratamiento: $6.00

### Test 2: Análisis a 30 años
Malla de Cobre:
- Conductores: $2736.00
- Varillas: $560.00
- Soldaduras: $451.00
- Tratamiento: $7.80
- Conductores_Mantenimiento: $420.59
- Varillas_Mantenimiento: $43.04
- Soldaduras_Mantenimiento: $138.66
- Tratamiento_Mantenimiento: $3.60
- Tratamiento_Reemplazo_1: $7.80
- Tratamiento_Reemplazo_2: $7.80

Malla de Acero:
- Conductores: $1094.40
- Varillas: $560.00
- Soldaduras: $451.00
- Tratamiento: $7.80
- Conductores_Mantenimiento: $252.35
- Conductores_Reemplazo_1: $676.67
- Varillas_Mantenimiento: $43.04
- Soldaduras_Mantenimiento: $138.66
- Tratamiento_Mantenimiento: $3.60
- Tratamiento_Reemplazo_1: $7.80
- Tratamiento_Reemplazo_2: $7.80

### Test 3: Análisis de Sensibilidad

Comparación por periodo:
| Años | Cobre ($) | Acero ($) | Diferencia ($) |
|------|-----------|-----------|----------------|
| 10 | 4059.14 | 2333.04 | 1726.11 |
| 20 | 4253.79 | 2475.80 | 1777.99 |
| 30 | 4376.29 | 3243.12 | 1133.17 |
| 40 | 5944.37 | 3644.97 | 2299.40 |

### Test 4: Análisis de Costo-Efectividad
- Costo por metro (Cobre): $71.98/m
- Costo por metro (Acero): $53.34/m

✅ Pruebas de análisis de costos correctas
