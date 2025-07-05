"""
Script para reiniciar la base de datos SQLite - Versión Windows
Elimina todos los contactos y opcionalmente todos los usuarios
"""

from gestor import gestor
from models import db, Contacto, Usuario

def reset_database(keep_users=True):
    """
    Reinicia la base de datos
    
    Args:
        keep_users (bool): Si es True, mantiene los usuarios. Si es False, elimina todo.
    """
    with gestor.app_context():
        try:
            # Eliminar todos los contactos
            contactos_eliminados = Contacto.query.delete()
            print(f"✓ {contactos_eliminados} contactos eliminados")
            
            if not keep_users:
                # Eliminar todos los usuarios (CUIDADO: esto eliminará también tu cuenta admin)
                usuarios_eliminados = Usuario.query.delete()
                print(f"✓ {usuarios_eliminados} usuarios eliminados")
            else:
                print("✓ Usuarios mantenidos")
            
            # Confirmar los cambios
            db.session.commit()
            print("✓ Base de datos reiniciada exitosamente")
            
        except Exception as e:
            print(f"✗ Error al reiniciar la base de datos: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    print("=== REINICIO DE BASE DE DATOS ===")
    print("Este script eliminará todos los contactos de la base de datos.")
    
    respuesta = input("¿Deseas mantener los usuarios? (s/n): ").lower().strip()
    keep_users = respuesta in ['s', 'si', 'sí', 'y', 'yes']
    
    if keep_users:
        print("Manteniendo usuarios, eliminando solo contactos...")
    else:
        print("ADVERTENCIA: Se eliminarán TODOS los usuarios y contactos.")
        confirmacion = input("¿Estás seguro? Escribe 'CONFIRMAR' para continuar: ")
        if confirmacion != 'CONFIRMAR':
            print("Operación cancelada.")
            exit()
    
    reset_database(keep_users=keep_users) 