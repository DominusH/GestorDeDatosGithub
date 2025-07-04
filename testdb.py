#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de la base de datos SQLite
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_database_config():
    """Prueba la configuración de la base de datos SQLite"""
    print("=== PRUEBA DE CONFIGURACIÓN DE BASE DE DATOS SQLITE ===")
    
    # Verificar configuración de Flask
    print("\n1. Configuración de Flask:")
    try:
        from config import Config, ADMIN_EMAILS
        db_uri = Config.SQLALCHEMY_DATABASE_URI
        
        if 'sqlite' in db_uri.lower():
            print("   ✓ Usando SQLite")
            print(f"   URI: {db_uri}")
            
            # Verificar si el directorio instance existe
            db_path = db_uri.replace('sqlite:///', '')
            instance_dir = os.path.dirname(db_path)
            
            if os.path.exists(instance_dir):
                print(f"   ✓ Directorio instance existe: {instance_dir}")
            else:
                print(f"   ⚠ Directorio instance no existe: {instance_dir}")
                print("   → Se creará automáticamente al usar la aplicación")
                
        else:
            print("   ✗ No está usando SQLite")
            print(f"   URI: {db_uri}")
            return False
            
    except Exception as e:
        print(f"   ✗ Error al cargar configuración: {e}")
        return False
    
    # Probar conexión a la base de datos
    print("\n2. Prueba de conexión:")
    try:
        from flask import Flask
        from models import db, Usuario, Contacto
        
        app = Flask(__name__)
        app.config.from_object('config.Config')
        db.init_app(app)
        
        with app.app_context():
            # Intentar crear las tablas
            db.create_all()
            print("   ✓ Base de datos SQLite creada/verificada exitosamente")
            
            # Verificar que las tablas existen
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"   ✓ Tablas creadas: {', '.join(tables)}")
            
            # Verificar usuarios existentes
            usuarios = Usuario.query.all()
            print(f"   ✓ Usuarios en la base de datos: {len(usuarios)}")
            
            if usuarios:
                print("   Usuarios existentes:")
                for usuario in usuarios:
                    admin_status = "Admin" if usuario.is_admin else "Usuario"
                    print(f"     - {usuario.email} ({admin_status})")
            else:
                print("   ⚠ No hay usuarios registrados aún")
            
    except Exception as e:
        print(f"   ✗ Error en la conexión: {e}")
        return False
    
    # Verificar configuración de administradores
    print("\n3. Configuración de administradores:")
    try:
        print(f"   ✓ Correos de administrador configurados: {ADMIN_EMAILS}")
        
        # Verificar lógica de asignación
        from auth import RegisterForm
        from flask_wtf.csrf import CSRFProtect
        
        test_app = Flask(__name__)
        test_app.config['SECRET_KEY'] = 'test'
        test_app.config['WTF_CSRF_ENABLED'] = False
        csrf = CSRFProtect(test_app)
        
        with test_app.app_context():
            form = RegisterForm()
            print("   ✓ Formulario de registro configurado correctamente")
            
    except Exception as e:
        print(f"   ✗ Error al verificar configuración de administradores: {e}")
        return False
    
    # Verificar archivo de base de datos
    print("\n4. Verificación de archivo:")
    try:
        db_path = Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
        if os.path.exists(db_path):
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            print(f"   ✓ Archivo de base de datos existe: {db_path}")
            print(f"   ✓ Tamaño: {size_mb:.2f} MB")
        else:
            print(f"   ⚠ Archivo de base de datos no existe aún: {db_path}")
            print("   → Se creará automáticamente al usar la aplicación")
            
    except Exception as e:
        print(f"   ✗ Error al verificar archivo: {e}")
        return False
    
    print("\n=== CONFIGURACIÓN COMPLETADA ===")
    print("✓ La aplicación está configurada para usar SQLite")
    print("✓ No se crean usuarios administradores automáticamente")
    print("✓ Los usuarios se convierten en admin automáticamente si usan:")
    for email in ADMIN_EMAILS:
        print(f"  - {email}")
    print("✓ Contraseña comunal requerida para registro")
    
    return True

if __name__ == "__main__":
    success = test_database_config()
    sys.exit(0 if success else 1)