# Normas y Recomendaciones para Sistemas de Puesta a Tierra

## 1. Parámetros de Diseño Principales

### 1.1 Área y Dimensiones
- **Área mínima**: 4 m² (2x2 metros)
- **Área máxima recomendada**: 10000 m² (100x100 metros)
- **Relación largo/ancho**: Preferentemente ≤ 2:1 para mejor distribución de corriente
- **Factores que influyen en el área**:
  * Corriente de falla
  * Resistividad del suelo
  * Tiempo de despeje de falla
  * Temperatura ambiente

### 1.2 Espaciamiento entre Conductores
- **Mínimo**: 0.5 metros
- **Máximo**: 10 metros
- **Óptimo**: 2-3 metros para la mayoría de las aplicaciones
- **Consideraciones**:
  * Mayor espaciamiento → Menor costo, pero mayor potencial de paso
  * Menor espaciamiento → Mayor costo, mejor distribución de corriente

### 1.3 Profundidad de Enterramiento
- **Mínima**: 0.3 metros
- **Máxima**: 3.0 metros
- **Óptima**: 0.5-0.8 metros
- **Factores a considerar**:
  * Tipo de suelo
  * Nivel freático
  * Temperatura
  * Riesgo de daño mecánico

## 2. Configuración de Capas del Suelo

### 2.1 Número de Capas
- **Mínimo**: 1 capa (suelo homogéneo)
- **Típico**: 2-3 capas
- **Máximo recomendado**: 4 capas
- **Rango de resistividades**:
  * Capa superior: 50-500 Ω⋅m
  * Capas intermedias: 100-2000 Ω⋅m
  * Capa profunda: 50-5000 Ω⋅m

### 2.2 Separación entre Capas
- **Mínima**: 0.2 metros
- **Máxima**: 5.0 metros
- **Consideraciones por capa**:
  * Primera capa: 0.3-1.0 metros
  * Segunda capa: 1.0-2.5 metros
  * Tercera capa: 2.5-5.0 metros

### 2.3 Uniones entre Capas
- **Tipos de uniones**:
  * Soldadura exotérmica (preferida)
  * Conexiones mecánicas (con mantenimiento periódico)
  * Conectores certificados
- **Requisitos**:
  * Resistencia mecánica adecuada
  * Resistencia a la corrosión
  * Capacidad de conducción de corriente

## 3. Límites de Seguridad

### 3.1 Potenciales de Paso y Contacto
- **Potencial de paso máximo**: 
  * Con capa superficial: 3000V
  * Sin capa superficial: 2000V
- **Potencial de contacto máximo**:
  * Con capa superficial: 1000V
  * Sin capa superficial: 800V

### 3.2 Resistencia de la Malla
- **Máxima general**: 5 Ω
- **Subestaciones**: ≤ 1 Ω
- **Edificios**: ≤ 10 Ω
- **Torres de transmisión**: ≤ 20 Ω

## 4. Recomendaciones de Diseño

### 4.1 Por Tipo de Suelo
| Resistividad (Ω⋅m) | Recomendación |
|-------------------|----------------|
| < 100 | Malla simple, espaciamiento estándar |
| 100-500 | Agregar varillas en perímetro |
| 500-1000 | Tratamiento químico del suelo |
| > 1000 | Sistema multicapa con varillas profundas |

### 4.2 Por Nivel de Corriente de Falla
| Corriente (kA) | Recomendación |
|----------------|---------------|
| < 5 | Malla básica |
| 5-15 | Agregar varillas en esquinas |
| 15-30 | Doble malla o menor espaciamiento |
| > 30 | Sistema especial con conductores paralelos |

## 5. Factores de Ajuste

### 5.1 Por Temperatura
```python
Factor = 1 + α(T - 20°C)
donde:
α = 0.00393 para cobre
α = 0.00400 para acero
```

### 5.2 Por Humedad
| Humedad (%) | Factor |
|-------------|---------|
| < 20 | 3.0 |
| 20-40 | 2.0 |
| 40-60 | 1.5 |
| > 60 | 1.0 |

## 6. Variables de Control en la Interfaz

### 6.1 Parámetros Ajustables
- **Dimensiones de la malla**:
  * Ancho: 2-100 metros
  * Largo: 2-100 metros
  * Paso: 0.5 metros

- **Espaciamiento**:
  * Rango: 0.5-10 metros
  * Paso: 0.1 metros

- **Configuración de capas**:
  * Número: 1-4 capas
  * Profundidad: 0.2-5.0 metros por capa
  * Resistividad: 50-5000 Ω⋅m

- **Varillas**:
  * Longitud: 1.5-6.0 metros
  * Diámetro: 12-25 mm
  * Cantidad: 4-36 unidades

### 6.2 Indicadores de Estado
- 🟢 Valores dentro de rango óptimo
- 🟡 Valores aceptables pero no óptimos
- 🔴 Valores fuera de rango seguro

## 7. Mantenimiento y Monitoreo

### 7.1 Frecuencia de Inspección
- Visual: Anual
- Mediciones: Cada 2 años
- Termografía: Cada 5 años

### 7.2 Parámetros a Monitorear
- Resistencia de la malla
- Continuidad de las uniones
- Corrosión en conexiones
- Condición del suelo

## 8. Documentación Requerida

### 8.1 Diseño
- Planos de la malla
- Cálculos justificativos
- Especificaciones de materiales
- Memoria técnica

### 8.2 Mantenimiento
- Registro de mediciones
- Historial de modificaciones
- Reportes de inspección
- Plan de mantenimiento
