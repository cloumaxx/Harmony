from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Cargar el modelo y el tokenizador de GPT-2
model_name = 'gpt2'
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Función para generar respuestas del chatbot
import torch

def obtener_respuesta(pregunta, contexto):
    input_ids = tokenizer.encode(pregunta, return_tensors='pt')
    
    # Set the seed for reproducibility
    torch.manual_seed(0)
    
    # Generate text using greedy search
    output = model.generate(input_ids, max_length=100, num_return_sequences=1, temperature=1.0, early_stopping=True)
    
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    print(len(generated_text),type(generated_text))
    print(generated_text)
    return generated_text
