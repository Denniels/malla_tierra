import streamlit as st
from calc import calc_malla_tierra
from calc_avanzado import (
    calcular_potencial_paso,
    calcular_potencial_contacto,
    calcular_resistencia_malla,
    factor_temperatura_suelo
)
from analisis_avanzado import (
    CapaSuelo,
    SueloMulticapa,
    AnalisisCostos,
    OptimizadorMalla
)
from visualizacion import (
    generar_mapa_calor,
    generar_perfil_suelo,
    generar_reporte_pdf,
    calcular_potenciales_superficie
)
from graph import generate_malla_tierra
from validations import ValidationError
from malla import Conductor, MallaTierra
import matplotlib.pyplot as plt
import os
from datetime import datetime

def run_app():
    st.title("Calculadora de Malla de Puesta a Tierra")
    st.write("Diseño según norma IEEE-80")
    
    # Crear pestañas para organizar la interfaz
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Parámetros Básicos",
        "Diseño Avanzado",
        "Análisis",
        "Visualización y Reportes",
        "Análisis Avanzado"
    ])
    
    # Variables globales para el estado
    if 'malla' not in st.session_state:
        st.session_state.malla = None
    
    with tab1:
        # Columnas para parámetros
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Parámetros Eléctricos")
            I = st.number_input(
                "Intensidad de corriente (A)", 
                min_value=0.1, 
                value=100.0, 
                step=0.1,
                help="Corriente nominal del sistema"
            )
            
            R_des = st.number_input(
                "Resistencia deseada por barra (Ω/km)", 
                min_value=0.1, 
                value=0.5, 
                step=0.1,
                help="Resistencia máxima deseada para cada barra de la malla"
            )
            
            sigma = st.number_input(
                "Conductividad del suelo (S/m)", 
                min_value=1e-4, 
                value=0.01, 
                step=1e-3,
                help="Conductividad del terreno. Valores típicos: 0.001-0.1 S/m"
            )
            
            # Calcular resistividad del suelo
            resistividad = 1/sigma
            if resistividad > 1000:
                st.warning("⚠️ Resistividad muy alta (>1000 Ω⋅m). Considere tratamiento del suelo.")
            
            # Densidad del material (antes estaba mal etiquetado)
            densidad = st.number_input(
                "Densidad del material conductor (kg/m³)", 
                min_value=1000, 
                value=7800, 
                step=100,
                help="Densidad del material conductor. Cobre: ~8960, Acero: ~7800"
            )
            
            I_falla = st.number_input(
                "Intensidad de corriente de falla (A)", 
                min_value=0.1, 
                value=1000.0, 
                step=0.1,
                help="Corriente máxima de falla esperada"
            )
            
            if I_falla > 10000:
                st.warning("⚠️ Corriente de falla muy alta. Verifique protecciones.")
        
        with col2:
            st.subheader("Parámetros Físicos")
            L = st.number_input(
                "Longitud total de la malla (m)", 
                min_value=0.5, 
                value=2.0, 
                step=0.5,
                help="Para una malla cuadrada, este es el largo de un lado"
            )
            
            spacing_options = {
                "0.25 m (Densidad Alta)": 0.25,
                "0.5 m (Densidad Media)": 0.5,
                "1.0 m (Densidad Baja)": 1.0
            }
            spacing = st.selectbox(
                "Espaciamiento entre nodos",
                options=list(spacing_options.keys()),
                index=1,
                help="Distancia entre nodos consecutivos de la malla"
            )
            spacing_value = spacing_options[spacing]
            
            h = st.number_input(
                "Profundidad de enterramiento (m)",
                min_value=0.5,
                max_value=2.5,
                value=0.5,
                step=0.1,
                help="Profundidad a la que se enterrará la malla (IEEE-80: 0.5m - 2.5m)"
            )

    with tab2:
        st.subheader("Configuración de la Malla")
        col3, col4 = st.columns(2)
        
        with col3:
            tipo_malla = st.radio(
                "Tipo de malla",
                ["Cuadrada", "Rectangular"],
                index=0,
                help="Seleccione la forma de la malla"
            )
            
            if tipo_malla == "Rectangular":
                ancho = st.number_input(
                    "Ancho de la malla (m)",
                    min_value=0.5,
                    value=2.0,
                    step=0.5
                )
                largo = st.number_input(
                    "Largo de la malla (m)",
                    min_value=0.5,
                    value=3.0,
                    step=0.5
                )
            else:
                ancho = largo = L
            
            material_conductor = st.selectbox(
                "Material del conductor",
                ["Cobre", "Acero Galvanizado"],
                help="Material del conductor de la malla"
            )
            
            diametro_conductor = st.number_input(
                "Diámetro del conductor (mm)",
                min_value=8.0,
                max_value=50.0,
                value=10.0,
                step=0.5
            )
            
        with col4:
            usar_varillas = st.checkbox(
                "Usar varillas verticales",
                help="Añadir varillas de tierra verticales"
            )
            
            if usar_varillas:
                n_varillas = st.number_input(
                    "Número de varillas",
                    min_value=1,
                    max_value=20,
                    value=4
                )
                
                longitud_varilla = st.number_input(
                    "Longitud de varillas (m)",
                    min_value=1.0,
                    max_value=6.0,
                    value=2.4,
                    step=0.1
                )
                
                diametro_varilla = st.number_input(
                    "Diámetro de varillas (mm)",
                    min_value=12.7,
                    max_value=25.4,
                    value=16.0,
                    step=0.1
                )
        
        # Crear conductor según selección
        if material_conductor == "Cobre":
            conductor = Conductor.get_conductor_cobre(diametro_conductor)
        else:
            conductor = Conductor.get_conductor_acero(diametro_conductor)
            
    with tab3:
        st.subheader("Parámetros Avanzados")
        col5, col6 = st.columns(2)
        
        with col5:
            t_c = st.number_input(
                "Tiempo de despeje de falla (s)",
                min_value=0.03,
                max_value=3.0,
                value=0.5,
                step=0.01
            )
            
            rho_s = st.number_input(
                "Resistividad capa superficial (Ω⋅m)",
                min_value=100.0,
                max_value=10000.0,
                value=3000.0,
                step=100.0
            )
            
        with col6:
            T_suelo = st.number_input(
                "Temperatura del suelo (°C)",
                min_value=-20.0,
                max_value=50.0,
                value=25.0,
                step=1.0
            )

    try:
        # Crear objeto malla
        malla = MallaTierra(
            ancho=L if tipo_malla == "Cuadrada" else ancho,
            largo=L if tipo_malla == "Cuadrada" else largo,
            espaciamiento=spacing_value,
            conductor=conductor,
            profundidad=h
        )
        
        if usar_varillas:
            # Agregar varillas en las esquinas
            for x in [0, malla.ancho]:
                for y in [0, malla.largo]:
                    malla.agregar_varilla(
                        x=x,
                        y=y,
                        longitud=longitud_varilla,
                        diametro=diametro_varilla
                    )
        
        st.session_state.malla = malla
        
        # Calcular los parámetros básicos de la malla
        I, R_des, sigma, resistividad, I_falla, L, A, n_barras = calc_malla_tierra(
            I=I,
            R_des=R_des,
            sigma=sigma,
            rho=resistividad,
            I_falla=I_falla,
            L=L if tipo_malla == "Cuadrada" else max(ancho, largo),
            spacing=spacing_value,
            h=h,
            conductor=conductor
        )
        
        # Calcular parámetros avanzados
        f_temp = factor_temperatura_suelo(T_suelo)
        resistividad_corregida = resistividad * f_temp
        
        E_paso, E_paso_max = calcular_potencial_paso(
            I_falla, resistividad_corregida, L, n_barras, h, t_c, rho_s
        )
        
        E_contacto, E_contacto_max = calcular_potencial_contacto(
            I_falla, resistividad_corregida, L, n_barras, h, t_c, rho_s
        )
        
        R_malla = calcular_resistencia_malla(
            resistividad_corregida, L, n_barras, h, diametro_conductor/1000
        )

        # Mostrar información básica de la malla
        st.info(f"""
            ### Dimensiones de la malla:
            - Lado: {L}m x {L}m
            - Área total: {L*L}m²
            - Nodos por lado: {n_barras}
            - Total de nodos: {n_barras * n_barras}
            - Espaciamiento real: {L/(n_barras-1):.3f}m
            - Profundidad: {h}m
            
            ### Parámetros eléctricos:
            - Resistividad del suelo: {resistividad:.2f} Ω⋅m
            - Resistividad corregida por temperatura: {resistividad_corregida:.2f} Ω⋅m
            - Conductividad del suelo: {sigma:.3f} S/m
            - Resistencia de la malla: {R_malla:.3f} Ω
        """)
        
        # Mostrar resultados de seguridad
        col5, col6 = st.columns(2)
        with col5:
            st.metric(
                "Potencial de Paso",
                f"{E_paso:.1f} V",
                f"{E_paso_max - E_paso:.1f} V bajo límite",
                delta_color="normal" if E_paso < E_paso_max else "off"
            )
        with col6:
            st.metric(
                "Potencial de Contacto",
                f"{E_contacto:.1f} V",
                f"{E_contacto_max - E_contacto:.1f} V bajo límite",
                delta_color="normal" if E_contacto < E_contacto_max else "off"
            )
        
        if E_paso > E_paso_max or E_contacto > E_contacto_max:
            st.warning("⚠️ Los potenciales de paso y/o contacto superan los límites seguros. Considere:")
            st.write("- Aumentar el área de la malla")
            st.write("- Reducir el espaciamiento entre conductores")
            st.write("- Aumentar la profundidad de enterramiento")
            st.write("- Mejorar la resistividad de la capa superficial")

        # Botón para calcular y graficar
        if st.button("Calcular y graficar"):
            fig, ax = generate_malla_tierra(I, R_des, sigma, resistividad, I_falla, L, A, n_barras)
            st.pyplot(fig)
            
    except ValidationError as e:
        st.error(f"Error de validación: {str(e)}")
    except Exception as e:
        st.error(f"Error en el cálculo: {str(e)}")

    with tab4:
        st.subheader("Visualización Avanzada")
        
        vista = st.radio(
            "Tipo de visualización",
            ["Mapa de calor de potenciales", "Perfil del suelo", "Malla 3D"],
            help="Seleccione el tipo de visualización"
        )
        
        col7, col8 = st.columns(2)
        with col7:
            mostrar_varillas = st.checkbox(
                "Mostrar varillas",
                value=True,
                help="Mostrar varillas verticales en la visualización"
            )
            
        with col8:
            mostrar_isolineas = st.checkbox(
                "Mostrar isolíneas",
                value=True,
                help="Mostrar líneas de igual potencial"
            )
        
        # Botón para generar reporte PDF
        if st.button("Generar Reporte PDF"):
            try:
                # Preparar datos para el reporte
                parametros = {
                    "Corriente de falla": f"{I_falla} A",
                    "Resistividad del suelo": f"{resistividad} Ω⋅m",
                    "Dimensiones": f"{malla.ancho}m x {malla.largo}m",
                    "Profundidad": f"{h} m",
                    "Material conductor": conductor.material
                }
                
                resultados = {
                    "Potencial de paso": f"{E_paso:.2f} V",
                    "Potencial de contacto": f"{E_contacto:.2f} V",
                    "Resistencia de malla": f"{R_malla:.3f} Ω",
                    "Número de nodos": f"{n_barras * n_barras}"
                }
                
                # Generar y guardar reporte
                nombre_archivo = f"reporte_malla_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                ruta_pdf = generar_reporte_pdf(
                    st.session_state.malla,
                    parametros,
                    resultados,
                    nombre_archivo
                )
                
                with open(ruta_pdf, "rb") as pdf_file:
                    st.download_button(
                        label="Descargar Reporte PDF",
                        data=pdf_file,
                        file_name=nombre_archivo,
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Error al generar el reporte: {e}")
            
        try:
            # Actualizar visualizaciones según la selección
            if vista == "Mapa de calor de potenciales" and st.session_state.malla:
                potenciales = calcular_potenciales_superficie(
                    st.session_state.malla,
                    I_falla,
                    resistividad
                )
                fig, ax = generar_mapa_calor(
                    I_falla,
                    resistividad,
                    st.session_state.malla,
                    potenciales
                )
                st.pyplot(fig)
                
            elif vista == "Perfil del suelo" and st.session_state.malla:
                fig, ax = generar_perfil_suelo(
                    st.session_state.malla,
                    resistividad,
                    h,
                    rho_s
                )
                st.pyplot(fig)
                
            else:  # Malla 3D
                fig, ax = generate_malla_tierra(
                    I, R_des, sigma, resistividad,
                    I_falla, L, A, n_barras
                )
                st.pyplot(fig)
                
        except ValidationError as e:
            st.error(f"Error de validación: {str(e)}")
        except Exception as e:
            st.error(f"Error en el cálculo: {str(e)}")

    with tab5:
        st.subheader("Análisis Avanzado")
        
        analisis_type = st.radio(
            "Tipo de análisis",
            ["Suelo multicapa", "Análisis de costos", "Optimización automática"]
        )
        
        if analisis_type == "Suelo multicapa":
            st.write("Configuración de capas del suelo")
            
            n_capas = st.number_input(
                "Número de capas",
                min_value=1,
                max_value=5,
                value=2
            )
            
            capas = []
            for i in range(n_capas):
                col1, col2 = st.columns(2)
                with col1:
                    prof = st.number_input(
                        f"Profundidad capa {i+1} (m)",
                        min_value=0.0 if i == 0 else capas[-1].profundidad + 0.1,
                        value=float(i+1),
                        step=0.1
                    )
                with col2:
                    res = st.number_input(
                        f"Resistividad capa {i+1} (Ω⋅m)",
                        min_value=1.0,
                        value=100.0 * (i+1),
                        step=10.0
                    )
                capas.append(CapaSuelo(prof, res, f"Capa {i+1}"))
            
            suelo = SueloMulticapa(capas)
            
        elif analisis_type == "Análisis de costos":
            st.write("Análisis económico de la malla")
            
            analisis = AnalisisCostos()
            if st.session_state.malla:
                costos_iniciales = analisis.calcular_costo_inicial(st.session_state.malla)
                
                st.write("Costos iniciales:")
                for item, costo in costos_iniciales.items():
                    st.write(f"- {item}: ${costo:.2f}")
                
                años = st.number_input(
                    "Años de análisis",
                    min_value=1,
                    max_value=50,
                    value=30
                )
                
                costos_totales = analisis.calcular_costo_vida_util(
                    st.session_state.malla,
                    años
                )
                
                st.write("Costos totales (vida útil):")
                for item, costo in costos_totales.items():
                    st.write(f"- {item}: ${costo:.2f}")
                
                costo_total = sum(costos_totales.values())
                st.info(f"Costo total en {años} años: ${costo_total:.2f}")
                
        else:  # Optimización automática
            st.write("Optimización automática del diseño")
            
            col1, col2 = st.columns(2)
            with col1:
                area_min = st.number_input(
                    "Área mínima (m²)",
                    min_value=1.0,
                    value=4.0
                )
                
                I_falla_max = st.number_input(
                    "Corriente de falla máxima (A)",
                    min_value=100.0,
                    value=1000.0
                )
                
            with col2:
                area_max = st.number_input(
                    "Área máxima (m²)",
                    min_value=area_min + 1,
                    value=16.0
                )
                
                R_max = st.number_input(
                    "Resistencia máxima (Ω)",
                    min_value=0.1,
                    value=5.0
                )
            
            if st.button("Optimizar diseño"):
                try:
                    # Usar primera capa del suelo multicapa si está definido
                    if 'suelo' in locals():
                        optimizador = OptimizadorMalla(suelo, AnalisisCostos())
                    else:
                        # Crear suelo simple
                        suelo_simple = SueloMulticapa([CapaSuelo(2.0, resistividad)])
                        optimizador = OptimizadorMalla(suelo_simple, AnalisisCostos())
                    
                    restricciones = {
                        'I_falla': I_falla_max,
                        'R_max': R_max,
                        't_c': 0.5
                    }
                    
                    resultado = optimizador.optimizar_diseño(
                        area_min,
                        area_max,
                        restricciones
                    )
                    
                    if resultado:
                        st.success("¡Diseño optimizado encontrado!")
                        malla_opt = resultado['malla']
                        st.write(f"""
                        Características del diseño óptimo:
                        - Dimensiones: {malla_opt.ancho}m x {malla_opt.largo}m
                        - Espaciamiento: {malla_opt.espaciamiento_x:.2f}m
                        - Profundidad: {malla_opt.profundidad}m
                        - Costo total: ${resultado['costo']:.2f}
                        """)
                        
                        # Actualizar malla actual
                        st.session_state.malla = malla_opt
                    else:
                        st.error("No se encontró un diseño que cumpla con las restricciones")
                        
                except Exception as e:
                    st.error(f"Error en la optimización: {str(e)}")

if __name__ == "__main__":
    run_app()
