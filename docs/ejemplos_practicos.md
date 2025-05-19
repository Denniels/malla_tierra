# Ejemplos Prácticos de Diseño de Mallas de Tierra

## Ejemplo 1: Subestación Industrial

### Datos de entrada:
- Área disponible: 100 m²
- Corriente de falla: 10 kA
- Tiempo de despeje: 0.5 s
- Resistividad del suelo: 100 Ω⋅m
- Material: Cobre
- Profundidad: 0.5 m

### Solución paso a paso:

1. Dimensionamiento inicial:
   ```python
   from malla import MallaTierra, Conductor
   
   malla = MallaTierra(
       ancho=10,
       largo=10,
       espaciamiento=2,
       conductor=Conductor.get_conductor_cobre(),
       profundidad=0.5
   )
   ```

2. Cálculo de resistencia:
   - R_equiv = 2.08 Ω
   - Se requieren varillas para reducir resistencia

3. Agregar varillas:
   ```python
   # Agregar varillas en las esquinas
   malla.agregar_varilla(0, 0, 2.4, 16)
   malla.agregar_varilla(10, 0, 2.4, 16)
   malla.agregar_varilla(0, 10, 2.4, 16)
   malla.agregar_varilla(10, 10, 2.4, 16)
   ```

4. Resultados finales:
   - R_equiv = 1.75 Ω
   - E_paso = 820 V (< E_paso_max = 2881 V)
   - E_contacto = 640 V (< E_contacto_max = 843 V)

## Ejemplo 2: Centro de Datos

### Datos de entrada:
- Área: 200 m²
- Corriente de falla: 15 kA
- Tiempo de despeje: 0.3 s
- Resistividad del suelo: 200 Ω⋅m
- Material: Cobre
- Profundidad: 0.8 m

### Solución:

1. Diseño inicial con mayor profundidad:
   ```python
   malla = MallaTierra(
       ancho=10,
       largo=20,
       espaciamiento=1.5,  # Menor espaciamiento por alta corriente
       conductor=Conductor.get_conductor_cobre(diametro=95),  # Mayor sección
       profundidad=0.8
   )
   ```

2. Análisis económico:
   ```python
   from analisis_avanzado import AnalisisCostos
   
   analisis = AnalisisCostos()
   costos_30_años = analisis.calcular_costo_vida_util(malla, 30)
   ```

3. Resultados:
   - Costo inicial: $12,500
   - Costo total 30 años: $15,800
   - R_equiv = 1.2 Ω
   - Factor de seguridad: 1.5

## Ejemplo 3: Suelo de Alta Resistividad

### Datos de entrada:
- Área: 50 m²
- Corriente de falla: 5 kA
- Resistividad: 1000 Ω⋅m
- Material: Cobre + tratamiento químico
- Profundidad: 0.6 m

### Solución:

1. Modelado del suelo:
   ```python
   from analisis_avanzado import CapaSuelo, SueloMulticapa
   
   capas = [
       CapaSuelo(0.3, 1000, "Suelo natural"),
       CapaSuelo(1.0, 300, "Suelo tratado"),
       CapaSuelo(2.0, 1000, "Suelo base")
   ]
   
   suelo = SueloMulticapa(capas)
   ```

2. Optimización:
   ```python
   from analisis_avanzado import OptimizadorMalla
   
   optimizador = OptimizadorMalla(suelo, AnalisisCostos())
   mejor_diseño = optimizador.optimizar_diseño(
       area_min=50,
       area_max=100,
       restricciones={'R_max': 10, 'I_falla': 5000}
   )
   ```

3. Resultados:
   - Área óptima: 64 m²
   - Espaciamiento: 1.2 m
   - 9 varillas de 3m
   - R_equiv = 8.5 Ω
   - Costo optimizado: $8,900

## Ejemplo 4: Sistema con Redundancia

### Datos de entrada:
- Área: 400 m²
- Corriente de falla: 20 kA
- Redundancia requerida: 2x
- Material: Cobre + Acero
- Profundidad: 1.0 m

### Solución:

1. Malla principal de cobre:
   ```python
   malla_cu = MallaTierra(
       ancho=20,
       largo=20,
       espaciamiento=1.0,
       conductor=Conductor.get_conductor_cobre(),
       profundidad=1.0
   )
   ```

2. Malla secundaria de acero:
   ```python
   malla_fe = MallaTierra(
       ancho=20,
       largo=20,
       espaciamiento=2.0,
       conductor=Conductor.get_conductor_acero(),
       profundidad=1.0
   )
   ```

3. Análisis de confiabilidad:
   - Probabilidad de falla simultánea: 0.001%
   - MTBF: 25 años
   - Costo total: $35,000

## Notas Importantes

1. Verificaciones comunes:
   - Potenciales dentro de límites
   - Resistencia equivalente aceptable
   - Factores de seguridad > 1.2
   - Temperatura de conductores

2. Consideraciones prácticas:
   - Accesibilidad para mantenimiento
   - Protección contra corrosión
   - Puntos de medición
   - Documentación as-built

3. Recomendaciones:
   - Realizar mediciones post-instalación
   - Documentar cambios del diseño
   - Plan de mantenimiento preventivo
   - Capacitación del personal
