from model_loader import model, tokenizer

def saludo_inicial():
    prompts = [
        {"role": "system", "content": """
            Trabajas en un banco y eres un asesor hipotecario experto.
            Saluda al cliente y dile que quieres ayudarle a conseguir su hipoteca.
            Pero dile que primero se han de hacer unas comprobaciones.
            """},
        {"role": "user", "content": "Hola, me gustaría comprar una casa pero necesito una hipoteca"}
    ]

    inputs = tokenizer.apply_chat_template(
        prompts,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device)

    outputs = model.generate(**inputs, 
                            max_new_tokens=50)

    generated_text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])
    print("Respuesta del agente:", generated_text)
    
    return prompts
