import streamlit as st
from unidades import UnidadesMallaTierra, SistemaUnidades
from proyecto import ProyectoMallaTierra
from presets import PRESETS_INSTALACIONES
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
    generar_reporte_markdown,
    calcular_potenciales_superficie
)
from graph import generate_malla_tierra
from validations import ValidationError
from malla import Conductor, MallaTierra
import matplotlib.pyplot as plt
import os
from datetime import datetime

def inicializar_sistema_unidades():
    """Inicializa el sistema de unidades en el estado de la sesión"""
    if 'sistema_unidades' not in st.session_state:
        st.session_state.sistema_unidades = UnidadesMallaTierra()
    if 'sistema_actual' not in st.session_state:
        st.session_state.sistema_actual = SistemaUnidades.METRICO

def convertir_valor(valor: float, tipo: str, desde: SistemaUnidades, hacia: SistemaUnidades) -> float:
    """Convierte un valor entre sistemas de unidades"""
    valor_convertido, _ = st.session_state.sistema_unidades.convertir(valor, tipo, desde, hacia)
    return valor_convertido

def cargar_estado_desde_proyecto(proyecto: ProyectoMallaTierra) -> None:
    """Carga el estado de la aplicación desde un proyecto"""
    if not proyecto:
        return
        
    # Actualizar st.session_state con los valores del proyecto
    for key, value in proyecto.parametros.items():
        if key in st.session_state:
            st.session_state[key] = value

def guardar_estado_en_proyecto(proyecto: ProyectoMallaTierra) -> None:
    """Guarda el estado actual de la aplicación en un proyecto"""
    if not proyecto:
        return
        
    # Guardar valores relevantes en el proyecto
    proyecto.actualizar_parametros(
        corriente=st.session_state.get('I', 100.0),
        corriente_falla=st.session_state.get('I_falla', 1000.0),
        tiempo_despeje=st.session_state.get('t_c', 0.5),
        resistividad=st.session_state.get('resistividad', 100.0),
        tipo_malla=st.session_state.get('tipo_malla', 'Cuadrada'),
        ancho=st.session_state.get('ancho', 20.0),
        largo=st.session_state.get('largo', 20.0),
        spacing=st.session_state.get('spacing', 2.0),
        profundidad=st.session_state.get('h', 0.5),
        usar_varillas=st.session_state.get('usar_varillas', True),
        n_varillas=st.session_state.get('n_varillas', 4)
    )

def obtener_parametros_unidad(tipo: str) -> dict:
    """Obtiene los parámetros de unidad para un tipo de medida"""
    unidades = st.session_state.sistema_unidades
    sistema = st.session_state.sistema_actual
    return {
        "simbolo": unidades.obtener_simbolo(tipo),
        "factor": unidades.obtener_factor(tipo)
    }

