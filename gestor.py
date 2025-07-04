from dotenv import load_dotenv
import os
from flask import Flask, redirect, url_for, render_template, session, send_file, flash, request, jsonify
from auth import auth_bp 
from models import db, Usuario
from form import ContactoForm
import pandas as pd
from flask_login import LoginManager, login_required, current_user, AnonymousUserMixin
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.chart import PieChart, Reference
from openpyxl.utils import get_column_letter
from email_utils import mail, init_serializer
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
import logging
from datetime import timedelta, datetime
from flask_wtf.csrf import CSRFProtect
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Border, Side

# Configurar logging primero
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Cargar variables de entorno
logging.info("Intentando cargar archivo .env...")
load_dotenv(override=True)  # Forzar recarga de variables
logging.info("Archivo .env cargado")

# Verificar variables críticas
logging.info("Variables de entorno cargadas:")
logging.info(f"MAIL_USERNAME: {os.environ.get('MAIL_USERNAME')}")
logging.info(f"MAIL_PASSWORD: {'Configurado' if os.environ.get('MAIL_PASSWORD') else 'NO CONFIGURADO'}")
logging.info(f"MAIL_DEFAULT_SENDER: {os.environ.get('MAIL_DEFAULT_SENDER')}")

class Anonymous(AnonymousUserMixin):
    @property
    def is_authenticated(self):
        return False
    
    @property
    def is_active(self):
        return False
    
    @property
    def is_anonymous(self):
        return True
    
    def get_id(self):
        return None

# Inicializar Flask y sus extensiones
gestor = Flask(__name__)
gestor.config.from_object('config.Config')

# Configuración de sesión
gestor.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
gestor.config['SESSION_COOKIE_SECURE'] = False  # Cambiado a False para desarrollo local
gestor.config['SESSION_COOKIE_HTTPONLY'] = True
gestor.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
gestor.config['SESSION_PROTECTION'] = 'basic'  # Cambiado a 'basic' en lugar de 'strong'
gestor.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=14)
gestor.config['REMEMBER_COOKIE_REFRESH_EACH_REQUEST'] = True

# Inicializar extensiones
csrf = CSRFProtect(gestor)
db.init_app(gestor)
migrate = Migrate(gestor, db)
mail.init_app(gestor)
init_serializer(gestor)

# Registrar blueprints
gestor.register_blueprint(auth_bp)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(gestor)
login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor inicia sesión para acceder a esta página."
login_manager.login_message_category = "info"
login_manager.login_message_category = "info"
login_manager.session_protection = "basic"  # Cambiado a 'basic'
login_manager.refresh_view = "auth.login"
login_manager.needs_refresh_message = "Por favor inicia sesión nuevamente para continuar."
login_manager.needs_refresh_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    if user_id is None:
        return None
    try:
        user = db.session.get(Usuario, int(user_id))
        if user:
            # Renovar la sesión
            session.permanent = True
            session['user_id'] = user.id
            session.modified = True
        return user
    except (ValueError, TypeError):
        return None

# Crear la base de datos
with gestor.app_context():
    from models import Contacto
    db.create_all() 

# Configurar manejo de usuarios anónimos
login_manager.anonymous_user = Anonymous

@gestor.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))
    contactos = Contacto.query.all()
    return render_template('admin.html', contactos=contactos, now=datetime.now)

