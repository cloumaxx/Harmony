from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
import json
import spacy

# Cargar modelo Bert
modelo_importado = 'mrm8488/distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es'
tokenizer = AutoTokenizer.from_pretrained(modelo_importado, do_lower_case=False)
modelo = AutoModelForQuestionAnswering.from_pretrained(modelo_importado)
ruta = "harmonyApp/chatbot/contexto/contexto.json"

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
def respuesta_modelo_bert_contexto(pregunta):
    tipo_pregunta = definir_pregunta(pregunta)
    #print("tipo_pregunta", tipo_pregunta, type(tipo_pregunta))
    #print("pregunta:", pregunta, "clasificacion", definir_pregunta(pregunta))
    with open(ruta, 'r') as f:
        data = json.load(f)
        contexto = next(entry["respuestas"] for entry in data["informacion"] if entry["tag"] == tipo_pregunta)
    #print("contexto:", contexto)
    encode = tokenizer.encode_plus(pregunta, contexto, return_tensors='pt')
    input_ids = encode['input_ids']
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
       
    nlp = pipeline('question-answering', model=modelo, tokenizer=tokenizer)

    salida = nlp({'question': pregunta, 'context': contexto})
    print(salida)    
    return salida

