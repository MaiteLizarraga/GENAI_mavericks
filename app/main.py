from saludo_inicial import saludo_inicial
from gdpr import solicitar_consentimiento_gdpr
from morosidad import solicitar_consentimiento_morosos
from slot_filling import iniciar_slot_filling_json

def main():
    # 1️⃣ Saludo inicial
    prompts = saludo_inicial()

    # 2️⃣ Solicitar consentimiento GDPR
    if not solicitar_consentimiento_gdpr():
        return  # Termina el programa si el usuario no consiente
    
    if not solicitar_consentimiento_morosos():
        return # Termina el programa si el usuario no consiente

    # 3️⃣ Slot filling / preguntas guiadas
    iniciar_slot_filling_json(prompts)

if __name__ == "__main__":
    main()