@gestor.route('/exportar_contactos')
@login_required
def exportar_contactos():
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))
        
    contactos = Contacto.query.all()
    
    # Función para normalizar texto
    def normalize_text(text):
        if text:
            # Convertir a minúsculas y capitalizar la primera letra
            return text.strip().lower().capitalize()
        return text
    
    data = [{
        "Origen": normalize_text(c.origen),
        "Cobertura Actual": normalize_text(c.cobertura_actual_otra) if c.cobertura_actual == 'otros' else c.cobertura_actual,
        "¿Por qué no toma la cobertura?": normalize_text(c.promocion) if c.promocion else "No especificado",
        "Privado/Desregulado": c.privadoDesregulado,
        "Apellido y nombre": c.apellido_nombre,
        "Correo electrónico": c.correo_electronico,
        "Edad titular": c.edad_titular,
        "Teléfono": c.telefono,
        "Grupo familiar": c.grupo_familiar,
        "Plan ofrecido": c.plan_ofrecido,
        "Fecha": c.fecha,
        "Estado": c.estado,
        "Observaciones": c.observaciones,
        "Cónyuge": c.conyuge,
        "Edad cónyuge": c.conyuge_edad,
        "Fecha de carga": c.created_at.strftime("%d/%m/%Y"),
        "Usuario cargador": c.usuario.email
    } for c in contactos]
    
    df = pd.DataFrame(data)
    
    # Crear un nuevo libro de Excel
    wb = openpyxl.Workbook()
    
    # Configurar estilos generales
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    month_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    month_font = Font(bold=True, size=11, color="1F4E78")
    
    # Crear la hoja de datos
    ws_data = wb.active
    ws_data.title = "Base de Datos"

    # Ordenar los datos por fecha de carga
    df['Mes de carga'] = pd.to_datetime(df['Fecha de carga'], format='%d/%m/%Y').dt.strftime('%B %Y')
    df = df.sort_values('Fecha de carga')

    # Agrupar por mes
    grupos_mes = df.groupby('Mes de carga')

    # Fila actual para ir agregando datos
    current_row = 1

    for mes, grupo in grupos_mes:
        # Agregar encabezado del mes
        ws_data.merge_cells(f'A{current_row}:P{current_row}')
        mes_cell = ws_data[f'A{current_row}']
        mes_cell.value = f"CONTACTOS CARGADOS EN {mes.upper()}"
        mes_cell.fill = month_fill
        mes_cell.font = month_font
        mes_cell.alignment = Alignment(horizontal="center", vertical="center")
        current_row += 1

        # Agregar encabezados de columnas
        headers = [
            "Origen", "Cobertura Actual", "¿Por qué no toma la cobertura?", "Privado/Desregulado",
            "Apellido y nombre", "Correo electrónico", "Edad titular",
            "Teléfono", "Grupo familiar", "Plan ofrecido", "Fecha",
            "Estado", "Observaciones", "Cónyuge", "Edad cónyuge", "Fecha de carga"
        ]

        for col, header in enumerate(headers, 1):
            cell = ws_data.cell(row=current_row, column=col)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
        current_row += 1

        # Agregar datos del grupo
        for _, row in grupo.iterrows():
            ws_data.cell(row=current_row, column=1).value = row['Origen']
            ws_data.cell(row=current_row, column=2).value = row['Cobertura Actual']
            ws_data.cell(row=current_row, column=3).value = row['¿Por qué no toma la cobertura?']
            ws_data.cell(row=current_row, column=4).value = row['Privado/Desregulado']
            ws_data.cell(row=current_row, column=5).value = row['Apellido y nombre']
            ws_data.cell(row=current_row, column=6).value = row['Correo electrónico']
            ws_data.cell(row=current_row, column=7).value = row['Edad titular']
            ws_data.cell(row=current_row, column=8).value = row['Teléfono']
            ws_data.cell(row=current_row, column=9).value = row['Grupo familiar']
            ws_data.cell(row=current_row, column=10).value = row['Plan ofrecido']
            ws_data.cell(row=current_row, column=11).value = row['Fecha']
            ws_data.cell(row=current_row, column=12).value = row['Estado']
            ws_data.cell(row=current_row, column=13).value = row['Observaciones']
            ws_data.cell(row=current_row, column=14).value = row['Cónyuge']
            ws_data.cell(row=current_row, column=15).value = row['Edad cónyuge']
            ws_data.cell(row=current_row, column=16).value = row['Fecha de carga']

            # Aplicar estilo según el estado
            estado_cell = ws_data.cell(row=current_row, column=12)
            if row['Estado'] == 'abierto':
                estado_cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                estado_cell.font = Font(color="006100")
            elif row['Estado'] == 'cerrado':
                estado_cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                estado_cell.font = Font(color="9C0006")
            elif row['Estado'] == 'vendido':
                estado_cell.fill = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
                estado_cell.font = Font(color="1F4E78")
            elif row['Estado'] == 'vendido':
                estado_cell.fill = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
                estado_cell.font = Font(color="1F4E78")

            current_row += 1

        # Agregar espacio entre grupos
        current_row += 1

    # Ajustar ancho de columnas
    for column in ws_data.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws_data.column_dimensions[column_letter].width = min(adjusted_width, 30)

    # Agregar bordes a todas las celdas con datos
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for row in ws_data.iter_rows(min_row=1, max_row=ws_data.max_row):
        for cell in row:
            if cell.value is not None:
                cell.border = border
                if not cell.alignment:
                    cell.alignment = Alignment(horizontal="left", vertical="center")

    # Agregar una nueva hoja de resumen por mes
    ws_monthly = wb.create_sheet(title="Resumen Mensual")
    
    # Título
    ws_monthly.merge_cells('A1:F1')
    ws_monthly['A1'] = "RESUMEN DE CONTACTOS POR MES"
    ws_monthly['A1'].font = Font(size=16, bold=True, color="1F4E78")
    ws_monthly['A1'].alignment = Alignment(horizontal="center")
    
    # Encabezados
    headers = ["Mes", "Total Contactos", "Planes Vendidos", "Abiertos", "Cerrados", "Tasa de Efectividad"]
    for col, header in enumerate(headers, 1):
        cell = ws_monthly.cell(row=3, column=col)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
    
    # Datos por mes
    current_row = 4
    for mes, grupo in grupos_mes:
        total = len(grupo)
        vendidos = len(grupo[grupo['Estado'] == 'vendido'])
        abiertos = len(grupo[grupo['Estado'] == 'abierto'])
        cerrados = len(grupo[grupo['Estado'] == 'cerrado'])
        tasa = (vendidos / total * 100) if total > 0 else 0
        
        ws_monthly[f'A{current_row}'] = mes
        ws_monthly[f'B{current_row}'] = total
        ws_monthly[f'C{current_row}'] = vendidos
        ws_monthly[f'D{current_row}'] = abiertos
        ws_monthly[f'E{current_row}'] = cerrados
        ws_monthly[f'F{current_row}'] = f"{tasa:.1f}%"
        
        # Formato
        for col in range(1, 7):
            cell = ws_monthly.cell(row=current_row, column=col)
            cell.border = border
            cell.alignment = Alignment(horizontal="center")
        
        current_row += 1
    
    # Ajustar ancho de columnas
    for column in ws_monthly.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws_monthly.column_dimensions[column_letter].width = min(adjusted_width, 30)

    # Agregar hoja de estadísticas de campos
    ws_stats = wb.create_sheet(title="Estadísticas de Campos")
    
    # Título
    ws_stats.merge_cells('A1:D1')
    ws_stats['A1'] = "DISTRIBUCIÓN DE OPCIONES SELECCIONADAS"
    ws_stats['A1'].font = Font(size=16, bold=True, color="1F4E78")
    ws_stats['A1'].alignment = Alignment(horizontal="center")
    
    # Encabezados
    headers = ["Campo", "Opción", "Cantidad", "Porcentaje"]
    for col, header in enumerate(headers, 1):
        cell = ws_stats.cell(row=3, column=col)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
    
    # Campos a analizar
    campos = {
        'Origen': 'Origen',
        'Cobertura Actual': 'Cobertura Actual',
        '¿Por qué no toma la cobertura?': '¿Por qué no toma la cobertura?',
        'Privado/Desregulado': 'Privado/Desregulado',
        'Estado': 'Estado'
    }
    
    current_row = 4
    
    # Analizar cada campo
    for campo_df, nombre_campo in campos.items():
        # Agregar título del campo
        ws_stats.merge_cells(f'A{current_row}:D{current_row}')
        campo_cell = ws_stats[f'A{current_row}']
        campo_cell.value = f"DISTRIBUCIÓN DE {nombre_campo.upper()}"
        campo_cell.fill = month_fill
        campo_cell.font = month_font
        campo_cell.alignment = Alignment(horizontal="center")
        current_row += 1
        
        # Calcular distribución
        total = len(df)
        distribucion = df[campo_df].value_counts()
        
        # Agregar datos
        for opcion, cantidad in distribucion.items():
            porcentaje = (cantidad / total * 100)
            
            ws_stats[f'A{current_row}'] = nombre_campo
            ws_stats[f'B{current_row}'] = opcion
            ws_stats[f'C{current_row}'] = cantidad
            ws_stats[f'D{current_row}'] = f"{porcentaje:.1f}%"
            
            # Formato
            for col in range(1, 5):
                cell = ws_stats.cell(row=current_row, column=col)
                cell.border = border
                cell.alignment = Alignment(horizontal="center")
            
            current_row += 1
        
        # Espacio entre campos
        current_row += 1
    
    # Ajustar ancho de columnas
    for column in ws_stats.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws_stats.column_dimensions[column_letter].width = min(adjusted_width, 30)

    # Guardar el archivo
    wb.save("contactos.xlsx")

    return send_file("contactos.xlsx", as_attachment=True)

