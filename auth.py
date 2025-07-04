from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario
from flask_login import login_user, logout_user, current_user
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from datetime import datetime
from email_utils import send_confirmation_email, confirm_token
import logging
from config import ADMIN_EMAILS
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

class LoginForm(FlaskForm):
    email = StringField("Correo electrónico", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField("Ingresar")

def validate_community_password(form, field):
    community_pwd = os.environ.get('COMMUNITY_PASSWORD')
    if not community_pwd:
        raise ValidationError('Error en la configuración del servidor. Contacte al administrador.')
    if field.data != community_pwd:
        raise ValidationError('Contraseña comunal incorrecta')

class RegisterForm(FlaskForm):
    email = StringField("Correo electrónico", validators=[
        DataRequired(),
        Email(message="Por favor ingrese un correo electrónico válido")
    ])
    password = PasswordField("Contraseña", validators=[
        DataRequired(),
        Length(min=6, message="La contraseña debe tener al menos 6 caracteres")
    ])
    confirm_password = PasswordField("Confirmar Contraseña", validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    community_password = PasswordField("Contraseña Comunal", validators=[
        DataRequired(message="La contraseña comunal es requerida"),
        validate_community_password
    ])
    accept_terms = BooleanField('Acepto los términos y condiciones', validators=[
        DataRequired(message='Debes aceptar los términos y condiciones para registrarte')
    ])
    submit = SubmitField("Registrarse")

class RequestResetForm(FlaskForm):
    email = StringField("Correo electrónico", validators=[
        DataRequired(),
        Email(message="Por favor ingrese un correo electrónico válido")
    ])
    submit = SubmitField("Solicitar restablecimiento")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Nueva contraseña", validators=[
        DataRequired(),
        Length(min=6, message="La contraseña debe tener al menos 6 caracteres")
    ])
    confirm_password = PasswordField("Confirmar nueva contraseña", validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField("Cambiar contraseña")

@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('usuario'))
    except AttributeError:
        # Si hay un error con current_user, asegurarnos de limpiar la sesión
        logout_user()
        
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        if Usuario.query.filter_by(email=email).first():
            flash("El correo ya está registrado.", "danger")
            return redirect(url_for('auth.register'))
            
        try:
            # Verificar si el email está en la lista de administradores
            is_admin = email in ADMIN_EMAILS
            
            user = Usuario(
                email=email,
                password=generate_password_hash(form.password.data),
                is_admin=is_admin  # Asignar el rol de admin si corresponde
            )
            db.session.add(user)
            db.session.commit()
            
            try:
                send_confirmation_email(user)
                if is_admin:
                    flash("Cuenta de administrador creada. Te hemos enviado un correo de confirmación.", "info")
                else:
                    flash("Te hemos enviado un correo de confirmación. Por favor revisa tu bandeja de entrada.", "info")
            except Exception as e:
                logging.error(f"Error al enviar correo de confirmación: {str(e)}")
                flash("Se creó tu cuenta pero hubo un problema al enviar el correo de confirmación. Por favor contacta al administrador.", "warning")
            
            return redirect(url_for('auth.login'))
        except Exception as e:
            logging.error(f"Error al registrar usuario: {str(e)}")
            db.session.rollback()
            flash("Error al registrar el usuario. Por favor, intenta nuevamente.", "danger")
            return redirect(url_for('auth.register'))
            
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    # Asegurarnos de que no haya sesión activa
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin'))
        return redirect(url_for('usuario'))
    
    login_form = LoginForm()
    if login_form.validate_on_submit():
        try:
            email = login_form.email.data
            password = login_form.password.data
            remember = login_form.remember.data  # Obtener el valor del checkbox
            user = Usuario.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password, password):
                if not user.email_confirmed:
                    try:
                        send_confirmation_email(user)
                        flash("Tu correo aún no está confirmado. Te hemos enviado un nuevo correo de confirmación.", "warning")
                    except Exception as e:
                        logging.error(f"Error al reenviar correo de confirmación: {str(e)}")
                        flash("No se pudo enviar el correo de confirmación. Por favor contacta al administrador.", "danger")
                    return redirect(url_for('auth.login'))
                    
                # Login exitoso
                login_user(user, remember=remember)  # Usar el valor del checkbox
                if not remember:
                    # Si no se marca "recordarme", la sesión durará hasta que se cierre el navegador
                    session.permanent = False
                else:
                    # Si se marca "recordarme", la sesión durará 14 días
                    session.permanent = True
                session['user_id'] = user.id
                session.modified = True

                next_page = request.args.get('next')
                if next_page:
                    try:
                        return redirect(next_page)
                    except:
                        pass
                
                if user.is_admin:
                    return redirect(url_for('admin'))
                return redirect(url_for('usuario'))
            else:
                flash("Usuario o contraseña incorrectos", "danger")
        except Exception as e:
            logging.error(f"Error en el proceso de login: {str(e)}")
            flash("Error al procesar el inicio de sesión. Por favor intenta nuevamente.", "danger")
            
    return render_template('login.html', form=login_form)

