import json
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

# Cargar modelo Bert
#modelo_importado = 'mrm8488/distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es'
#tokenizer = AutoTokenizer.from_pretrained(modelo_importado, do_lower_case=False)
#modelo = AutoModelForQuestionAnswering.from_pretrained(modelo_importado)
"""ruta = "millyApp/contexto/contexto.json"

def definir_pregunta(pregunta):
    # Cargar el modelo de procesamiento de lenguaje de spaCy
    nlpSpacy = spacy.load("es_core_news_lg")
    
    # Cargar el archivo JSON desde la ruta especificada
    with open(ruta, "r") as file:
        json_data = json.load(file)

    # Calcular la similitud de la pregunta con cada clave del JSON
    similarity_scores = {}
    for entry in json_data["informacion"]:
        doc1 = nlpSpacy(pregunta.lower())
        doc2 = nlpSpacy(' '.join(entry["entradas"]).lower())
        similarity_scores[entry["tag"]] = doc1.similarity(doc2)

    # Identificar la clave con la mayor similitud
    key_max_similarity = max(similarity_scores, key=similarity_scores.get)

    return key_max_similarity

"""

model_name = "gpt2"  # Puedes usar otras variantes como "gpt2-medium", "gpt2-large", etc.
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
@require_GET
def generar_respuesta_openai(request, entrada):
    """entrada = entrada.lower()
    tipo_pregunta = definir_pregunta(entrada)
    with open(ruta, 'r') as f:
        data = json.load(f)
        contexto = next(entry["respuestas"] for entry in data["informacion"] if entry["tag"] == tipo_pregunta)
    encode = tokenizer.encode_plus(entrada, contexto, return_tensors='pt')
    input_ids = encode['input_ids']
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0])     
    nlp = pipeline('question-answering', model=modelo, tokenizer=tokenizer)
    salida = nlp({'question': entrada, 'context': contexto})"""
    # Convertir la pregunta en tokens y generar la respuesta
    input_ids = tokenizer.encode(entrada, return_tensors="pt")
    output = model.generate(input_ids, max_length=100, num_return_sequences=1)
    respuesta_referencia = "La capital de Francia es París."

    respuesta_generada = tokenizer.decode(output[0], skip_special_tokens=True)
    respuesta_referencia = "La capital de Francia es París."
    generada_tokens = respuesta_generada.split()
    referencia_tokens = respuesta_referencia.split()
    bleu_score = sentence_bleu([referencia_tokens], generada_tokens)

    print("\n\n\n\n",respuesta_generada)
    print("porcentaje: ", bleu_score)

    print("\n\n\n\n")
    return JsonResponse({'data': respuesta_generada})