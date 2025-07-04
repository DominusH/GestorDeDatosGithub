from gestor import gestor, db
from models import Usuario, Contacto
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

# Datos de ejemplo
origenes = ['referido', 'redes', 'web', 'otros']
origenes_otros = ['Evento corporativo', 'Feria de salud', 'Recomendación médica']

coberturas = ['osde', 'swiss', 'galeno', 'otros']
coberturas_otras = ['Medifé', 'OMINT', 'Medicus']

promociones = ['2x1', 'descuento_familiar', 'sin_carencia', 'otros']
promociones_otras = ['50% primer mes', 'Sin copago 3 meses', 'Consultas gratis']

estados = ['abierto', 'cerrado']
planes = ['210', '310', '410', '450', '510']

nombres = [
    "Juan Pérez", "María García", "Carlos López", "Ana Martínez",
    "Luis Rodríguez", "Laura Sánchez", "Pedro González", "Sofía Torres",
    "Diego Fernández", "Valentina Ruiz", "Martín Silva", "Lucía Morales",
    "Andrés Castro", "Camila Flores", "Gabriel Díaz", "Isabella Vargas",
    "Mateo Romero", "Victoria Acosta", "Daniel Medina", "Emma Ortiz"
]

observaciones = [
    "Interesado en plan familiar",
    "Requiere cobertura inmediata",
    "Evaluando otras opciones",
    "Pendiente de documentación",
    "Solicita más información",
    "En proceso de cambio de obra social",
    "Consulta por medicación crónica",
    "Esperando respuesta del titular",
    "Necesita presupuesto detallado",
    "Comparando planes y beneficios"
]

def generar_email(nombre):
    nombre_limpio = nombre.lower().replace(" ", ".")
    dominios = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com"]
    return f"{nombre_limpio}@{random.choice(dominios)}"

def generar_telefono():
    return f"+54 9 11 {random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

def generar_fecha_aleatoria():
    # Generar fecha entre hace 6 meses y hoy
    dias_atras = random.randint(0, 180)
    fecha = datetime.now() - timedelta(days=dias_atras)
    return fecha.strftime("%d/%m/%Y")

def insertar_datos_ejemplo():
    with gestor.app_context():
        # Crear algunos usuarios de ejemplo si no existen
        usuarios_ejemplo = [
            "vendedor1@ejemplo.com",
            "vendedor2@ejemplo.com",
            "vendedor3@ejemplo.com"
        ]
        
        usuarios_ids = []
        for email in usuarios_ejemplo:
            usuario = Usuario.query.filter_by(email=email).first()
            if not usuario:
                usuario = Usuario(
                    email=email,
                    password=generate_password_hash("password123"),
                    email_confirmed=True
                )
                db.session.add(usuario)
                db.session.commit()
                print(f"Usuario creado: {email}")
            usuarios_ids.append(usuario.id)

        # Insertar 50 contactos de ejemplo
        for _ in range(50):
            nombre = random.choice(nombres)
            origen = random.choice(origenes)
            origen_otro = random.choice(origenes_otros) if origen == 'otros' else None
            
            cobertura = random.choice(coberturas)
            cobertura_otra = random.choice(coberturas_otras) if cobertura == 'otros' else None
            
            promocion = random.choice(promociones)
            promocion_otra = random.choice(promociones_otras) if promocion == 'otros' else None

            contacto = Contacto(
                usuario_id=random.choice(usuarios_ids),
                origen=origen,
                origen_otro=origen_otro,
                cobertura_actual=cobertura,
                cobertura_actual_otra=cobertura_otra,
                promocion=promocion,
                promocion_otra=promocion_otra,
                privadoDesregulado=random.choice(['privado', 'desregulado']),
                apellido_nombre=nombre,
                correo_electronico=generar_email(nombre),
                edad_titular=str(random.randint(25, 65)),
                telefono=generar_telefono(),
                grupo_familiar=str(random.randint(1, 5)),
                plan_ofrecido=random.choice(planes),
                fecha=generar_fecha_aleatoria(),
                estado=random.choice(estados),
                observaciones=random.choice(observaciones),
                created_at=datetime.now() - timedelta(days=random.randint(0, 180))
            )
            db.session.add(contacto)
            
        try:
            db.session.commit()
            print("50 contactos de ejemplo insertados correctamente")
        except Exception as e:
            print(f"Error al insertar datos: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    insertar_datos_ejemplo() 