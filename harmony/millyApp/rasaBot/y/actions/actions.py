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
from googletrans import Translator
import spacy
import enchant

def detectarStopWords(texto_a_analizar):
    # Carga el modelo de spaCy para español
    nlp = spacy.load('es_core_news_sm')

    doc = nlp(texto_a_analizar)
    palabras_filtradas = [token.text for token in doc if not token.is_stop]
    if len(palabras_filtradas) > 0:

        # Crea un objeto de diccionario para el español
        diccionario_espanol = enchant.Dict("es_ES")


        # Filtra palabras que no están en el diccionario en español
        palabras_filtradasSalida = [palabra for palabra in palabras_filtradas if diccionario_espanol.check(palabra)]
    return palabras_filtradasSalida

def traducirAEspañol(texto_a_traducir):
    # Crea una instancia del traductor
    translator = Translator()

    # Detecta automáticamente el idioma del texto de origen
    idioma_origen = translator.detect(texto_a_traducir).lang
    # Traduce el texto a español
    return translator.translate(texto_a_traducir, src=idioma_origen, dest='es')#.text

def traducirMensajeSalida(texto_a_traducir, idioma_origen, idioma_destino):
    # Crea una instancia del traductor
    translator = Translator()    
    # Traduce el texto al idioma de destino
    return translator.translate(texto_a_traducir, src=idioma_origen, dest=idioma_destino).text
