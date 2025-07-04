from gestor import gestor, db
from models import Usuario
import logging

def eliminar_usuarios():
    with gestor.app_context():
        try:
            # Lista de correos a eliminar
            correos = ["matvaltino@gmail.com", "walter.vega@galeno.com"]
            
            # Buscar y eliminar cada usuario
            for correo in correos:
                usuario = Usuario.query.filter_by(email=correo).first()
                if usuario:
                    db.session.delete(usuario)
                    print(f"Usuario {correo} eliminado correctamente")
                else:
                    print(f"Usuario {correo} no encontrado en la base de datos")
            
            # Guardar los cambios
            db.session.commit()
            print("Operación completada exitosamente")
            
        except Exception as e:
            print(f"Error al eliminar usuarios: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    eliminar_usuarios() 