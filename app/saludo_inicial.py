from model_loader import model, tokenizer
import torch

def saludo_inicial():
    prompts = [
        {"role": "system", "content": """
            Trabajas en un banco y eres un asesor hipotecario experto.
            Saluda al cliente y dile que quieres ayudarle a conseguir su hipoteca.
            Dile que primero se han de hacer unas comprobaciones.
            """},
        {"role": "user", "content": "Hola, me gustaría comprar una casa pero necesito una hipoteca"}
    ]

    # Convertir prompts a texto simple para CPU
    input_text = "\n".join([f"{p['role']}: {p['content']}" for p in prompts])
    inputs = tokenizer(input_text, return_tensors="pt").to("cpu")  # fuerza CPU

    with torch.no_grad():  # evita cálculos de gradiente, ahorra memoria
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
            do_sample=True,       # más rápido que greedy
            temperature=0.7       # para respuestas variadas
        )

    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("Respuesta del agente:", generated_text)

    return prompts
