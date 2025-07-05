from gestor import gestor, db
from models import Usuario, Contacto
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

# Datos de ejemplo actualizados según el formulario
origenes = ['propio', 'elegi mejor', 'wise', 'guardia', 'broker']

coberturas = ['smg', 'osde', 'prevencion', 'sancor', 'medife', 'obra social', 'otros']
coberturas_otras = ['Medifé', 'OMINT', 'Medicus', 'Swiss Medical', 'Galeno']

promociones = [
    'promocion sancor', 'promocion medicus', 'promocion omint', 
    'promocion prevencion', 'promocion smg', 'promocion medife',
    'osde', 'servicios insatisfactorios', 'no puede pagarlo', 'otros prepagos'
]

estados = ['abierto', 'cerrado', 'no responde', 'vendido']

planes = ['210', '310', '410', '450', '510', '610', '710']

conyuges = ['sin conyuge', 'con conyuge']

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
    "Comparando planes y beneficios",
    "Cliente muy interesado en promociones",
    "Busca cobertura para toda la familia",
    "Consulta por servicios específicos",
    "Pendiente de evaluación médica",
    "Interesado en beneficios adicionales"
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
            "vendedor3@ejemplo.com",
            "vendedor4@ejemplo.com"
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
        for i in range(50):
            nombre = random.choice(nombres)
            origen = random.choice(origenes)
            
            cobertura = random.choice(coberturas)
            cobertura_otra = random.choice(coberturas_otras) if cobertura == 'otros' else None
            
            promocion = random.choice(promociones)
            
            conyuge = random.choice(conyuges)
            conyuge_edad = str(random.randint(25, 65)) if conyuge == 'con conyuge' else 'Sin cónyuge'

            contacto = Contacto(
                usuario_id=random.choice(usuarios_ids),
                origen=origen,
                cobertura_actual=cobertura,
                cobertura_actual_otra=cobertura_otra,
                promocion=promocion,
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
                conyuge=conyuge,
                conyuge_edad=conyuge_edad,
                created_at=datetime.now() - timedelta(days=random.randint(0, 180))
            )
            db.session.add(contacto)
            
            # Mostrar progreso cada 10 contactos
            if (i + 1) % 10 == 0:
                print(f"Procesados {i + 1} contactos...")
            
        try:
            db.session.commit()
            print("✅ 50 contactos de ejemplo insertados correctamente")
            print(f"📊 Distribución por estado:")
            
            # Mostrar estadísticas
            contactos_creados = Contacto.query.all()
            estados_count = {}
            for c in contactos_creados:
                estados_count[c.estado] = estados_count.get(c.estado, 0) + 1
            
            for estado, count in estados_count.items():
                print(f"   - {estado.capitalize()}: {count}")
                
        except Exception as e:
            print(f"❌ Error al insertar datos: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    print("🚀 Iniciando inserción de datos de ejemplo...")
    insertar_datos_ejemplo()
    print("✨ Proceso completado") 