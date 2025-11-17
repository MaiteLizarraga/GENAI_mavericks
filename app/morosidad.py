# ficheros_morosos.py
def solicitar_consentimiento_morosos():
    """
    Solicita al usuario su consentimiento para consultar o procesar
    información relacionada con ficheros de morosos.
    Devuelve True si acepta, False si no.
    """
    print("💬 Antes de continuar, necesitamos tu consentimiento para consultar ficheros de morosos y procesar esos datos según la LOPD/GDPR.")
    
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
    if solicitar_consentimiento_morosos():
        print("Usuario aceptó consultar ficheros de morosos")
    else:
        print("Usuario NO aceptó consultar ficheros de morosos")
