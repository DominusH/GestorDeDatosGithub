#!/usr/bin/env python3
"""
Script para recrear la base de datos SQLite desde cero
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def recreate_database():
    """Recrea la base de datos SQLite desde cero"""
    print("=== RECREANDO BASE DE DATOS SQLITE ===")
    
    try:
        from flask import Flask
        from models import db, Usuario, Contacto
        from werkzeug.security import generate_password_hash
        
        # Crear aplicación Flask
        app = Flask(__name__)
        app.config.from_object('config.Config')
        db.init_app(app)
        
        with app.app_context():
            # Obtener ruta de la base de datos
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            # Eliminar archivo de base de datos existente
            if os.path.exists(db_path):
                os.remove(db_path)
                print(f"✓ Base de datos anterior eliminada: {db_path}")
            
            # Crear nueva base de datos
            db.create_all()
            print("✓ Nueva base de datos SQLite creada exitosamente")
            
            # Verificar que las tablas se crearon
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✓ Tablas creadas: {', '.join(tables)}")
            
            # Crear usuario administrador por defecto
            admin_email = "matvaltino@gmail.com"
            admin_user = Usuario(
                email=admin_email,
                password=generate_password_hash("admin123"),
                is_admin=True,
                email_confirmed=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"✓ Usuario administrador creado: {admin_email}")
            
            # Verificar tamaño del archivo
            if os.path.exists(db_path):
                size_mb = os.path.getsize(db_path) / (1024 * 1024)
                print(f"✓ Tamaño de la base de datos: {size_mb:.2f} MB")
            
            print("\n=== BASE DE DATOS SQLITE RECREADA EXITOSAMENTE ===")
            print("Credenciales por defecto:")
            print(f"Email: {admin_email}")
            print("Password: admin123")
            print("IMPORTANTE: Cambia la contraseña después del primer login")
            print(f"Ubicación: {db_path}")
            
            return True
            
    except Exception as e:
        print(f"✗ Error al recrear la base de datos: {e}")
        return False

if __name__ == "__main__":
    success = recreate_database()
    sys.exit(0 if success else 1) 