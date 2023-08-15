import json
import chromadb
from chromadb.config import Settings
import re

def cargar_datos(client):
    ruta = "harmonyApp/chatbot/contexto/contextoEndpoint.json"

    # Abre el archivo JSON
    with open(ruta, "r") as file:
        data = json.load(file)

    # Carga los datos en ChromaDB
    client.load_data(data, 'my_table')