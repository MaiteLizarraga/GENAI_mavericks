from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator
from typing import Annotated
import re
from model_loader import llm
from db_new_clients import crear_registro_vacio, actualizar_campo

# --- Mini-modelos por slot para Pydantic (solo los que necesitan validación estricta) ---
def modelo_slot(slot_name):
    if slot_name == "nombre_completo":
        class M(BaseModel):
            nombre_completo: Annotated[str, Field(min_length=3)]
        return M
    elif slot_name == "dni_nie":
        class M(BaseModel):
            dni_nie: Annotated[str, Field(pattern=r'^([0-9]{8}[A-Za-z]|[XYZxyz][0-9]{7}[A-Za-z])$')]
        return M
    elif slot_name == "fecha_nacimiento":
        class M(BaseModel):
            fecha_nacimiento: date

            @field_validator("fecha_nacimiento")
            def mayor_de_edad(cls, v):
                hoy = date.today()
                edad = hoy.year - v.year - ((hoy.month, hoy.day) < (v.month, v.day))
                if edad < 18:
                    raise ValueError("El cliente debe ser mayor de 18 años")
                return v
        return M
    elif slot_name == "telefono":
        class M(BaseModel):
            telefono: Annotated[str, Field(pattern=r'^[6-9]\d{8}$')]
        return M
    elif slot_name == "email":
        class M(BaseModel):
            email: EmailStr
        return M
    elif slot_name in ["precio_vivienda", "entrada", "importe_a_financiar",
                       "ingresos_netos_mensuales", "gastos_mensuales_est", "tasa_interes_anual"]:
        class M(BaseModel):
            __annotations__ = {slot_name: float}
        return M
    elif slot_name == "plazo_anos":
        class M(BaseModel):
            plazo_anos: Annotated[int, Field(gt=0)]
        return M
    else:
        # Para cualquier otro campo que sea string
        class M(BaseModel):
            __annotations__ = {slot_name: str}
        return M

def normalizar_booleano(texto):
    if not isinstance(texto, str):
        return None

    t = texto.lower().strip()

    # Eliminar puntuación y basura
    t = re.sub(r"[^a-záéíóúüñ]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()

    # Matches robustos
    afirmativos = ["si", "sí", "s", "claro", "correcto", "afirmativo"]
    negativos = ["no", "n", "negativo"]

    palabras = t.split()

    if any(p in palabras for p in afirmativos):
        return True
    if any(p in palabras for p in negativos):
        return False

    return None


# --- Validación de un solo slot usando LLM + Pydantic ---
def validar_slot(slot, user_input):
    # LLM limpia/normaliza la respuesta
    prompt = f"""
    Eres un asistente que extrae información precisa de un cliente.
    Pregunta: {slot['prompt']}
    Respuesta del cliente: {user_input}
    Solo limpia y devuelve el valor exactamente como el cliente lo escribió. 
    Para el resto de datos que no sean la fecha, no interpretes si es correcto o no, ni agregues comentarios. 
    Devuelve solo el valor limpio o 'INCOMPLETO'.
    """
    respuesta = llm.invoke(prompt, max_tokens=50)
    valor = respuesta.content.strip()
    print(valor)
    if slot["name"] == "dni_nie":
        match = re.search(r'([0-9]{8}[A-Za-z]|[XYZxyz][0-9]{7}[A-Za-z])', valor)
        if match:
            valor = match.group(1)
    if valor.upper() == "INCOMPLETO":
        return None

    # Normalización para booleanos (sin Pydantic)
    if slot["type"] == "boolean":
        valor_bool = normalizar_booleano(valor)
        return valor_bool

    # Normalización para fechas
    # if slot["type"] == "date":
    #     try:
    #         valor = datetime.strptime(valor, "%d/%m/%Y").date()
    #     except ValueError:
    #         return None

    # Normalización para números
    if slot["type"] == "number":
        try:
            valor = float(re.sub(r"[^\d.,]", "", valor).replace(",", "."))
        except ValueError:
            return None
    if slot["name"] == "telefono":
        valor = re.sub(r"[^\d]", "", valor)
    # Validación con Pydantic para los slots que necesitan reglas estrictas
    if slot["type"] in ["string", "number", "contact"]:
        Modelo = modelo_slot(slot["name"])
        try:
            m = Modelo(**{slot["name"]: valor})
            return getattr(m, slot["name"])
        except ValidationError:
            return None

    return valor

# --- Flujo de slot filling ---
def obtener_datos_hipoteca(slots):
    # Crear el registro vacío
    cliente_id = crear_registro_vacio()

    datos = {}

    for slot in slots:
        while True:
            slot_prompt = f"Pregunta al cliente por su {slot['name']} de manera clara y concisa."
            respuesta_slot = llm.invoke(slot_prompt, max_tokens=50)
            pregunta = respuesta_slot.content.strip().split("?")[0] + "?"
            print("\nAgente:", pregunta)

            valor = input("Tú: ")

            valor_validado = validar_slot(slot, valor)

            if valor_validado is None:
                print("Agente: La respuesta no es válida, por favor inténtalo de nuevo.")
                continue

            # Guardar en memoria del script
            datos[slot["name"]] = valor_validado

            # Guardar en la base de datos inmediatamente
            actualizar_campo(cliente_id, slot["name"], valor_validado)

            break

    return cliente_id, datos
