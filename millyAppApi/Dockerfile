# Usa una imagen base de Python
FROM python:3.10

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos necesarios a la imagen
COPY ./actions /app/actions
COPY ./data /app/data
COPY ./models /app/models
COPY ./tests /app/tests
COPY ./credentials.yml /app
COPY ./domain.yml /app
COPY ./endpoints.yml /app
COPY ./config.yml /app

# Instala las dependencias
RUN pip install  rasa # Si tienes un archivo de requerimientos

# Expone el puerto necesario (por ejemplo, si estás usando un servidor Rasa HTTP)
EXPOSE 5005

# Comando para ejecutar tu aplicación cuando se inicie el contenedor
CMD ["rasa", "run", "-m", "models", "--endpoints", "endpoints.yml"]
