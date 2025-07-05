from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.orm import relationship
import pytz

db = SQLAlchemy()

def get_argentina_time():
    """Obtiene la fecha y hora actual en la zona horaria de Chile + 1 hora (para coincidir con Buenos Aires)"""
    chile_tz = pytz.timezone('America/Santiago')
    chile_time = datetime.now(chile_tz)
    # Sumar 1 hora para que coincida con Buenos Aires
    from datetime import timedelta
    return chile_time + timedelta(hours=1)

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(512), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirmed_at = db.Column(db.DateTime)
    confirmation_token = db.Column(db.String(100), unique=True)
    confirmation_token_expires = db.Column(db.DateTime)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=get_argentina_time)
    contactos = relationship('Contacto', backref='usuario', lazy=True, cascade='all, delete-orphan')

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

class Contacto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    origen = db.Column(db.String(64), nullable=True)
    cobertura_actual = db.Column(db.String(64), nullable=True)
    cobertura_actual_otra = db.Column(db.String(128), nullable=True)
    promocion = db.Column(db.String(64), nullable=True)
    privadoDesregulado = db.Column(db.String(32), nullable=False)
    apellido_nombre = db.Column(db.String(128), nullable=False)
    correo_electronico = db.Column(db.String(128), nullable=False)
    edad_titular = db.Column(db.String(32), nullable=False)
    telefono = db.Column(db.String(32), nullable=False)
    grupo_familiar = db.Column(db.String(128), nullable=False)
    plan_ofrecido = db.Column(db.String(128), nullable=False)
    fecha = db.Column(db.String(32), nullable=False)
    estado = db.Column(db.String(32), nullable=False)
    observaciones = db.Column(db.Text)
    conyuge = db.Column(db.String(32), nullable=False)
    conyuge_edad = db.Column(db.String(32), nullable=True)
    created_at = db.Column(db.DateTime, default=get_argentina_time)