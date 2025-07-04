from gestor import gestor, db
from models import Usuario, Contacto
import logging

def recreate_database():
    with gestor.app_context():
        # Eliminar todas las tablas
        db.drop_all()
        logging.info("Base de datos eliminada")
        
        # Crear todas las tablas nuevamente
        db.create_all()
        logging.info("Tablas creadas")
        
        try:
            db.session.commit()
            print("Base de datos recreada exitosamente")
        except Exception as e:
            print(f"Error al recrear la base de datos: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    recreate_database() 