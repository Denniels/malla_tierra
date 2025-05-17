# Calculadora de Malla de Puesta a Tierra

Esta aplicación permite calcular y visualizar una malla de puesta a tierra basada en parámetros eléctricos y físicos específicos.

## Requisitos

- Python 3.8 o superior
- Streamlit
- NumPy
- Matplotlib
- SciPy

## Instalación

1. Clone este repositorio:
```bash
git clone <url-del-repositorio>
cd malla_tierra
```

2. Instale las dependencias:
```bash
pip install streamlit numpy matplotlib scipy
```

## Uso

1. Ejecute la aplicación:
```bash
streamlit run app.py
```

2. En la interfaz web, ingrese los siguientes parámetros:
   - Intensidad de corriente (A)
   - Resistencia deseada por barra (Ω/km)
   - Conductividad del suelo (S/m)
   - Densidad del material de la barra (kg/m³)
   - Intensidad de corriente de falla (A)
   - Longitud total de la malla (m)

3. Haga clic en "Calcular y graficar" para visualizar la malla de tierra.

## Parámetros de Ejemplo

Para una malla de tierra de 2x2 metros con secciones de 50 cm:

- Intensidad de corriente: 100 A
- Resistencia deseada: 0.5 Ω/km
- Conductividad del suelo: 0.01 S/m
- Densidad del material: 7800 kg/m³ (acero)
- Intensidad de falla: 1000 A
- Longitud total: 2 m

## Estructura del Proyecto

- `app.py`: Interfaz de usuario con Streamlit
- `calc.py`: Funciones de cálculo de parámetros
- `graph.py`: Funciones de visualización
- `resultados_prueba.md`: Documentación de resultados de prueba
