from transformers import GPTNeoForCausalLM, GPTNeoTokenizer

model_name = "EleutherAI/gpt-neo-2.7B"
model = GPTNeoForCausalLM.from_pretrained(model_name)
tokenizer = GPTNeoTokenizer.from_pretrained(model_name)


# Función para generar respuestas del chatbot
def generate_response(input_text):
    # Preprocesar la entrada
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    
    # Generar la respuesta
    output = model.generate(input_ids, max_length=50, num_return_sequences=1)
    
    # Decodificar la salida en texto legible
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return response