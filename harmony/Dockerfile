# Usa una imagen base con Python
FROM python:3.10

# Establece el directorio de trabajo en la imagen
WORKDIR /harmonyApp/templates/

# Copia los archivos de requerimientos e instala dependencias
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación
COPY . .

# Configura las variables de entorno
ENV PORT=8890
ENV DJANGO_SETTINGS_MODULE=harmonyProject.settings

# Recopila archivos estáticos
RUN python manage.py collectstatic --noinput

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE $PORT

# Comando para ejecutar la aplicación (ajusta según tu proyecto)
CMD ["gunicorn", "--bind", "0.0.0.0:8890", "harmonyProject.wsgi:application"]
