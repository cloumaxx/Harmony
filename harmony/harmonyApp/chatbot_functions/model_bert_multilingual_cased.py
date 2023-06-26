from transformers import GPT2Tokenizer, TFGPT2LMHeadModel

# Cargar el tokenizer y el modelo DialoGPT preentrenado en PyTorch
tokenizer = GPT2Tokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = TFGPT2LMHeadModel.from_pretrained("microsoft/DialoGPT-medium")

# Función para generar respuestas del chatbot
def obtener_respuesta(pregunta, contexto):
    print(pregunta)
    input_ids = tokenizer.encode(pregunta, return_tensors="tf")

    response = model.generate(input_ids, max_length=100)
    response_text = tokenizer.decode(response[:, input_ids.shape[-1]:][0], skip_special_tokens=True)

    print("-->", response)

    return response_text