@gestor.route('/usuario', methods=["GET", "POST"])
@login_required
def usuario():
    logging.info(f"Accediendo a ruta /usuario - Usuario autenticado: {current_user.is_authenticated}")
    
    # Verificar autenticación
    if not current_user.is_authenticated:
        logging.error("Usuario no autenticado en ruta protegida")
        flash("Por favor inicia sesión para continuar", "warning")
        return redirect(url_for('auth.login'))
    
    # Renovar la sesión
    session.permanent = True
    session['user_id'] = current_user.id
    session['_fresh'] = True
    session.modified = True
    
    form = ContactoForm()
    
    if request.method == "POST":
        logging.info("Recibiendo POST para agregar contacto")
        logging.info(f"Form data: {request.form}")
        
        # Verificar campos requeridos
        campos_requeridos = [
            ('origen', 'Origen'),
            ('privadoDesregulado', 'Privado/Desregulado'),
            ('apellido_nombre', 'Apellido y nombre'),
            ('correo_electronico', 'Correo electrónico'),
            ('edad_titular', 'Edad titular'),
            ('telefono', 'Teléfono'),
            ('grupo_familiar', 'Grupo familiar'),
            ('plan_ofrecido', 'Plan ofrecido'),
            ('fecha', 'Fecha'),
            ('estado', 'Estado')
        ]
        
        campos_vacios = []
        for campo, nombre in campos_requeridos:
            valor = getattr(form, campo).data
            if not valor or (isinstance(valor, str) and not valor.strip()):
                campos_vacios.append(nombre)
        
        if campos_vacios:
            flash(f"Por favor complete los siguientes campos obligatorios: {', '.join(campos_vacios)}", "danger")
            return render_template('usuario.html', form=form, contactos_usuario=contactos_usuario)
        
        if form.validate_on_submit():
            logging.info("Formulario validado correctamente")
            try:
                # Procesar campos con opción "otros"
                cobertura_final = form.cobertura_actual_otra.data if form.cobertura_actual.data == 'otros' else form.cobertura_actual.data
                
                # Procesar campo de cónyuge
                conyuge_edad_final = form.conyuge_edad.data if form.conyuge.data == 'con conyuge' else 'Sin cónyuge'
                
                nuevo_contacto = Contacto(
                    usuario_id=current_user.id,
                    origen=form.origen.data,
                    cobertura_actual=cobertura_final,
                    cobertura_actual_otra=form.cobertura_actual_otra.data if form.cobertura_actual.data == 'otros' else None,
                    promocion=form.promocion.data,
                    privadoDesregulado=form.privadoDesregulado.data,
                    apellido_nombre=form.apellido_nombre.data,
                    correo_electronico=form.correo_electronico.data,
                    edad_titular=form.edad_titular.data,
                    telefono=form.telefono.data,
                    grupo_familiar=form.grupo_familiar.data,
                    plan_ofrecido=form.plan_ofrecido.data,
                    fecha=form.fecha.data,
                    estado=form.estado.data,
                    observaciones=form.observaciones.data,
                    conyuge=form.conyuge.data,
                    conyuge_edad=conyuge_edad_final
                )
                db.session.add(nuevo_contacto)
                db.session.commit()
                
                flash("Contacto agregado correctamente", "success")
                logging.info("Contacto agregado exitosamente")
                return redirect(url_for('usuario'))
                
            except Exception as e:
                logging.error(f"Error al agregar contacto: {str(e)}")
                db.session.rollback()
                flash("Error al agregar el contacto. Por favor intenta nuevamente.", "danger")
        else:
            logging.error(f"Errores en el formulario: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error en {getattr(form, field).label.text}: {error}", "danger")

    try:
        contactos_usuario = Contacto.query.filter_by(usuario_id=current_user.id).all()
    except Exception as e:
        logging.error(f"Error al obtener contactos: {str(e)}")
        contactos_usuario = []
        flash("Error al cargar los contactos", "warning")

    return render_template('usuario.html', form=form, contactos_usuario=contactos_usuario)

