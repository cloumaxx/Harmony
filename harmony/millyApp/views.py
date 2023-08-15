import json
import chromadb
from django.http import JsonResponse
from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import spacy    
from harmonyProject import settings
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from nltk.translate.bleu_score import sentence_bleu
from google.cloud import translate_v2 as translate

from millyApp.chatbot.process import cargar_datos

"""ruta = "millyApp/contexto/contexto.json"""

model_name = 'gpt2'
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)


@require_GET
def generar_respuesta_openai(request, entrada):
    
    return JsonResponse({'data': 'hola'})
