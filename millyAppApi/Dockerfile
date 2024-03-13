FROM python:3.10

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

# Instalar las dependencias
RUN pip install  rasa 

EXPOSE 5005

CMD ["rasa", "run", "-m", "models", "--endpoints", "endpoints.yml"]
