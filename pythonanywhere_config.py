#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuración específica para PythonAnywhere
"""

import os
import sys

# Configurar el entorno para PythonAnywhere
def setup_pythonanywhere():
    """Configurar el entorno para PythonAnywhere"""
    
    # Agregar el directorio del proyecto al path
    project_path = os.path.dirname(os.path.abspath(__file__))
    if project_path not in sys.path:
        sys.path.append(project_path)
    
    # Configurar variables de entorno
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = '0'
    
    # Crear directorios necesarios
    directories = ['temp', 'logs', 'instance']
    for directory in directories:
        dir_path = os.path.join(project_path, directory)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"Directorio creado: {dir_path}")
            except Exception as e:
                print(f"Error creando directorio {dir_path}: {e}")
    
    # Configurar logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(project_path, 'logs', 'app.log')),
            logging.StreamHandler()
        ]
    )
    
    print("Configuración de PythonAnywhere completada")

if __name__ == "__main__":
    setup_pythonanywhere() 