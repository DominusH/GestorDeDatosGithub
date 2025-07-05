from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class RegisterForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    retype_password = PasswordField('Repetir contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas no coinciden')])
    submit = SubmitField('Registrarse')



class ContactoForm(FlaskForm):
    OPCIONES_ORIGEN = [
        ('', 'Seleccione...'),
        ('propio', 'Propio'),
        ('elegi mejor', 'Elegi Mejor'),
        ('wise', 'Wise'),
        ('guardia', 'Guardia'),
        ('broker', 'Broker')
    ]

    OPCIONES_COBERTURA = [
        ('', 'Seleccione...'),
        ('smg', 'SMG'),
        ('osde', 'OSDE'),
        ('prevencion', 'Prevencion'),
        ('sancor', 'Sancor'),
        ('medife', 'Medife'),
        ('obra social', 'Obra social'),
        ('otros', 'Otros')
    ]

    OPCIONES_PROMOCION = [
        ('', 'Seleccione...'),
        ('promocion sancor', 'Promocion Sancor'),
        ('promocion medicus', 'Promocion Medicus'),
        ('promocion omint', 'Promocion Omint'),
        ('promocion prevencion', 'Promocion Prevencion'),
        ('promocion smg', 'Promocion SMG'),
        ('promocion medife', 'Promocion Medife'),
        ('osde', 'Osde'),
        ('servicios insatisfactorios', 'Servicios insatisfactorios'),
        ('no puede pagarlo', 'No puede pagarlo'),
        ('otros prepagos', 'Otros prepagos')
    ]

    OPCIONES_CONYUGE = [
        ('', 'Seleccione...'),
        ('sin conyuge', 'Sin cónyuge'),
        ('con conyuge', 'Con cónyuge')
    ]

    class Meta:
        csrf = True  # Habilitar protección CSRF explícitamente
    
    origen = SelectField('Origen', choices=OPCIONES_ORIGEN, validators=[DataRequired(message="Por favor seleccione un origen")])
    
    cobertura_actual = SelectField('Cobertura Actual', choices=OPCIONES_COBERTURA, validators=[DataRequired(message="Por favor seleccione una cobertura")])
    cobertura_actual_otra = StringField('Especificar otra cobertura')
    
    promocion = SelectField('¿Por qué no toma la cobertura?', choices=OPCIONES_PROMOCION, validators=[Optional()])

    privadoDesregulado = SelectField('Privado/Desregulado',
        choices=[('', 'Seleccione...'), ('privado', 'Privado'), ('desregulado', 'Desregulado')],
        validators=[DataRequired()])
    
    apellido_nombre = StringField('Apellido y nombre', validators=[DataRequired()])
    correo_electronico = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    edad_titular = StringField('Edad titular', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    grupo_familiar = StringField('Grupo familiar', validators=[DataRequired()])
    plan_ofrecido = StringField('Plan ofrecido', validators=[DataRequired()])
    estado = SelectField('Estado',
        choices=[
            ('', 'Seleccione...'),
            ('abierto', 'Abierto'),
            ('cerrado', 'Cerrado'),
            ('no responde', 'No responde'),
            ('vendido', 'Vendido')
        ],
        validators=[DataRequired()])
    observaciones = TextAreaField('Observaciones')
    
    conyuge = SelectField('Cónyuge', choices=OPCIONES_CONYUGE, validators=[DataRequired(message="Por favor seleccione una opción")])
    conyuge_edad = StringField('Edad del cónyuge')
    
    submit = SubmitField('Agregar contacto')