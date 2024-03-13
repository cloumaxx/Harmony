from ast import AsyncFunctionDef
from flask import Flask, after_this_request, request, jsonify
from rasa.core.agent import Agent
import asyncio

from actions.actions import detectar_stop_words, traducir_a_espanol, traducir_mensaje_salida


app = Flask(__name__)

# Cargar el modelo de Rasa
modeloActual = "models/20231220-170647-rosy-moscato.tar.gz"#"models/20231220-170647-rosy-moscato.tar.gz"
agent = Agent.load(modeloActual)

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'GET':
        return 'La aplicacion Flask esta en ejecucion  GET !!!'
    elif request.method == 'POST':
        return 'La aplicacion Flask esta en ejecucion POST !!!'
    else:
        return 'Metodo no permitido', 405
    
async def handle_message(user_message):
    # Maneja el mensaje de manera asíncrona utilizando asyncio
    return await agent.handle_text(user_message)

@app.route('/PreguntaMilly', methods=['POST'])
def millyResponde():
    try:
        # Obtén el mensaje del cliente
        user_message = request.json.get('message', '').lower()
        print("-->",user_message)
        if not user_message:
            return jsonify({'response': [{'text': 'Mensaje vacío'}]})

        message_espanol = traducir_a_espanol(user_message)
        stop_words = detectar_stop_words(message_espanol.text)
        if len(stop_words) > 0:
            idioma = message_espanol.src
            message_espanol = message_espanol.text

            # Ejecuta la función asíncrona de manera síncrona usando asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            rasa_response = loop.run_until_complete(handle_message(message_espanol))
            print(rasa_response)
            if idioma != 'es':
                traducir = traducir_mensaje_salida(rasa_response[0]['text'], 'es', idioma)
                rasa_response[0]['text'] = traducir
        else:
            rasa_response = [{'text': 'No entiendo lo que me dices'}]

        # Devuelve la respuesta en formato JSON
        return jsonify({'response': rasa_response})

    except Exception as e:
        # Manejo de excepciones
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    import os

    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 5100))

    # Utiliza Gunicorn para ejecutar la aplicación Flask sin especificar el número de workers
    cmd = f'gunicorn -b {host}:{port} app:app'
    os.system(cmd)
