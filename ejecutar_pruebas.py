#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para ejecutar todas las pruebas y generar un informe detallado
"""
import unittest
import sys
import os
from datetime import datetime
import traceback
from io import StringIO

def ejecutar_pruebas_y_generar_informe():
    # Configurar el directorio de salida
    output_dir = "informes"
    os.makedirs(output_dir, exist_ok=True)
    
    # Nombre del archivo de informe
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    informe_path = os.path.join(output_dir, f"informe_pruebas_{timestamp}.md")
    
    # Lista de módulos de prueba a ejecutar
    modulos_prueba = [
        "test_completo",
        "test_malla",
        "test_resistividad",
        "test_visualizacion",
        "test_historial"
    ]
    
    # Iniciar el informe
    contenido_informe = [
        "# Informe de Pruebas - Sistema de Malla de Tierra",
        f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "\n## Resumen de Ejecución\n"
    ]
    
    total_pruebas = 0
    pruebas_exitosas = 0
    pruebas_fallidas = 0
    pruebas_error = 0
    
    # Ejecutar cada módulo de pruebas
    for modulo in modulos_prueba:
        contenido_informe.append(f"\n### Módulo: {modulo}\n")
        
        try:
            # Redireccionar stdout para capturar la salida
            stdout_original = sys.stdout
            sys.stdout = StringIO()
            
            # Cargar y ejecutar las pruebas
            suite = unittest.defaultTestLoader.loadTestsFromName(modulo)
            resultado = unittest.TextTestRunner(stream=sys.stdout).run(suite)
            
            # Recuperar la salida
            output = sys.stdout.getvalue()
            sys.stdout = stdout_original
            
            # Actualizar contadores
            total_pruebas += resultado.testsRun
            pruebas_fallidas += len(resultado.failures)
            pruebas_error += len(resultado.errors)
            pruebas_exitosas += resultado.testsRun - len(resultado.failures) - len(resultado.errors)
            
            # Agregar resultados al informe
            contenido_informe.append("```")
            contenido_informe.append(output)
            contenido_informe.append("```\n")
            
            # Agregar detalles de fallos si los hay
            if resultado.failures:
                contenido_informe.append("#### Fallos Detallados\n")
                for test, error in resultado.failures:
                    contenido_informe.append(f"**{test}**\n")
                    contenido_informe.append("```python")
                    contenido_informe.append(error)
                    contenido_informe.append("```\n")
            
            if resultado.errors:
                contenido_informe.append("#### Errores Detallados\n")
                for test, error in resultado.errors:
                    contenido_informe.append(f"**{test}**\n")
                    contenido_informe.append("```python")
                    contenido_informe.append(error)
                    contenido_informe.append("```\n")
                    
        except Exception as e:
            contenido_informe.append(f"❌ Error al ejecutar el módulo: {str(e)}\n")
            contenido_informe.append("```python")
            contenido_informe.append(traceback.format_exc())
            contenido_informe.append("```\n")
            pruebas_error += 1
    
    # Agregar resumen estadístico
    contenido_informe.insert(3, "\n### Estadísticas Globales\n")
    contenido_informe.insert(4, f"- Total de pruebas ejecutadas: {total_pruebas}")
    contenido_informe.insert(5, f"- Pruebas exitosas: {pruebas_exitosas}")
    contenido_informe.insert(6, f"- Pruebas fallidas: {pruebas_fallidas}")
    contenido_informe.insert(7, f"- Pruebas con error: {pruebas_error}")
    contenido_informe.insert(8, f"- Porcentaje de éxito: {(pruebas_exitosas/total_pruebas*100):.2f}%\n")
    
    # Escribir el informe
    with open(informe_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(contenido_informe))
    
    print(f"\nInforme generado en: {informe_path}")
    return informe_path

if __name__ == '__main__':
    informe_path = ejecutar_pruebas_y_generar_informe()
