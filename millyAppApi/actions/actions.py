from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from random import choice

class ActionPreguntarVersion(Action):
    def name(self) -> Text:
        return "action_preguntar_version"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        respuestas = [
            "Mi versión es 1.0.0",
            "Actualmente estoy en la versión 2.0.0",
            "Estoy ejecutando la versión 3.0.0"
        ]

        respuesta_seleccionada = choice(respuestas)
        dispatcher.utter_message(text=respuesta_seleccionada)

        return []
