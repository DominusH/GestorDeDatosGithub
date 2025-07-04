from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from models import db
from flask import url_for, current_app
import logging

mail = Mail()
serializer = None

def init_serializer(app):
    global serializer
    logging.info("Inicializando serializer con SECRET_KEY")
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def generate_confirmation_token(email):
    if not serializer:
        logging.error("Serializer no inicializado")
        raise RuntimeError("Serializer no inicializado. Llama a init_serializer primero.")
    logging.info(f"Generando token para {email}")
    return serializer.dumps(email, salt='email-confirm')

def confirm_token(token, expiration=3600):
    if not serializer:
        logging.error("Serializer no inicializado")
        raise RuntimeError("Serializer no inicializado. Llama a init_serializer primero.")
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=expiration)
        return email
    except Exception as e:
        logging.error(f"Error al confirmar token: {str(e)}")
        return False

def send_confirmation_email(user):
    try:
        logging.info(f"Iniciando envío de correo a {user.email}")
        
        # Verificar configuración
        required_config = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_DEFAULT_SENDER']
        for config in required_config:
            value = current_app.config.get(config)
            logging.info(f"Configuración {config}: {'Presente' if value else 'FALTA'}")
            if not value:
                raise ValueError(f"Falta configuración requerida: {config}")
        
        token = generate_confirmation_token(user.email)
        logging.info("Token generado correctamente")
        
        # Guardar el token y su fecha de expiración
        user.confirmation_token = token
        user.confirmation_token_expires = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        logging.info("Token guardado en la base de datos")
        
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        logging.info(f"URL de confirmación generada: {confirm_url}")
        
        subject = "Por favor confirma tu correo electrónico"
        html = f'''
        <h1>¡Bienvenido al Gestor de Contactos!</h1>
        <p>Para confirmar tu correo electrónico, por favor haz clic en el siguiente enlace:</p>
        <p><a href="{confirm_url}">Confirmar correo electrónico</a></p>
        <p>Este enlace expirará en 24 horas.</p>
        <p>Si no te registraste en nuestra aplicación, por favor ignora este correo.</p>
        '''
        
        msg = Message(
            subject,
            recipients=[user.email],
            html=html,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        logging.info("Intentando enviar el correo...")
        try:
            mail.send(msg)
            logging.info(f"Correo de confirmación enviado exitosamente a {user.email}")
            return True
        except Exception as e:
            logging.error(f"Error al enviar el correo: {str(e)}")
            if "Username and Password not accepted" in str(e):
                logging.error("Error de autenticación SMTP - Verifica usuario y contraseña")
            raise
            
    except Exception as e:
        logging.error(f"Error en send_confirmation_email: {str(e)}")
        logging.exception("Detalles completos del error:")
        db.session.rollback()
        raise 

def generate_reset_token(email):
    if not serializer:
        logging.error("Serializer no inicializado")
        raise RuntimeError("Serializer no inicializado. Llama a init_serializer primero.")
    logging.info(f"Generando token de reset para {email}")
    return serializer.dumps(email, salt='password-reset')

def confirm_reset_token(token, expiration=3600):
    if not serializer:
        logging.error("Serializer no inicializado")
        raise RuntimeError("Serializer no inicializado. Llama a init_serializer primero.")
    try:
        email = serializer.loads(token, salt='password-reset', max_age=expiration)
        return email
    except Exception as e:
        logging.error(f"Error al confirmar token de reset: {str(e)}")
        return False

def send_reset_email(user):
    try:
        logging.info(f"Iniciando envío de correo de reset a {user.email}")
        
        # Verificar configuración
        required_config = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_DEFAULT_SENDER']
        for config in required_config:
            value = current_app.config.get(config)
            logging.info(f"Configuración {config}: {'Presente' if value else 'FALTA'}")
            if not value:
                raise ValueError(f"Falta configuración requerida: {config}")
        
        token = generate_reset_token(user.email)
        logging.info("Token de reset generado correctamente")
        
        # Guardar el token y su fecha de expiración
        user.reset_token = token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hora de expiración
        db.session.commit()
        logging.info("Token de reset guardado en la base de datos")
        
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        logging.info(f"URL de reset generada: {reset_url}")
        
        subject = "Restablecer tu contraseña - Gestor de Contactos"
        html = f'''
        <h1>Restablecer Contraseña</h1>
        <p>Has solicitado restablecer tu contraseña en el Gestor de Contactos.</p>
        <p>Para continuar con el proceso, haz clic en el siguiente enlace:</p>
        <p><a href="{reset_url}">Restablecer contraseña</a></p>
        <p>Este enlace expirará en 1 hora.</p>
        <p>Si no solicitaste este cambio, por favor ignora este correo. Tu contraseña permanecerá sin cambios.</p>
        <p>Si tienes alguna pregunta, contacta al administrador del sistema.</p>
        '''
        
        msg = Message(
            subject,
            recipients=[user.email],
            html=html,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        logging.info("Intentando enviar el correo de reset...")
        try:
            mail.send(msg)
            logging.info(f"Correo de reset enviado exitosamente a {user.email}")
            return True
        except Exception as e:
            logging.error(f"Error al enviar el correo de reset: {str(e)}")
            if "Username and Password not accepted" in str(e):
                logging.error("Error de autenticación SMTP - Verifica usuario y contraseña")
            raise
            
    except Exception as e:
        logging.error(f"Error en send_reset_email: {str(e)}")
        logging.exception("Detalles completos del error:")
        db.session.rollback()
        raise 