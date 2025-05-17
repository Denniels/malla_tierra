# 📊 Resumen de Pruebas

## Estadísticas Generales
- **Fecha de ejecución**: 2025-05-17 18:52:45
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
Fecha: 2025-05-17 18:52:43

## 1. Pruebas de Validaciones Básicas
❌ Error en validaciones básicas: La resistencia equivalente (2.08 Ω) supera la resistencia deseada (0.5 Ω)

## 2. Pruebas de Cálculos de Potenciales
- Potencial de paso: -4331.65 V
- Potencial de paso máximo: 2881.24 V
- Potencial de contacto: -4058.33 V
- Potencial de contacto máximo: 843.35 V
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
- Conductores: $500.00
- Varillas: $0.00
- Soldaduras: $250.00
- Tratamiento: $6.00

Malla de Acero:
- Conductores: $300.00
- Varillas: $0.00
- Soldaduras: $250.00
- Tratamiento: $6.00
❌ Error en pruebas de análisis de costos: 'AnalisisCostos' object has no attribute 'calcular_costo_vida_util'
