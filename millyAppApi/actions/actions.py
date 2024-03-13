# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from flask import jsonify
from googletrans import Translator
import spacy
def detectar_stop_words(texto_a_analizar):
    # Carga el modelo de spaCy para español
    # python -m spacy download es_core_news_sm
    nlp = spacy.load('es_core_news_sm')

    # Procesa el texto
    doc = nlp(texto_a_analizar)
    # Filtra las stop words
    palabras_filtradas = [token.text for token in doc if not token.is_stop]
    return palabras_filtradas

def traducir_a_espanol(texto_a_traducir):
    translator = Translator()
        # Detecta automáticamente el idioma del texto de origen
    idioma_origen = translator.detect(texto_a_traducir).lang
    traduccion = translator.translate(texto_a_traducir, src=idioma_origen, dest='es')


    try:
        translator = Translator()
        # Detecta automáticamente el idioma del texto de origen
        idioma_origen = translator.detect(texto_a_traducir).lang

        traduccion = translator.translate(texto_a_traducir, src=idioma_origen, dest='es')
        return traduccion   
    except Exception as e:
        print('Salio por la excepcion  ',e)
        return e  

def traducir_mensaje_salida(texto_a_traducir, idioma_origen, idioma_destino):
    # Crea una instancia del traductor
    translator = Translator()

    # Traduce el texto al idioma de destino
    return translator.translate(texto_a_traducir, src=idioma_origen, dest=idioma_destino).text


# Ejemplos de uso:
"""texto_ejemplo = "This is an example sentence."
stop_words_filtradas = detectar_stop_words(texto_ejemplo)
texto_traducido = traducir_a_espanol(texto_ejemplo)
texto_traducido_destino = traducir_mensaje_salida(texto_ejemplo, 'en', 'es')

print("Stop Words Filtradas:", stop_words_filtradas)
print("Texto Traducido a Español:", texto_traducido)
print("Texto Traducido al Idioma Destino:", texto_traducido_destino)"""