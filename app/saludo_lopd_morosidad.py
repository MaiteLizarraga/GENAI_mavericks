from model_loader import llm

def saludo_inicial():
    # --- Prompt general para Groq ---
    prompts = [
        {"role": "system", "content": """
            Eres un asesor hipotecario experto que interactúa con un cliente.
            Saluda al cliente y muestra disposición a ayudarle.
            Termina cada mensaje de manera natural, preferiblemente con una sola frase principal.
            No incluyas explicaciones de ingresos, gastos o presupuestos aún.
        """},
        {"role": "user", "content": "Hola, me gustaría comprar una casa pero necesito una hipoteca"}
    ]

    # Convertir prompts a texto plano
    input_text = "\n".join([f"{p['role']}: {p['content']}" for p in prompts])

    # Llamada al modelo Groq con límite de tokens
    respuesta = llm.invoke(input_text, max_tokens=60)
    generated_text = respuesta.content.strip()

    # Cortamos por frases completas
    frases = [f.strip() for f in generated_text.split(".") if f.strip()]
    
    # Tomamos solo la primera frase para el saludo inicial
    saludo_texto = frases[0] + "."
    print("Agente:", saludo_texto)
    input("Tú: ")  # Espera respuesta del cliente

    # --- Solicitar GDPR generado por el modelo ---
    gdpr_prompt = (
        "Ahora solicita al cliente que acepte la política de protección de datos "
        "de manera natural y breve, usando solo una frase."
    )
    respuesta_gdpr = llm.invoke(gdpr_prompt, max_tokens=40)
    gdpr_texto = respuesta_gdpr.content.strip().split(".")[0] + "."
    print("\nAgente:", gdpr_texto)
    
    consentimiento_gdpr = input("Tú (escriba 'sí' para aceptar): ").strip().lower()
    while consentimiento_gdpr not in ["sí", "si", "s", "yes"]:
        print("Agente: Necesitamos que aceptes la política de protección de datos para continuar.")
        consentimiento_gdpr = input("Tú (escribe 'sí' para aceptar): ").strip().lower()
    
    print("Agente: Gracias por aceptar la política de protección de datos.")

    # --- Solicitar permiso fichero de morosos generado por el modelo ---
    morosos_prompt = (
        "Ahora solicita permiso al cliente para consultar el fichero de morosos del Banco de España, "
        "de manera natural y breve, usando solo una frase."
    )
    
    respuesta_morosos = llm.invoke(morosos_prompt, max_tokens=40)
    morosos_texto = respuesta_morosos.content.strip().split(".")[0] + "."
    print("\nAgente:", morosos_texto)
    permiso_morosos = input("Tú (escribe 'sí' para aceptar): ").strip().lower()
    
    while permiso_morosos not in ["sí", "si", "s", "yes"]:
        print("Agente: Necesitamos tu permiso para consultar el fichero de morosos para continuar.")
        permiso_morosos = input("Tú (escribe 'sí' para aceptar): ").strip().lower()
    
    print("Agente: Perfecto, gracias por tu permiso.")

    return prompts
