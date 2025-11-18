from model_loader import model, tokenizer
import re
from datetime import datetime

def validar_con_modelo(slot, user_input):
    """
    Extrae y limpia la respuesta del usuario usando el LLM.
    Devuelve un valor limpio o None si no cumple los requisitos.
    """
    prompt = f"""
    Eres un asistente que extrae información precisa de un cliente.
    Solo devuelve el valor solicitado, sin explicaciones adicionales.

    Pregunta: {slot['prompt']}
    Respuesta del cliente: {user_input}

    Reglas estrictas:
    """

    if slot["name"] == "nombre_completo":
        prompt += """
        - DEVUELVE SOLO EL VALOR: el NOMBRE y DOS APELLIDOS.
        - Ejemplo válido: 'Juan Pérez García'
        - Ejemplo NO válido: 'Juan Pérez', 'Maite', 'Pérez García'
        - Si no cumple, devuelve 'INCOMPLETO'.
        """
    elif slot["name"] == "dni_nie":
        prompt += """
        - El DNI/NIE debe tener un formato válido:
            - 8 cifras seguidas de una letra (ej. '12345678A')
            - una letra inicial (X, Y o Z) seguida de 7 cifras y una letra final (ej. 'X1234567A')
        - No son válidos números incompletos ni letras faltantes (ej. '12345678', '1234567', 'X1234567')
        - Si el valor NO cumple el formato, devuelve 'INCOMPLETO'.
        - Si el valor SÍ cumple el formato, devuelve el valor EXACTO sin modificaciones.
            Ejemplos:
		- Entrada: '44153821P' → Salida: '44153821P'
		- Entrada: 'X1234567A' → Salida: 'X1234567A'
		- Entrada: '12345678' → Salida: 'INCOMPLETO'
		- Entrada: 'X1234567' → Salida: 'INCOMPLETO'

		Devuelve solo el valor limpio o 'INCOMPLETO'.
        """
    elif slot["type"] == "date":
        prompt += """
        - La fecha debe estar en formato DD/MM/YYYY.
        - Ejemplo válido: '31/12/2025'
        - Ejemplo NO válido: '31-12-2025', '2025/12/31'
        - Si el formato es incorrecto, devuelve 'INCOMPLETO'.
        - La fecha debe ser válida, no hay más de 31 días en los meses, ni 12 meses en el año.
        - La persona debe ser mayor de edad. Su edad no debe ser menor a 18 años restando a la fecha de hoy la fecha de nacimiento
        """
    elif slot["type"] == "boolean":
        prompt += """
        - Convierte la respuesta a 'sí' o 'no'.
        - Ejemplo válido: 'sí', 'no'
        - Ejemplo NO válido: 'tal vez', 'no sé'
        - Si no es claro, devuelve 'INCOMPLETO'.
        """
    elif slot["type"] == "telefono":
        prompt += """
        - Valida que la respuesta sea un número de teléfono válido siguiendo estas reglas:
            1. Prefijo de 2 o 3 cifras:
                - Fijo: empieza por 9
                - Móvil: empieza por 6 o 7
            2. Siguientes cifras: 7 o 6 dígitos para completar el número
            3. El número total **no debe superar las 9 cifras**
        - Ejemplo válido: '912345678' (fijo), '612345678' (móvil)
        - Ejemplo NO válido: '512345678' (prefijo incorrecto)
        - Ejemplo NO válido: '9123456789' (más de 9 cifras)
        - Si cumple los criterios, devuelve el número tal cual.
        - Si no cumple o es ambiguo, devuelve 'INCOMPLETO'.
        """
    # elif slot["type"] == "email":
    #     prompt += """
    #     - Valida que la respuesta sea una dirección de correo electrónico válida:
    #         1. Contiene exactamente un '@'.
    #         2. Tiene al menos un carácter antes del '@'.
    #         4. Solo se permiten letras, números, guiones (-), guion bajo (_) y puntos (.) en el nombre y dominio.
    #         5. No se permiten espacios.
    #     - Ejemplo válido: 'usuario@example.com', 'nombre.apellido@empresa.es', 'mliztellez@gmail.co'
    #     - Ejemplo NO válido: 'usuario@@example.com', 'usuario@', 'usuario example.com', 'm@g'
    #     - Devuelve el email tal cual si cumple los criterios.
    #     - Si no cumple o es ambiguo, devuelve 'INCOMPLETO'.
    #     """
    # prompt += "\nDevuelve solo el valor limpio o 'INCOMPLETO'."

    try:
        inputs = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True
        ).to(model.device)
        output = model.generate(**inputs, max_new_tokens=50)
        raw_response = tokenizer.decode(output[0], skip_special_tokens=True).strip()
        last_response = raw_response.split("\n")[-1].strip()

        # Validación estricta para nombre completo
        if slot["name"] == "nombre_completo":
            palabras = re.findall(r'\b\w+\b', last_response)
            if len(palabras) < 3:
                return None  # INCOMPLETO
            return " ".join(palabras[:3])  # Nombre + 2 apellidos

        if slot["name"] == "dni_nie":
            if last_response.upper() == "INCOMPLETO":
                return None
            # Validar formato con regex
            if not re.match(r'^([0-9]{8}[A-Za-z]|[XYZxyz][0-9]{7}[A-Za-z])$', last_response):
                return None
            return last_response
        
        # Validación para otros slots
        if last_response.upper() == "INCOMPLETO":
            return None

        if slot["type"] == "date":
            try:
                datetime.strptime(last_response, "%d/%m/%Y")
            except ValueError:
                return None
        elif slot["type"] == "boolean":
            v_lower = last_response.lower()
            if v_lower in ["sí", "si", "s", "yes"]:
                return True
            elif v_lower in ["no", "n"]:
                return False
            else:
                return None

        return last_response or None
    except Exception as e:
        print(f"Error al generar respuesta: {e}")
        return None