@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    if current_user.is_authenticated and current_user.email_confirmed:
        return redirect(url_for('usuario'))
        
    email = confirm_token(token)
    if not email:
        flash('El enlace de confirmación es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.login'))
        
    user = Usuario.query.filter_by(email=email).first()
    if not user:
        flash('No se encontró el usuario.', 'danger')
        return redirect(url_for('auth.login'))
        
    if user.email_confirmed:
        flash('Tu correo ya está confirmado. Por favor inicia sesión.', 'info')
    else:
        user.email_confirmed = True
        user.email_confirmed_at = datetime.utcnow()
        user.confirmation_token = None
        user.confirmation_token_expires = None
        db.session.commit()
        flash('¡Has confirmado tu correo exitosamente! Ya puedes iniciar sesión.', 'success')
        
    return redirect(url_for('auth.login'))

@auth_bp.route('/resend-confirmation')
def resend_confirmation():
    if current_user.is_authenticated:
        return redirect(url_for('usuario'))
        
    email = request.args.get('email')
    if not email:
        flash('Por favor proporciona un correo electrónico.', 'danger')
        return redirect(url_for('auth.login'))
        
    user = Usuario.query.filter_by(email=email).first()
    if not user:
        flash('No se encontró el usuario.', 'danger')
        return redirect(url_for('auth.login'))
        
    if user.email_confirmed:
        flash('Tu correo ya está confirmado. Por favor inicia sesión.', 'info')
        return redirect(url_for('auth.login'))
        
    try:
        send_confirmation_email(user)
        flash('Te hemos enviado un nuevo correo de confirmación.', 'info')
    except Exception as e:
        logging.error(f"Error al reenviar correo de confirmación: {str(e)}")
        flash('No se pudo enviar el correo de confirmación. Por favor contacta al administrador.', 'danger')
        
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('usuario'))
        
    form = RequestResetForm()
    if form.validate_on_submit():
        email = form.email.data
        user = Usuario.query.filter_by(email=email).first()
        
        if user:
            try:
                from email_utils import send_reset_email
                send_reset_email(user)
                flash('Te hemos enviado un correo con instrucciones para restablecer tu contraseña. Por favor revisa tu bandeja de entrada.', 'info')
            except Exception as e:
                logging.error(f"Error al enviar correo de reset: {str(e)}")
                flash('No se pudo enviar el correo de restablecimiento. Por favor contacta al administrador.', 'danger')
        else:
            # Por seguridad, no revelamos si el email existe o no
            flash('Si el correo electrónico está registrado, recibirás instrucciones para restablecer tu contraseña.', 'info')
            
        return redirect(url_for('auth.login'))
        
    return render_template('forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('usuario'))
        
    from email_utils import confirm_reset_token
    email = confirm_reset_token(token)
    
    if not email:
        flash('El enlace de restablecimiento es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.login'))
        
    user = Usuario.query.filter_by(email=email).first()
    if not user:
        flash('No se encontró el usuario.', 'danger')
        return redirect(url_for('auth.login'))
        
    # Verificar que el token en la base de datos coincida
    if user.reset_token != token:
        flash('El enlace de restablecimiento es inválido.', 'danger')
        return redirect(url_for('auth.login'))
        
    # Verificar que el token no haya expirado
    if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
        flash('El enlace de restablecimiento ha expirado.', 'danger')
        return redirect(url_for('auth.login'))
        
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            user.password = generate_password_hash(form.password.data)
            user.reset_token = None
            user.reset_token_expires = None
            db.session.commit()
            flash('Tu contraseña ha sido actualizada exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            logging.error(f"Error al actualizar contraseña: {str(e)}")
            db.session.rollback()
            flash('Error al actualizar la contraseña. Por favor intenta nuevamente.', 'danger')
            
    return render_template('reset_password.html', form=form, token=token)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))