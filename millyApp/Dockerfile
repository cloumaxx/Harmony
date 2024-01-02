# Usa la imagen oficial de Rasa con una versión específica
FROM rasa/rasa:latest

# Establece el directorio de trabajo en /rasaBot/y
WORKDIR /rasaBot/y


# Copia tu código fuente al contenedor
COPY . .

# Entrena el modelo Rasa especificando la ubicación del archivo de configuración
RUN rasa train --config config.yml

# Expón el puerto en el que Rasa va a estar escuchando
EXPOSE 5015

# Comando para iniciar el servidor Rasa
CMD ["rasa", "run", "-p", "5015", "--enable-api", "--cors", "*"]
