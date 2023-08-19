import json
import chromadb
from django.http import JsonResponse
from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import requests
import spacy    
from harmonyProject import settings
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from nltk.translate.bleu_score import sentence_bleu
from google.cloud import translate_v2 as translate

from millyApp.chatbot.process import cargar_datos

#from rasa.core.agent import Agent
    
def generar_respuesta_openai(request, entrada):
    print("request: ", request)
    """rasa_url = request+'/preguntaAmilly'
    payload = {
        'message': entrada
    }
    response = requests.post(rasa_url, json=payload)
    """
    response= send_to_rasa(entrada)
    salida = response[0]
    print(">>response: ", response)
    return JsonResponse({'data': salida['text']})

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        data = request.POST
        user_message = data['user_message']

        rasa_response = send_to_rasa(user_message)
        return JsonResponse(rasa_response, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method'})

def send_to_rasa(message):
    rasa_url = 'http://localhost:5005/webhooks/rest/webhook'
    payload = {
        'sender': 'user_id',
        'message': message
    }
    response = requests.post(rasa_url, json=payload)
    return response.json()