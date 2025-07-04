from gestor import gestor, db
from models import Usuario, Contacto

def reset_database():
    with gestor.app_context():
        # Eliminar todos los contactos primero (debido a la clave foránea)
        Contacto.query.delete()
        # Eliminar todos los usuarios
        Usuario.query.delete()
        # Confirmar los cambios
        db.session.commit()
        print("Base de datos reseteada exitosamente")

if __name__ == "__main__":
    reset_database() 