@gestor.route('/cambiar_estado_contacto', methods=['POST'])
@login_required
def cambiar_estado_contacto():
    try:
        logging.info(f"Recibiendo solicitud para cambiar estado - Usuario: {current_user.id}")
        contacto_id = request.form.get('contacto_id')
        nuevo_estado = request.form.get('nuevo_estado')
        
        logging.info(f"Datos recibidos - contacto_id: {contacto_id}, nuevo_estado: {nuevo_estado}")
        
        if not contacto_id or not nuevo_estado:
            logging.warning("Datos incompletos en la solicitud")
            return jsonify({'success': False, 'message': 'Datos incompletos'})
        
        # Verificar que el contacto pertenece al usuario actual
        contacto = Contacto.query.filter_by(id=contacto_id, usuario_id=current_user.id).first()
        
        if not contacto:
            logging.warning(f"Contacto no encontrado - ID: {contacto_id}, Usuario: {current_user.id}")
            return jsonify({'success': False, 'message': 'Contacto no encontrado'})
        
        logging.info(f"Contacto encontrado - Estado actual: {contacto.estado}")
        
        # Validar que el estado sea válido
        estados_validos = ['abierto', 'cerrado', 'no responde', 'vendido']
        if nuevo_estado not in estados_validos:
            logging.warning(f"Estado no válido: {nuevo_estado}")
            return jsonify({'success': False, 'message': 'Estado no válido'})
        
        # Actualizar el estado
        contacto.estado = nuevo_estado
        db.session.commit()
        
        logging.info(f"Estado actualizado exitosamente - Nuevo estado: {nuevo_estado}")
        
        return jsonify({
            'success': True, 
            'message': f'Estado actualizado a {nuevo_estado.capitalize()}',
            'nuevo_estado': nuevo_estado
        })
        
    except Exception as e:
        logging.error(f"Error al cambiar estado del contacto: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al actualizar el estado'})

@gestor.route('/exportar_mis_contactos')
@login_required
def exportar_mis_contactos():
    contactos = Contacto.query.filter_by(usuario_id=current_user.id).all()
    
    # Función para normalizar texto
    def normalize_text(text):
        if text:
            return text.strip().lower().capitalize()
        return text
    
    data = [{
        "Origen": normalize_text(c.origen),
        "Cobertura Actual": normalize_text(c.cobertura_actual_otra) if c.cobertura_actual == 'otros' else c.cobertura_actual,
        "¿Por qué no toma la cobertura?": normalize_text(c.promocion) if c.promocion else "No especificado",
        "Privado/Desregulado": c.privadoDesregulado,
        "Apellido y nombre": c.apellido_nombre,
        "Correo electrónico": c.correo_electronico,
        "Edad titular": c.edad_titular,
        "Teléfono": c.telefono,
        "Grupo familiar": c.grupo_familiar,
        "Plan ofrecido": c.plan_ofrecido,
        "Fecha": c.fecha,
        "Estado": c.estado,
        "Observaciones": c.observaciones,
        "Cónyuge": c.conyuge,
        "Edad cónyuge": c.conyuge_edad,
        "Fecha de carga": c.created_at.strftime("%d/%m/%Y")
    } for c in contactos]
    
    df = pd.DataFrame(data)
    
    # Crear un nuevo libro de Excel
    wb = openpyxl.Workbook()
    
    # Configurar estilos generales
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    # Crear la hoja de datos
    ws_data = wb.active
    ws_data.title = "Mis Contactos"
    
    # Convertir DataFrame a Excel
    for r in dataframe_to_rows(df, index=False, header=True):
        ws_data.append(r)
    
    # Formato de encabezados
    for cell in ws_data[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
    
    # Ajustar ancho de columnas
    for column in ws_data.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws_data.column_dimensions[column_letter].width = min(adjusted_width, 30)

    # Agregar bordes a todas las celdas con datos
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for row in ws_data.iter_rows(min_row=1, max_row=ws_data.max_row):
        for cell in row:
            if cell.value is not None:
                cell.border = border
                if not cell.alignment:
                    cell.alignment = Alignment(horizontal="left", vertical="center")

    # Agregar hoja de resumen mensual
    ws_monthly = wb.create_sheet(title="Resumen Mensual")
    
    # Título
    ws_monthly.merge_cells('A1:F1')
    ws_monthly['A1'] = "RESUMEN DE CONTACTOS POR MES"
    ws_monthly['A1'].font = Font(size=16, bold=True, color="1F4E78")
    ws_monthly['A1'].alignment = Alignment(horizontal="center")
    
    # Encabezados
    headers = ["Mes", "Total Contactos", "Planes Vendidos", "Abiertos", "Cerrados", "Tasa de Efectividad"]
    for col, header in enumerate(headers, 1):
        cell = ws_monthly.cell(row=3, column=col)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
    
    # Ordenar los datos por fecha de carga
    df['Mes de carga'] = pd.to_datetime(df['Fecha de carga'], format='%d/%m/%Y').dt.strftime('%B %Y')
    df = df.sort_values('Fecha de carga')
    
    # Agrupar por mes
    grupos_mes = df.groupby('Mes de carga')
    
    # Datos por mes
    current_row = 4
    for mes, grupo in grupos_mes:
        total = len(grupo)
        vendidos = len(grupo[grupo['Estado'] == 'vendido'])
        abiertos = len(grupo[grupo['Estado'] == 'abierto'])
        cerrados = len(grupo[grupo['Estado'] == 'cerrado'])
        tasa = (vendidos / total * 100) if total > 0 else 0
        
        ws_monthly[f'A{current_row}'] = mes
        ws_monthly[f'B{current_row}'] = total
        ws_monthly[f'C{current_row}'] = vendidos
        ws_monthly[f'D{current_row}'] = abiertos
        ws_monthly[f'E{current_row}'] = cerrados
        ws_monthly[f'F{current_row}'] = f"{tasa:.1f}%"
        
        # Formato
        for col in range(1, 7):
            cell = ws_monthly.cell(row=current_row, column=col)
            cell.border = border
            cell.alignment = Alignment(horizontal="center")
        
        current_row += 1
    
    # Ajustar ancho de columnas
    for column in ws_monthly.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws_monthly.column_dimensions[column_letter].width = min(adjusted_width, 30)

    # Guardar el archivo
    wb.save("mis_contactos.xlsx")
    
    return send_file("mis_contactos.xlsx", as_attachment=True)

@gestor.route('/')
def redirigirlogin():
    return redirect(url_for('auth.login'))

@gestor.errorhandler(404)
def pageNotFound(error):
    return redirect(url_for('auth.login'))

@gestor.route('/verificar_email', methods=['POST'])
def verificar_email():
    email = request.json.get('email')
    tipo = request.json.get('tipo')  # 'login' o 'register'
    
    if not email:
        return jsonify({'valid': False, 'message': 'Email requerido'})
    
    # Verificar formato básico del email
    import re
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(email):
        return jsonify({'valid': False, 'message': 'Formato de email inválido'})
    
    # Verificar si existe en la base de datos
    usuario = Usuario.query.filter_by(email=email).first()
    
    if tipo == 'login':
        # Para login, el email debe existir
        if usuario:
            return jsonify({'valid': True, 'message': 'Email válido'})
        return jsonify({'valid': False, 'message': 'Email no registrado'})
    else:  # register
        # Para registro, el email no debe existir
        if usuario:
            return jsonify({'valid': False, 'message': 'Email ya registrado'})
        return jsonify({'valid': True, 'message': 'Email disponible'})

@gestor.route('/terminos-y-condiciones')
def terminos():
    return render_template('terminos.html')

if __name__ == '__main__':
    gestor.run(host='0.0.0.0', port=5555, debug=False)