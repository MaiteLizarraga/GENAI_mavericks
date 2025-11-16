from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")

def router_llm(state):
    pregunta = state["input"].lower()

    prompt = f"""
    Eres un clasificador de expertos para una entidad bancaria. Responde SOLO una palabra:
    - 'hipoteca' si la pregunta contiene cualquiera de las siguientes palabras o trata sobre hipotecas, préstamos, intereses o créditos.
    - 'faq' si trata de cualquier otra cosa relacionada con el banco.

    Pregunta: "{pregunta}"
    Respuesta:
    """

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=2,
        pad_token_id=tokenizer.eos_token_id
    )

    salida_completa = tokenizer.decode(outputs[0], skip_special_tokens=True)
    respuesta = salida_completa[len(prompt):].strip().lower()

    print(respuesta)
    if "hip" in respuesta:
        state["model"] = "hipotecas"
    else:
        state["model"] = "faq"

    return state