def run_app():
    st.set_page_config(layout="wide")
    st.title("Calculadora de Malla de Puesta a Tierra")
    st.write("Diseño según norma IEEE-80")
    
    # Inicializar sistema de unidades y variables globales
    inicializar_sistema_unidades()
    if 'factor_seg' not in st.session_state:
        st.session_state.factor_seg = 1.2
    
    # Inicializar el estado del proyecto
    if 'proyecto_actual' not in st.session_state:
        st.session_state.proyecto_actual = None
        
    # Variables de estado
    if 'malla' not in st.session_state:
        st.session_state.malla = None
    
    # Barra superior para archivo, presets y unidades
    col_archivo, col_preset, col_unidades = st.columns([2, 2, 1])
    
    with col_archivo:
        archivo_option = st.selectbox(
            "Archivo",
            ["Nuevo proyecto", "Cargar proyecto", "Guardar proyecto", "Guardar como..."]
        )
        
        if archivo_option == "Nuevo proyecto":
            if st.button("Crear nuevo proyecto"):
                nombre = datetime.now().strftime("Proyecto_%Y%m%d_%H%M%S")
                st.session_state.proyecto_actual = ProyectoMallaTierra(nombre)
                st.success("Nuevo proyecto creado")
        
        elif archivo_option == "Cargar proyecto":
            uploaded_file = st.file_uploader("Seleccionar archivo de proyecto", type="json")
            if uploaded_file is not None:
                try:
                    # Guardar el archivo temporalmente
                    temp_path = os.path.join("reportes", uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Cargar el proyecto
                    proyecto = ProyectoMallaTierra.cargar(temp_path)
                    st.session_state.proyecto_actual = proyecto
                    cargar_estado_desde_proyecto(proyecto)
                    st.success("Proyecto cargado correctamente")
                    
                    # Limpiar archivo temporal
                    os.remove(temp_path)
                except Exception as e:
                    st.error(f"Error al cargar el proyecto: {str(e)}")
        
        elif archivo_option in ["Guardar proyecto", "Guardar como..."]:
            if st.session_state.proyecto_actual:
                nombre = st.text_input(
                    "Nombre del proyecto",
                    value=st.session_state.proyecto_actual.nombre
                )
                if st.button("Guardar"):
                    try:
                        guardar_estado_en_proyecto(st.session_state.proyecto_actual)
                        ruta = os.path.join("reportes", f"{nombre}.json")
                        st.session_state.proyecto_actual.guardar(ruta)
                        
                        # Ofrecer descarga del archivo
                        with open(ruta, "rb") as f:
                            st.download_button(
                                "📥 Descargar archivo del proyecto",
                                f,
                                file_name=f"{nombre}.json",
                                mime="application/json"
                            )
                    except Exception as e:
                        st.error(f"Error al guardar el proyecto: {str(e)}")
            else:
                st.warning("Primero debe crear o cargar un proyecto")
    
    with col_preset:
        st.subheader("Presets")
        preset_seleccionado = st.selectbox(
            "Cargar configuración predefinida",
            ["Personalizado"] + list(PRESETS_INSTALACIONES.keys()),
            help="Seleccione una configuración predefinida para el tipo de instalación"
        )
        
        if preset_seleccionado != "Personalizado":
            if st.button("Aplicar preset"):
                preset = PRESETS_INSTALACIONES[preset_seleccionado]
                st.session_state.update(preset["parametros"])
                st.info(f"Preset aplicado: {preset['descripcion']}")
    
    with col_unidades:
        sistema_anterior = st.session_state.sistema_actual
        nuevo_sistema = st.selectbox(
            "Sistema de unidades",
            [sistema.value for sistema in SistemaUnidades],
            index=list(SistemaUnidades).index(st.session_state.sistema_actual)
        )
        
        # Convertir valores si cambió el sistema
        if nuevo_sistema != sistema_anterior.value:
            nuevo_sistema_enum = SistemaUnidades(nuevo_sistema)
            if 'malla' in st.session_state and st.session_state.malla:
                # Convertir dimensiones de la malla
                st.session_state.malla.ancho = convertir_valor(
                    st.session_state.malla.ancho,
                    "longitud",
                    sistema_anterior,
                    nuevo_sistema_enum
                )
                st.session_state.malla.largo = convertir_valor(
                    st.session_state.malla.largo,
                    "longitud",
                    sistema_anterior,
                    nuevo_sistema_enum
                )
                st.session_state.malla.profundidad = convertir_valor(
                    st.session_state.malla.profundidad,
                    "longitud",
                    sistema_anterior,
                    nuevo_sistema_enum
                )
            st.session_state.sistema_actual = nuevo_sistema_enum
            st.rerun()  # Recargar la interfaz con las nuevas unidades
    
    # Separador visual
    st.markdown("---")

    # Barra lateral para documentación y ayuda
    with st.sidebar:
        st.header("Documentación")
        with st.expander("Rangos Recomendados"):
            st.write("""
            - Área: 4-10000 m²
            - Espaciamiento: 0.5-10 m
            - Profundidad: 0.3-3.0 m
            - Resistividad: 1-5000 Ω⋅m
            - Corriente de falla: 1-50 kA
            """)
        
        with st.expander("Recomendaciones"):
            st.write("""
            ### Por tipo de suelo:
            - <100 Ω⋅m: Malla simple
            - 100-500 Ω⋅m: Agregar varillas
            - >500 Ω⋅m: Tratamiento químico
            
            ### Por corriente de falla:
            - <5 kA: Malla básica
            - 5-15 kA: Varillas en esquinas
            - >15 kA: Menor espaciamiento
            """)
    
    # Crear pestañas para organizar la interfaz
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Parámetros Básicos",
        "Diseño de Malla",
        "Configuración de Capas",
        "Visualización y Reportes",
        "Análisis Avanzado"
    ])
    
    with tab1:
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
            
            I_falla = st.number_input(
                "Intensidad de corriente de falla (A)", 
                min_value=100.0, 
                value=1000.0, 
                step=100.0,
                help="Corriente máxima de falla esperada"
            )
            
            t_c = st.number_input(
                "Tiempo de despeje de falla (s)",
                min_value=0.03,
                max_value=3.0,
                value=0.5,
                step=0.01,
                help="Tiempo de actuación de las protecciones"
            )
            
            if I_falla > 15000:
                st.warning("⚠️ Corriente de falla alta (>15kA). Se recomienda menor espaciamiento.")
        
        with col2:
            st.subheader("Parámetros del Suelo")
            resistividad = st.number_input(
                "Resistividad del suelo (Ω⋅m)", 
                min_value=1.0,
                max_value=5000.0,
                value=100.0,
                step=10.0,
                help="Resistividad del terreno natural"
            )
            
            rho_s = st.number_input(
                "Resistividad capa superficial (Ω⋅m)",
                min_value=100.0,
                max_value=10000.0,
                value=3000.0,
                step=100.0,
                help="Resistividad del material superficial (grava)"
            )
            
            T_suelo = st.number_input(
                "Temperatura del suelo (°C)",
                min_value=-20.0,
                max_value=50.0,
                value=25.0,
                step=1.0,
                help="Temperatura del suelo a profundidad de la malla"
            )
            
            if resistividad > 500:
                st.warning("⚠️ Resistividad alta. Considere tratamiento químico del suelo.")
    
    with tab2:
        st.subheader("Diseño de la Malla")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            tipo_malla = st.radio(
                "Tipo de malla",
                ["Cuadrada", "Rectangular"],
                help="Forma general de la malla"
            )
            
            # Obtener unidades para dimensiones
            unidad_longitud = st.session_state.sistema_unidades.obtener_simbolo("longitud")
            factor_longitud = st.session_state.sistema_unidades.obtener_factor("longitud")
            
            # Inicializar variables
            largo = ancho = 20.0/factor_longitud
            
            if tipo_malla == "Rectangular":
                ancho = st.slider(
                    f"Ancho de la malla ({unidad_longitud})",
                    min_value=2.0/factor_longitud,
                    max_value=100.0/factor_longitud,
                    value=20.0/factor_longitud,
                    step=1.0/factor_longitud,
                    help=f"Ancho de la malla rectangular en {unidad_longitud}"
                )
                largo = st.slider(
                    f"Largo de la malla ({unidad_longitud})",
                    min_value=2.0/factor_longitud,
                    max_value=100.0/factor_longitud,
                    value=30.0/factor_longitud,
                    step=1.0/factor_longitud,
                    help=f"Largo de la malla rectangular en {unidad_longitud}"
            )
            if largo/ancho > 2:
                    st.warning("⚠️ Relación largo/ancho >2:1. Considere una forma más cuadrada.")
            else:
                lado = st.slider(
                    f"Lado de la malla ({unidad_longitud})",
                    min_value=2.0/factor_longitud,
                    max_value=100.0/factor_longitud,
                    value=20.0/factor_longitud,
                    step=1.0/factor_longitud,
                    help=f"Longitud del lado de la malla cuadrada en {unidad_longitud}"
                )
                ancho = largo = lado
        
        with col4:            from unit_utils import obtener_parametros_campo
        params = obtener_parametros_campo(
                "Espaciamiento entre conductores",
                "longitud",
                2.0,  # valor base
                0.5,  # min
                10.0, # max
                0.5   # paso
            )
        spacing = st.slider(
                params["label"],
                min_value=params["min_value"],
                max_value=params["max_value"],
                value=params["value"],
                step=params["step"],
                help="Distancia entre conductores paralelos"
            )
            
        h = st.slider(
                "Profundidad de enterramiento (m)",
                min_value=0.3,
                max_value=3.0,
                value=0.5,
                step=0.1,
                help="Profundidad de la malla"
            )
            
        if spacing > 3:
                st.warning("⚠️ Espaciamiento grande. Mayor riesgo de potenciales peligrosos.")
            
        with col5:
            material_conductor = st.selectbox(
                "Material del conductor",
                ["Cobre", "Acero Galvanizado"],
                help="Material de los conductores de la malla"
            )
            
            diametro_conductor = st.slider(
                "Diámetro del conductor (mm)",
                min_value=8.0,
                max_value=50.0,
                value=10.0,
                step=0.5,
                help="Diámetro del conductor principal"
            )
            
            usar_varillas = st.checkbox(
                "Usar varillas verticales",
                value=True,
                help="Incluir varillas de puesta a tierra"
            )
            
            if usar_varillas:
                n_varillas = st.number_input(
                    "Número de varillas",
                    min_value=4,
                    max_value=36,
                    value=4,
                    step=4,
                    help="Cantidad total de varillas"
                )
                
                longitud_varilla = st.slider(
                    "Longitud de varillas (m)",
                    min_value=1.5,
                    max_value=6.0,
                    value=2.4,
                    step=0.3,
                    help="Longitud de cada varilla"
                )
                
                diametro_varilla = st.slider(
                    "Diámetro de varillas (mm)",
                    min_value=12.7,
                    max_value=25.4,
                    value=16.0,
                    step=0.1,
                    help="Diámetro de las varillas"
                )
    
    with tab3:
        st.subheader("Configuración de Capas del Suelo")
        col6, col7 = st.columns(2)
        
        with col6:
            n_capas = st.number_input(
                "Número de capas",
                min_value=1,
                max_value=4,
                value=2,
                help="Cantidad de capas del suelo"
            )
            
            metodo_union = st.selectbox(
                "Método de unión entre capas",
                ["Soldadura exotérmica", "Conectores mecánicos", "Conectores certificados"],
                help="Método de unión entre conductores y varillas"
            )
        
        capas = []
        for i in range(n_capas):
            st.write(f"### Capa {i+1}")
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                prof = st.slider(
                    f"Profundidad capa {i+1} (m)",
                    min_value=0.2 if i == 0 else capas[-1].profundidad + 0.2,
                    max_value=5.0,
                    value=float(i+1),
                    step=0.2,
                    help=f"Profundidad de la capa {i+1}"
                )
            
            with col_b:
                res = st.number_input(
                    f"Resistividad capa {i+1} (Ω⋅m)",
                    min_value=1.0,
                    max_value=5000.0,
                    value=100.0 * (i+1),
                    step=10.0,
                    help=f"Resistividad de la capa {i+1}"
                )
            
            with col_c:
                desc = st.text_input(
                    f"Descripción capa {i+1}",
                    value=f"Capa {i+1}",
                    help=f"Descripción del material de la capa {i+1}"
                )
            
            capas.append(CapaSuelo(prof, res, desc))
            
            if i > 0 and res < capas[i-1].resistividad * 0.5:
                st.warning(f"⚠️ Gran diferencia de resistividad entre capas {i} y {i+1}")
    
    with tab4:
        st.subheader("Visualización y Reportes")
        
        # Crear pestañas para visualización y reporte
        viz_tab, report_tab = st.tabs(["Visualizaciones", "Reporte Detallado"])
        
        with viz_tab:
            col8, col9 = st.columns(2)
            
            with col8:
                vista = st.radio(
                    "Tipo de visualización",
                    ["Malla 3D", "Mapa de calor", "Perfil del suelo", "Potenciales"],
                    help="Seleccione el tipo de visualización"
                )
            
            mostrar_varillas = st.checkbox(
                "Mostrar varillas",
                value=True,
                help="Visualizar varillas en el modelo"
            )
            
            mostrar_isolineas = st.checkbox(
                "Mostrar isolíneas",
                value=True,
                help="Mostrar líneas de igual potencial"
            )
        
        with col9:
            escala = st.select_slider(
                "Escala de colores",
                options=["Lineal", "Logarítmica"],
                value="Lineal",
                help="Escala para el mapa de colores"
            )
            
            if vista == "Potenciales":
                tipo_potencial = st.radio(
                    "Tipo de potencial",
                    ["Paso", "Contacto", "Ambos"]
                )
    
    with tab5:
        st.subheader("Análisis Avanzado")
        analisis_type = st.radio(
            "Tipo de análisis",
            ["Optimización automática", "Análisis económico", "Análisis de seguridad"]
        )
        
        if analisis_type == "Optimización automática":
            col10, col11 = st.columns(2)
            
            with col10:
                area_min = st.number_input(
                    "Área mínima (m²)",
                    min_value=4.0,
                    value=100.0,
                    help="Área mínima de la malla"
                )
                
                R_max = st.number_input(
                    "Resistencia máxima (Ω)",
                    min_value=0.1,
                    value=5.0,
                    help="Resistencia máxima permitida"
                )
            
            with col11:
                area_max = st.number_input(
                    "Área máxima (m²)",
                    min_value=area_min + 1,
                    value=1000.0,
                    help="Área máxima de la malla"
                )
                
                factor_seg = st.slider(
                    "Factor de seguridad",
                    min_value=1.0,
                    max_value=2.0,
                    value=st.session_state.factor_seg,
                    step=0.1,
                    help="Factor de seguridad adicional",
                    key="factor_seg"  # Esto vinculará el slider directamente con session_state.factor_seg
                )
        
        elif analisis_type == "Análisis económico":
            años = st.slider(
                "Período de análisis (años)",
                min_value=10,
                max_value=50,
                value=30,
                step=5,
                help="Período para análisis económico"
            )
            
            tasa_interes = st.slider(
                "Tasa de interés anual (%)",
                min_value=1.0,
                max_value=15.0,
                value=5.0,
                step=0.5,
                help="Tasa de interés para valor presente"
            )
            
            incluir_mantenimiento = st.checkbox(
                "Incluir costos de mantenimiento",
                value=True,
                help="Considerar costos de mantenimiento periódico"
            )
        
        else:  # Análisis de seguridad
            factor_temperatura = factor_temperatura_suelo(T_suelo)
            st.write(f"Factor de corrección por temperatura: {factor_temperatura:.2f}")
            
            if st.session_state.malla:
                E_paso, E_paso_max = calcular_potencial_paso(
                    I_falla, resistividad, 
                    ancho if tipo_malla == "Rectangular" else lado,
                    int(ancho/spacing) + 1, h
                )
                
                E_contacto, E_contacto_max = calcular_potencial_contacto(
                    I_falla, resistividad,
                    ancho if tipo_malla == "Rectangular" else lado,
                    int(ancho/spacing) + 1, h
                )
                
                # Métricas de seguridad
                col12, col13 = st.columns(2)
                with col12:
                    st.metric(
                        "Potencial de paso",
                        f"{E_paso:.1f} V",
                        f"{E_paso_max - E_paso:.1f} V bajo límite",
                        delta_color="normal" if E_paso < E_paso_max else "off"
                    )
                
                with col13:
                    st.metric(
                        "Potencial de contacto",
                        f"{E_contacto:.1f} V",
                        f"{E_contacto_max - E_contacto:.1f} V bajo límite",
                        delta_color="normal" if E_contacto < E_contacto_max else "off"
                    )
                    
                if E_paso > E_paso_max * 0.8 or E_contacto > E_contacto_max * 0.8:
                    st.warning("""
                    ⚠️ Potenciales cercanos a límites máximos. Considere:
                    - Reducir el espaciamiento entre conductores
                    - Aumentar el área de la malla
                    - Agregar más varillas
                    - Mejorar la resistividad superficial
                    """)

    # Botones de acción principales
    col_action1, col_action2 = st.columns(2)
    
    with col_action1:
        if st.button("Calcular y Validar", use_container_width=True):
            try:
                # Crear conductor según selección
                if material_conductor == "Cobre":
                    conductor = Conductor.get_conductor_cobre(diametro_conductor)
                else:
                    conductor = Conductor.get_conductor_acero(diametro_conductor)
                
                # Crear malla
                malla = MallaTierra(
                    ancho=ancho,
                    largo=largo,
                    espaciamiento=spacing,
                    conductor=conductor,
                    profundidad=h
                )
                
                if usar_varillas:
                    # Distribuir varillas uniformemente
                    dx = ancho / (int(n_varillas**0.5) - 1)
                    dy = largo / (int(n_varillas**0.5) - 1)
                    
                    for i in range(int(n_varillas**0.5)):
                        for j in range(int(n_varillas**0.5)):
                            malla.agregar_varilla(
                                x=i*dx,
                                y=j*dy,
                                longitud=longitud_varilla,
                                diametro=diametro_varilla
                            )
                
                st.session_state.malla = malla
                
                # Realizar cálculos básicos
                I, R_des, sigma, rho, I_falla, L, A, n_barras = calc_malla_tierra(
                    I=I,
                    R_des=5.0,  # Resistencia máxima típica
                    sigma=1/resistividad,
                    rho=resistividad,
                    I_falla=I_falla,
                    L=ancho,
                    spacing=spacing,
                    h=h,
                    conductor=conductor
                )
                
                st.success("Cálculos realizados correctamente")
            except ValidationError as e:
                st.error(f"Error de validación: {str(e)}")
            except Exception as e:
                st.error(f"Error en el cálculo: {str(e)}")
    
    with col_action2:
        if st.button("Generar Visualización", use_container_width=True):
            if st.session_state.malla:
                try:
                    if vista == "Malla 3D":
                        fig, ax = generate_malla_tierra(
                            I, 5.0, 1/resistividad, resistividad,
                            I_falla, ancho, ancho*largo, int(ancho/spacing) + 1
                        )
                        st.pyplot(fig)
                    elif vista == "Mapa de calor":
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
                    elif vista == "Perfil del suelo":
                        fig, ax = generar_perfil_suelo(
                            st.session_state.malla,
                            resistividad,
                            h,
                            rho_s
                        )
                        st.pyplot(fig)
                except Exception as e:
                    st.error(f"Error en la visualización: {str(e)}")
            else:
                st.warning("Primero debe calcular la malla")
    
    with report_tab:
        if st.session_state.malla:
            try:
                # Preparar datos para el reporte
                parametros = {
                    "Corriente de falla": f"{I_falla} A",
                    "Resistividad del suelo": f"{resistividad} Ω⋅m",
                    "Dimensiones": f"{ancho}m x {largo}m",
                    "Profundidad": f"{h} m",
                    "Material conductor": material_conductor,
                    "Número de varillas": str(n_varillas) if usar_varillas else "No usa",
                    "Método de unión": metodo_union
                }
                
                E_paso, E_paso_max = calcular_potencial_paso(
                    I_falla, resistividad, ancho, int(ancho/spacing) + 1, h
                )
                E_contacto, E_contacto_max = calcular_potencial_contacto(
                    I_falla, resistividad, ancho, int(ancho/spacing) + 1, h
                )
                
                resultados = {
                    "Potencial de paso": f"{E_paso:.2f} V",
                    "Potencial de contacto": f"{E_contacto:.2f} V",
                    "Resistencia de malla": "Pendiente de calcular",
                    "Factor de seguridad": f"{st.session_state.factor_seg:.1f}"
                }

                # Generar imágenes temporales
                os.makedirs("reportes", exist_ok=True)
                imagenes = {}
                
                # Mapa de calor
                fig1, ax1 = generar_mapa_calor(
                    I_falla,
                    resistividad,
                    st.session_state.malla,
                    calcular_potenciales_superficie(
                        st.session_state.malla,
                        I_falla,
                        resistividad
                    )
                )
                temp_path1 = os.path.join("reportes", f"temp_mapa_calor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                plt.savefig(temp_path1, format='png', dpi=300, bbox_inches='tight')
                plt.close(fig1)
                imagenes["Distribución de Potenciales"] = temp_path1

                # Perfil del suelo
                fig2, ax2 = generar_perfil_suelo(
                    st.session_state.malla,
                    resistividad,
                    h,
                    rho_s
                )
                temp_path2 = os.path.join("reportes", f"temp_perfil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                plt.savefig(temp_path2, format='png', dpi=300, bbox_inches='tight')
                plt.close(fig2)
                imagenes["Perfil del Suelo"] = temp_path2

                # Generar reporte markdown y mostrarlo
                reporte_md = generar_reporte_markdown(
                    st.session_state.malla,
                    parametros,
                    resultados,
                    imagenes
                )
                
                st.markdown(reporte_md)

                # Generar nombre único para el reporte
                fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Botones de descarga
                col_md, col_pdf = st.columns(2)
                
                with col_md:
                    nombre_md = f"reporte_malla_{fecha_hora}.md"
                    st.download_button(
                        label="📝 Descargar Reporte MD",
                        data=reporte_md,
                        file_name=nombre_md,
                        mime="text/markdown",
                        use_container_width=True
                    )

                with col_pdf:
                    nombre_pdf = f"reporte_malla_{fecha_hora}.pdf"
                    try:
                        ruta_pdf = generar_reporte_pdf(
                            st.session_state.malla,
                            parametros,
                            resultados,
                            nombre_pdf
                        )
                        
                        if os.path.exists(ruta_pdf):
                            with open(ruta_pdf, "rb") as pdf_file:
                                st.download_button(
                                    label="📄 Descargar Reporte PDF",
                                    data=pdf_file.read(),
                                    file_name=nombre_pdf,
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                        else:
                            st.error("Error: No se pudo generar el archivo PDF")
                    except Exception as e:
                        st.error(f"Error al generar el PDF: {str(e)}")

                # Limpiar archivos temporales
                try:
                    for imagen in imagenes.values():
                        if os.path.exists(imagen):
                            os.remove(imagen)
                except Exception:
                    pass
                        
            except Exception as e:
                st.error(f"Error al generar el reporte: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
        else:
            st.warning("Primero debe calcular la malla")


if __name__ == "__main__":
    run_app()
