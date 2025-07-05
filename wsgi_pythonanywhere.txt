# This file contains the WSGI configuration required to serve up your
# web application at http://<your-username>.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
# description.
#
# The below has been auto-generated for your Flask project

import sys
import os

# add your project directory to the sys.path
project_home = '/home/DominusHevno/GestorDeDatosGithub'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Configurar variables de entorno
os.environ['SECRET_KEY'] = 'BbOpcztegL8Z9vKyxDA2SV7Qvz7eH4UTTYgW79Q8kVigRkLJ0v'
os.environ['MAIL_USERNAME'] = 'bot1gestordecontactos@gmail.com'
os.environ['MAIL_PASSWORD'] = 'thaotgttamsyqrik'
os.environ['MAIL_SERVER'] = 'smtp.gmail.com'
os.environ['MAIL_PORT'] = '587'
os.environ['MAIL_USE_TLS'] = 'True'
os.environ['MAIL_DEFAULT_SENDER'] = 'bot1gestordecontactos@gmail.com'
os.environ['COMMUNITY_PASSWORD'] = '20gestor25'

# Configurar entorno para PythonAnywhere
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Crear directorios necesarios para descargas
directories = ['temp', 'logs', 'instance']
for directory in directories:
    dir_path = os.path.join(project_home, directory)
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"Directorio creado: {dir_path}")
        except Exception as e:
            print(f"Error creando directorio {dir_path}: {e}")

# Configurar logging para debugging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(project_home, 'logs', 'app.log')),
        logging.StreamHandler()
    ]
)

# import flask app but need to call it "application" for WSGI to work
try:
    from gestor import gestor as application  # noqa
    print("Aplicación Flask cargada exitosamente")
    
    # Configurar la aplicación para producción
    application.config['DEBUG'] = False
    application.config['TESTING'] = False
    
    # Asegurar que la base de datos se cree
    with application.app_context():
        try:
            from models import db
            db.create_all()
            print("Base de datos SQLite creada/verificada exitosamente")
        except Exception as e:
            print(f"Error al crear base de datos: {e}")
    
except Exception as e:
    print(f"Error cargando la aplicación: {e}")
    
    # Crear una aplicación de fallback
    from flask import Flask, jsonify
    
    def create_fallback_app():
        app = Flask(__name__)
        
        @app.route('/')
        def fallback():
            return jsonify({
                'error': 'Error en la aplicación',
                'message': str(e),
                'status': 'error'
            }), 500
        
        @app.route('/<path:path>')
        def catch_all(path):
            return jsonify({
                'error': 'Ruta no disponible',
                'path': path,
                'status': 'error'
            }), 404
        
        return app
    
    application = create_fallback_app()

# Middleware para manejar descargas en PythonAnywhere
from flask import request

@application.after_request
def add_download_headers(response):
    """Agregar headers específicos para descargas de archivos"""
    if request.path.startswith('/exportar'):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        # Asegurar que el archivo se descargue correctamente
        if 'Content-Disposition' in response.headers:
            response.headers['Content-Disposition'] = response.headers['Content-Disposition'].replace('attachment; ', 'attachment; filename*=UTF-8\'\'')
    return response

print("Configuración WSGI completada para PythonAnywhere") 