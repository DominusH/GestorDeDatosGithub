#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar que las descargas de Excel funcionen correctamente
"""

import os
import sys
import tempfile
import shutil

def test_excel_generation():
    """Probar la generación de archivos Excel"""
    try:
        # Importar las librerías necesarias
        import pandas as pd
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill
        
        print("✅ Librerías importadas correctamente")
        
        # Crear datos de prueba
        data = [
            {
                "Origen": "Propio",
                "Cobertura Actual": "OSDE",
                "¿Por qué no toma la cobertura?": "No puede pagarlo",
                "Privado/Desregulado": "Privado",
                "Apellido y nombre": "Juan Pérez",
                "Correo electrónico": "juan@test.com",
                "Edad titular": "35",
                "Teléfono": "123456789",
                "Grupo familiar": "2",
                "Plan ofrecido": "Plan Premium",
                "Estado": "cerrado",
                "Observaciones": "Cliente interesado",
                "Cónyuge": "Con cónyuge",
                "Edad cónyuge": "32",
                "Fecha de carga": "04/07/2025",
                "Usuario cargador": "admin@test.com"
            }
        ]
        
        df = pd.DataFrame(data)
        print("✅ Datos de prueba creados")
        
        # Crear directorio temporal
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            print("✅ Directorio temporal creado")
        
        # Crear archivo Excel
        filename = "test_export.xlsx"
        file_path = os.path.join(temp_dir, filename)
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Test"
        
        # Agregar datos
        for r in openpyxl.utils.dataframe.dataframe_to_rows(df, index=False, header=True):
            ws.append(r)
        
        # Guardar archivo
        wb.save(file_path)
        print(f"✅ Archivo Excel creado: {file_path}")
        
        # Verificar que el archivo existe
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ Archivo verificado - Tamaño: {file_size} bytes")
            
            # Limpiar archivo de prueba
            os.remove(file_path)
            print("✅ Archivo de prueba eliminado")
            
            return True
        else:
            print("❌ Error: El archivo no se creó correctamente")
            return False
            
    except ImportError as e:
        print(f"❌ Error al importar librerías: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def test_directory_permissions():
    """Probar permisos de directorio"""
    try:
        # Probar directorio actual
        current_dir = os.getcwd()
        print(f"✅ Directorio actual: {current_dir}")
        
        # Probar directorio temporal
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Probar escritura
        test_file = os.path.join(temp_dir, 'test_write.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        
        # Probar lectura
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Limpiar
        os.remove(test_file)
        
        print("✅ Permisos de directorio verificados")
        return True
        
    except Exception as e:
        print(f"❌ Error en permisos: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🧪 Iniciando pruebas de descarga de Excel...")
    print("=" * 50)
    
    # Probar permisos
    if not test_directory_permissions():
        print("❌ Falló la prueba de permisos")
        return False
    
    # Probar generación de Excel
    if not test_excel_generation():
        print("❌ Falló la prueba de generación de Excel")
        return False
    
    print("=" * 50)
    print("✅ Todas las pruebas pasaron correctamente")
    print("🎉 El sistema de descargas debería funcionar en PythonAnywhere")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 