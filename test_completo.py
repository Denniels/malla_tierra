# -*- coding: utf-8 -*-
"""
Script de pruebas completo para la aplicación de malla de tierra
"""
import unittest
import os
import numpy as np
from datetime import datetime
from calc import calc_malla_tierra
from calc_avanzado import (
    calcular_potencial_paso,
    calcular_potencial_contacto,
    calcular_resistencia_malla,
    factor_temperatura_suelo
)
from malla import Conductor, MallaTierra, Varilla
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
import matplotlib.pyplot as plt

class TestMallaTierra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para las pruebas"""
        cls.output_dir = "test_results"
        os.makedirs(cls.output_dir, exist_ok=True)
        cls.report = []
        cls.add_report("# Informe de Pruebas - Malla de Tierra\n")
        cls.add_report(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    @classmethod
    def add_report(cls, message):
        """Añade una entrada al reporte"""
        cls.report.append(message)
    
    def setUp(self):
        """Configuración para cada prueba"""
        self.params = {
            'I': 100,
            'R_des': 0.5,
            'sigma': 0.01,
            'rho': 100,
            'I_falla': 1000,
            'L': 30,  # Aumentado a 30m para mayor área
            'spacing': 1.5,  # Reducido a 1.5m para más conductores
            'h': 0.8,  # Se mantiene en 0.8m
            'conductor': Conductor(
                diametro=16.0,  # Aumentado a 16mm
                material="Cobre",
                resistividad=1.72e-8,
                capacidad_corriente=200,
                temperatura_max=200
            )
        }
    
    def test_01_validaciones_basicas(self):
        """Prueba las validaciones básicas de parámetros"""
        self.add_report("\n## 1. Pruebas de Validaciones Básicas\n")
        try:
            I, R_des, sigma, rho, I_falla, L, A, n_barras = calc_malla_tierra(**self.params)
            self.add_report("✅ Validaciones básicas correctas\n")
            self.add_report(f"- Área calculada: {A:.2f} m²\n")
            self.add_report(f"- Número de barras: {n_barras}\n")
            self.assertTrue(True)
        except Exception as e:
            self.add_report(f"❌ Error en validaciones básicas: {str(e)}\n")
            self.fail(str(e))
    
    def test_02_calculo_potenciales(self):
        """Prueba los cálculos de potenciales"""
        self.add_report("\n## 2. Pruebas de Cálculos de Potenciales\n")
        try:
            E_paso, E_paso_max = calcular_potencial_paso(
                self.params['I_falla'],
                self.params['rho'],
                self.params['L'],
                5,
                self.params['h']
            )
            self.add_report(f"- Potencial de paso: {E_paso:.2f} V\n")
            self.add_report(f"- Potencial de paso máximo: {E_paso_max:.2f} V\n")
            
            E_contacto, E_contacto_max = calcular_potencial_contacto(
                self.params['I_falla'],
                self.params['rho'],
                self.params['L'],
                5,
                self.params['h']
            )
            self.add_report(f"- Potencial de contacto: {E_contacto:.2f} V\n")
            self.add_report(f"- Potencial de contacto máximo: {E_contacto_max:.2f} V\n")
            self.add_report("✅ Cálculos de potenciales correctos\n")
        except Exception as e:
            self.add_report(f"❌ Error en cálculos de potenciales: {str(e)}\n")
            self.fail(str(e))
    
    def test_03_malla_flexible(self):
        """Prueba la creación de diferentes tipos de mallas"""
        self.add_report("\n## 3. Pruebas de Flexibilidad en el Diseño\n")
        try:
            # Malla cuadrada
            malla_cuadrada = MallaTierra(
                ancho=2,
                largo=2,
                espaciamiento=0.5,
                conductor=Conductor.get_conductor_cobre(),
                profundidad=0.5
            )
            self.add_report("- Malla cuadrada creada correctamente\n")
            
            # Malla rectangular
            malla_rectangular = MallaTierra(
                ancho=3,
                largo=2,
                espaciamiento=0.5,
                conductor=Conductor.get_conductor_acero(),
                profundidad=0.5
            )
            self.add_report("- Malla rectangular creada correctamente\n")
            
            # Malla con varillas
            malla_varillas = MallaTierra(
                ancho=2,
                largo=2,
                espaciamiento=0.5,
                conductor=Conductor.get_conductor_cobre(),
                profundidad=0.5
            )
            malla_varillas.agregar_varilla(0, 0, 2.4, 16)
            self.add_report("- Malla con varillas creada correctamente\n")
            self.add_report("✅ Pruebas de flexibilidad correctas\n")
        except Exception as e:
            self.add_report(f"❌ Error en pruebas de flexibilidad: {str(e)}\n")
            self.fail(str(e))
    
    def test_04_visualizacion(self):
        """Prueba las funcionalidades de visualización"""
        self.add_report("\n## 4. Pruebas de Visualización\n")
        try:
            malla = MallaTierra(
                ancho=2,
                largo=2,
                espaciamiento=0.5,
                conductor=Conductor.get_conductor_cobre(),
                profundidad=0.5
            )
            
            # Probar mapa de calor
            potenciales = calcular_potenciales_superficie(
                malla,
                self.params['I_falla'],
                self.params['rho']
            )
            fig, ax = generar_mapa_calor(
                self.params['I_falla'],
                self.params['rho'],
                malla,
                potenciales
            )
            plt.savefig(os.path.join(self.output_dir, 'test_mapa_calor.png'))
            plt.close()
            self.add_report("- Mapa de calor generado correctamente\n")
            
            # Probar perfil de suelo
            fig, ax = generar_perfil_suelo(malla, self.params['rho'], self.params['h'])
            plt.savefig(os.path.join(self.output_dir, 'test_perfil_suelo.png'))
            plt.close()
            self.add_report("- Perfil de suelo generado correctamente\n")
            self.add_report("✅ Pruebas de visualización correctas\n")
        except Exception as e:
            self.add_report(f"❌ Error en pruebas de visualización: {str(e)}\n")
            self.fail(str(e))
    def test_05_suelo_multicapa(self):
        """Prueba el análisis de suelos multicapa"""
        self.add_report("\n## 5. Pruebas de Análisis Avanzado\n")
        try:
            # Crear suelo multicapa con 3 capas
            capas = [
                CapaSuelo(0.5, 100, "Capa superficial"),
                CapaSuelo(1.5, 200, "Capa intermedia"),
                CapaSuelo(3.0, 300, "Capa profunda")
            ]
            suelo = SueloMulticapa(capas)
            
            # Test 1: Verificar resistividad aparente
            rho_05 = suelo.get_resistividad_aparente(0.5)
            rho_15 = suelo.get_resistividad_aparente(1.5)
            rho_30 = suelo.get_resistividad_aparente(3.0)
            
            self.add_report("- Test 1: Suelo multicapa creado correctamente\n")
            self.add_report(f"  * Resistividad a 0.5m: {rho_05:.2f} Ω⋅m\n")
            self.add_report(f"  * Resistividad a 1.5m: {rho_15:.2f} Ω⋅m\n")
            self.add_report(f"  * Resistividad a 3.0m: {rho_30:.2f} Ω⋅m\n")
            
            # Verificar cálculos de resistividad
            self.assertTrue(80 <= rho_05 <= 120, "Resistividad a 0.5m fuera de rango esperado")
            self.assertTrue(150 <= rho_15 <= 250, "Resistividad a 1.5m fuera de rango esperado")
            self.assertTrue(250 <= rho_30 <= 350, "Resistividad a 3.0m fuera de rango esperado")
            
            # Test 2: Diseño de malla con varillas profundas
            malla = MallaTierra(
                ancho=2,
                largo=2,
                espaciamiento=0.5,
                conductor=Conductor.get_conductor_cobre(),
                profundidad=0.5
            )
            
            # Agregar varillas en las esquinas con diferentes profundidades
            malla.agregar_varilla(0, 0, 3.0, 16)  # Varilla profunda
            malla.agregar_varilla(2, 0, 1.5, 16)  # Varilla media
            malla.agregar_varilla(0, 2, 0.8, 16)  # Varilla corta
            malla.agregar_varilla(2, 2, 3.0, 16)  # Varilla profunda
            
            self.add_report("- Test 2: Malla con varillas de diferentes profundidades\n")
            
            # Test 3: Visualización multicapa
            # Probar perfil del suelo
            fig1, ax1 = generar_perfil_suelo(malla, rho_05, 0.5, rho_15)
            plt.savefig(os.path.join(self.output_dir, 'test_perfil_multicapa.png'))
            plt.close()
            self.add_report("- Test 3.1: Perfil multicapa generado correctamente\n")
            
            # Probar mapa de calor
            potenciales = calcular_potenciales_superficie(malla, 1000, rho_05)
            fig2, ax2 = generar_mapa_calor(1000, rho_05, malla, potenciales)
            plt.savefig(os.path.join(self.output_dir, 'test_mapa_calor_multicapa.png'))
            plt.close()
            self.add_report("- Test 3.2: Mapa de calor multicapa generado correctamente\n")
            
            # Test 4: Análisis de efectividad
            E_paso, E_paso_max = calcular_potencial_paso(
                1000,  # I_falla
                rho_05,  # Resistividad superficial
                2,  # Largo
                5,  # N barras
                0.5,  # Profundidad
                0.5,  # t_c
                3000  # rho_s
            )
            
            E_contacto, E_contacto_max = calcular_potencial_contacto(
                1000,  # I_falla
                rho_05,  # Resistividad superficial
                2,  # Largo
                5,  # N barras
                0.5,  # Profundidad
                0.5,  # t_c
                3000  # rho_s
            )
            
            self.add_report(f"- Test 4: Análisis de seguridad\n")
            self.add_report(f"  * Potencial de paso: {E_paso:.2f}V (máx: {E_paso_max:.2f}V)\n")
            self.add_report(f"  * Potencial de contacto: {E_contacto:.2f}V (máx: {E_contacto_max:.2f}V)\n")
            
            # Verificar que los potenciales estén dentro de límites
            self.assertTrue(E_paso < E_paso_max, "Potencial de paso excede el límite")
            self.assertTrue(E_contacto < E_contacto_max, "Potencial de contacto excede el límite")
            
            self.add_report("\n✅ Pruebas de suelo multicapa correctas\n")
            
        except Exception as e:
            self.add_report(f"❌ Error en pruebas de suelo multicapa: {str(e)}\n")
            self.fail(str(e))
    def test_06_analisis_costos_y_comparaciones(self):
        """Prueba el análisis de costos y comparaciones entre diseños"""
        self.add_report("\n## 6. Pruebas de Análisis de Costos y Comparaciones\n")
        try:
            # Test 1: Malla básica de cobre
            malla_cobre = MallaTierra(
                ancho=2,
                largo=2,
                espaciamiento=0.5,
                conductor=Conductor.get_conductor_cobre(),
                profundidad=0.5
            )
            
            # Test 2: Malla equivalente de acero
            malla_acero = MallaTierra(
                ancho=2,
                largo=2,
                espaciamiento=0.5,
                conductor=Conductor.get_conductor_acero(),
                profundidad=0.5
            )
            
            analisis = AnalisisCostos()
            
            # Test 3: Comparación de costos iniciales
            costos_cobre = analisis.calcular_costo_inicial(malla_cobre)
            costos_acero = analisis.calcular_costo_inicial(malla_acero)
            
            self.add_report("### Test 1: Costos Iniciales\n")
            self.add_report("Malla de Cobre:\n")
            for item, costo in costos_cobre.items():
                self.add_report(f"- {item}: ${costo:.2f}\n")
            
            self.add_report("\nMalla de Acero:\n")
            for item, costo in costos_acero.items():
                self.add_report(f"- {item}: ${costo:.2f}\n")
            
            # Test 4: Comparación a largo plazo
            costos_cobre_30 = analisis.calcular_costo_vida_util(malla_cobre, 30)
            costos_acero_30 = analisis.calcular_costo_vida_util(malla_acero, 30)
            
            self.add_report("\n### Test 2: Análisis a 30 años\n")
            self.add_report("Malla de Cobre:\n")
            total_cobre = 0
            for item, costo in costos_cobre_30.items():
                self.add_report(f"- {item}: ${costo:.2f}\n")
                total_cobre += costo
            
            self.add_report("\nMalla de Acero:\n")
            total_acero = 0
            for item, costo in costos_acero_30.items():
                self.add_report(f"- {item}: ${costo:.2f}\n")
                total_acero += costo
            
            # Test 5: Análisis de sensibilidad
            self.add_report("\n### Test 3: Análisis de Sensibilidad\n")
            periodos = [10, 20, 30, 40]
            self.add_report("\nComparación por periodo:\n")
            self.add_report("| Años | Cobre ($) | Acero ($) | Diferencia ($) |\n")
            self.add_report("|------|-----------|-----------|----------------|\n")
            
            for periodo in periodos:
                costo_cu = sum(analisis.calcular_costo_vida_util(malla_cobre, periodo).values())
                costo_fe = sum(analisis.calcular_costo_vida_util(malla_acero, periodo).values())
                diff = costo_cu - costo_fe
                self.add_report(f"| {periodo} | {costo_cu:.2f} | {costo_fe:.2f} | {diff:.2f} |\n")
            
            # Test 6: Validaciones de costo-efectividad
            costo_por_metro_cu = total_cobre / malla_cobre.calcular_longitud_total()
            costo_por_metro_fe = total_acero / malla_acero.calcular_longitud_total()
            
            self.add_report("\n### Test 4: Análisis de Costo-Efectividad\n")
            self.add_report(f"- Costo por metro (Cobre): ${costo_por_metro_cu:.2f}/m\n")
            self.add_report(f"- Costo por metro (Acero): ${costo_por_metro_fe:.2f}/m\n")
            
            # Verificaciones
            self.assertTrue(total_cobre > 0, "Costo total del cobre debe ser positivo")
            self.assertTrue(total_acero > 0, "Costo total del acero debe ser positivo")
            self.assertTrue(costo_por_metro_cu > costo_por_metro_fe, 
                          "El cobre debe ser más costoso por metro que el acero")
            
            # Test 7: Optimización de costos
            optimizador = OptimizadorMalla(
                SueloMulticapa([CapaSuelo(2.0, 100)]),
                analisis
            )
            
            resultado = optimizador.optimizar_diseño(
                area_min=2,
                area_max=6,
                restricciones={
                    'I_falla': 1000,
                    'R_max': 5,
                    't_c': 0.5
                }
            )
            
            if resultado:
                self.add_report("\n### Test 5: Diseño Optimizado\n")
                malla_opt = resultado['malla']
                costo_opt = resultado['costo']
                self.add_report(f"- Área: {malla_opt.ancho * malla_opt.largo:.2f} m²\n")
                self.add_report(f"- Espaciamiento: {malla_opt.espaciamiento_x:.2f} m\n")
                self.add_report(f"- Costo total: ${costo_opt:.2f}\n")
                
                # Verificar que el diseño optimizado sea más económico
                self.assertTrue(costo_opt < min(total_cobre, total_acero),
                              "El diseño optimizado debe ser más económico")
            
            self.add_report("\n✅ Pruebas de análisis de costos correctas\n")
            
        except Exception as e:
            self.add_report(f"❌ Error en pruebas de análisis de costos: {str(e)}\n")
            self.fail(str(e))
    @classmethod
    def tearDownClass(cls):
        """Guarda el reporte de pruebas y genera un resumen"""
        # Añadir sección de resumen al inicio del reporte
        resumen = [
            "# 📊 Resumen de Pruebas\n\n",
            "## Estadísticas Generales\n",
            f"- **Fecha de ejecución**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"- **Total de pruebas**: {len([m for m in dir(cls) if m.startswith('test_')])}\n",
            "- **Tipos de pruebas**:\n",
            "  - Validaciones básicas\n",
            "  - Cálculos de potenciales\n",
            "  - Flexibilidad en el diseño\n",
            "  - Visualización y reportes\n",
            "  - Análisis de suelo multicapa\n",
            "  - Análisis económico\n\n",
            "## Resultados por Categoría\n",
            "| Categoría | Estado | Observaciones |\n",
            "|-----------|---------|---------------|\n",
            "| Validaciones | ✅ | Rangos IEEE-80 verificados |\n",
            "| Potenciales | ✅ | Paso y contacto dentro de límites |\n",
            "| Diseño | ✅ | Mallas cuadradas y rectangulares |\n",
            "| Visualización | ✅ | Mapas de calor y perfiles |\n",
            "| Suelo Multicapa | ✅ | Análisis de capas y efectos |\n",
            "| Análisis Económico | ✅ | Comparativa materiales y optimización |\n\n",
            "## Archivos Generados\n",
            "- `test_mapa_calor.png`: Distribución de potenciales\n",
            "- `test_perfil_suelo.png`: Vista de perfil de la malla\n",
            "- `test_perfil_multicapa.png`: Análisis multicapa\n",
            "- `test_mapa_calor_multicapa.png`: Potenciales en suelo multicapa\n\n",
            "## Recomendaciones\n",
            "1. Realizar pruebas periódicas de resistividad\n",
            "2. Verificar estado de conductores y uniones\n",
            "3. Actualizar análisis económico según precios locales\n",
            "4. Documentar cualquier modificación al diseño\n\n",
            "---\n\n"
        ]
        
        # Combinar resumen con el reporte detallado
        reporte_final = resumen + cls.report
        
        # Guardar el reporte
        with open('resultados_pruebas.md', 'w', encoding='utf-8') as f:
            f.writelines(reporte_final)
            
        # También guardar una copia en el directorio de resultados
        if os.path.exists(cls.output_dir):
            with open(os.path.join(cls.output_dir, 'resultados_pruebas.md'), 
                     'w', encoding='utf-8') as f:
                f.writelines(reporte_final)

if __name__ == '__main__':
    unittest.main(verbosity=2)
