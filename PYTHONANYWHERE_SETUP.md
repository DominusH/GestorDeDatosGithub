# Configuración para PythonAnywhere

## Pasos para desplegar en PythonAnywhere

### 1. Subir archivos
- Sube todos los archivos del proyecto a tu cuenta de PythonAnywhere
- Asegúrate de que el archivo `wsgi.py` esté en el directorio raíz

### 2. Configurar el entorno virtual
```bash
# En la consola de PythonAnywhere
cd /home/tu_usuario/tu_proyecto
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar la aplicación web
- Ve a la sección "Web" en PythonAnywhere
- Crea una nueva aplicación web
- Selecciona "Manual configuration"
- Selecciona tu versión de Python (3.13 recomendado)
- En "Code" → "WSGI configuration file", edita el archivo y asegúrate de que apunte a tu `wsgi.py`

### 4. Configurar variables de entorno
En el archivo WSGI, asegúrate de que las variables de entorno estén configuradas:
```python
os.environ['MAIL_USERNAME'] = 'tu_email@gmail.com'
os.environ['MAIL_PASSWORD'] = 'tu_password'
os.environ['SECRET_KEY'] = 'tu_secret_key'
```

### 5. Crear directorios necesarios
La aplicación creará automáticamente los directorios:
- `temp/` - Para archivos temporales de Excel
- `logs/` - Para archivos de log
- `instance/` - Para la base de datos SQLite

### 6. Reiniciar la aplicación
- Haz clic en "Reload" en la sección Web de PythonAnywhere

## Solución de problemas

### Error de descarga de Excel
Si tienes problemas con la descarga de Excel:

1. **Usa la exportación CSV**: El botón "Exportar CSV" es más confiable
2. **Verifica permisos**: Asegúrate de que el directorio `temp/` tenga permisos de escritura
3. **Revisa logs**: Los errores se registran en `logs/app.log`

### Error de importación de módulos
Si hay errores de importación:

1. **Verifica el entorno virtual**: Asegúrate de que esté activado
2. **Reinstala dependencias**: `pip install -r requirements.txt`
3. **Verifica la versión de Python**: Usa Python 3.13

### Error de base de datos
Si hay problemas con la base de datos:

1. **Verifica el directorio instance**: Debe existir y tener permisos de escritura
2. **Ejecuta migraciones**: Si usas Flask-Migrate
3. **Reinicia la aplicación**: Después de cambios en la base de datos

## Archivos importantes

- `wsgi.py` - Configuración principal para PythonAnywhere
- `gestor.py` - Aplicación Flask principal
- `requirements.txt` - Dependencias de Python
- `.env` - Variables de entorno (no subir a producción)

## URLs de la aplicación

- **Login**: `https://tu_usuario.pythonanywhere.com/`
- **Panel de usuario**: `https://tu_usuario.pythonanywhere.com/usuario`
- **Panel de admin**: `https://tu_usuario.pythonanywhere.com/admin`
- **Exportación CSV**: `https://tu_usuario.pythonanywhere.com/exportar_mis_contactos_simple`

## Notas importantes

1. **Debug desactivado**: En producción, el debug está desactivado por seguridad
2. **Logs**: Los logs se guardan en `logs/app.log` para debugging
3. **Archivos temporales**: Se limpian automáticamente después de 1 hora
4. **Base de datos**: SQLite se guarda en `instance/contactos.db`

## Soporte

Si tienes problemas:
1. Revisa los logs en `logs/app.log`
2. Verifica la configuración del WSGI
3. Asegúrate de que todas las dependencias estén instaladas
4. Contacta soporte de PythonAnywhere si es un problema del servidor 