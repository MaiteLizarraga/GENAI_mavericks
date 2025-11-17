# gdpr.py
def solicitar_consentimiento_gdpr():
    print("💬 Antes de continuar, necesitamos tu consentimiento para el tratamiento de datos (GDPR/LOPD).")
    while True:
        respuesta = input("¿Aceptas? (sí/no): ").strip().lower()
        if respuesta in ["sí", "si", "s", "yes"]:
            print("Gracias, puedes continuar.\n")
            return True
        elif respuesta == "no":
            print("No podemos continuar sin tu consentimiento. Fin del proceso.")
            return False
        else:
            print("Por favor, responde 'sí' o 'no'.")

if __name__ == "__main__":
    if solicitar_consentimiento_gdpr():
        print("Usuario aceptó GDPR")
    else:
        print("Usuario NO aceptó GDPR")
