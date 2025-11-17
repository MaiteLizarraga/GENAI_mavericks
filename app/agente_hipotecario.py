"""
hipoteca_agent.py
Ejemplo de microservicio + agent simple con LangChain + Llama 2 (Hugging Face).
Incluye:
 - cálculo cuota (amortización francesa)
 - tabla de amortización
 - export CSV y PDF
 - integración básica con LangChain (prompt + slot filling)
"""

import os
import math
import json
import datetime
from typing import List, Dict, Any

import pandas as pd

# PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# LangChain + HuggingFaceHub
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI  # fallback if needed
from langchain import HuggingFaceHub

# -------------------------
# 1) Utilidades: cálculo
# -------------------------
def cuota_mensual(P: float, annual_rate_percent: float, years: int) -> float:
    if annual_rate_percent == 0:
        return P / (years * 12)
    r = annual_rate_percent / 100.0 / 12.0
    n = years * 12
    numerator = P * r * (1 + r) ** n
    denominator = (1 + r) ** n - 1
    return numerator / denominator

def generar_tabla_amortizacion(P: float, annual_rate_percent: float, years: int, start_date: datetime.date = None) -> pd.DataFrame:
    if start_date is None:
        start_date = datetime.date.today()
    r = annual_rate_percent / 100.0 / 12.0
    n = years * 12
    cuota = cuota_mensual(P, annual_rate_percent, years)
    saldo = P
    rows = []
    for i in range(1, n + 1):
        interes = saldo * r
        amortizacion = cuota - interes
        saldo_nuevo = max(0.0, saldo - amortizacion)
        fecha = start_date + datetime.timedelta(days=30 * i)  # aproximación
        rows.append({
            "mes": i,
            "fecha": fecha.isoformat(),
            "cuota": round(cuota, 2),
            "interes": round(interes, 2),
            "amortizacion": round(amortizacion, 2),
            "saldo": round(saldo_nuevo, 2)
        })
        saldo = saldo_nuevo
        if saldo <= 0:
            break
    df = pd.DataFrame(rows)
    return df

# -------------------------
# 2) Export CSV / PDF
# -------------------------
def export_csv(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False, encoding='utf-8')

def export_pdf_summary(simulation_meta: Dict[str, Any], df_amort: pd.DataFrame, path: str):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Simulación de Hipoteca - Resumen")
    y -= 24

    c.setFont("Helvetica", 10)
    for k, v in simulation_meta.items():
        c.drawString(margin, y, f"{k}: {v}")
        y -= 14
        if y < 100:
            c.showPage()
            y = height - margin

    # tabla: primeros 24 meses
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Tabla de amortización (primeros 24 meses)")
    y -= 18
    c.setFont("Helvetica", 8)

    # columns
    cols = ["mes", "fecha", "cuota", "interes", "amortizacion", "saldo"]
    row_h = 12
    col_w = (width - 2 * margin) / len(cols)
    # header
    x = margin
    for col in cols:
        c.drawString(x + 2, y, col)
        x += col_w
    y -= row_h

    for _, row in df_amort.head(24).iterrows():
        x = margin
        for col in cols:
            text = str(row[col])
            c.drawString(x + 2, y, text)
            x += col_w
        y -= row_h
        if y < margin + 40:
            c.showPage()
            y = height - margin

    c.save()

# -------------------------
# 3) Mock credit checks (dev)
# -------------------------
def mock_check_asnef(dni: str) -> Dict[str, Any]:
    """
    En desarrollo, devuelve falso positivo si el dni termina en 9 (ejemplo).
    Reemplazar por llamada real a bureau con consentimiento.
    """
    flagged = str(dni).strip()[-1] == "9"
    return {
        "dni": dni,
        "in_asnef": flagged,
        "details": "Mock: flagged by last-digit rule" if flagged else "Not found"
    }

def mock_check_cirbe(dni: str) -> Dict[str, Any]:
    """
    Mock: devuelve deuda total declarada en CIRBE (ejemplo).
    """
    # Generamos un valor pseudo-aleatorio (no real)
    base = int(dni[-2:]) if len(dni) >= 2 and dni[-2:].isdigit() else 0
    deuda = base * 1000
    return {
        "dni": dni,
        "deuda_total_reportada": deuda
    }

# -------------------------
# 4) LangChain integration (slot-filling agent demo)
# -------------------------
# NOTE: requires HUGGINGFACEHUB_API_TOKEN env var and LangChain with HuggingFaceHub support.
HF_TOKEN = os.environ.get("HUGGINGFACEHUB_API_TOKEN", None)
if not HF_TOKEN:
    print("WARNING: HUGGINGFACEHUB_API_TOKEN not set. LangChain LLM parts will not work until you set it.")

# Example using HuggingFaceHub via LangChain
def create_llm():
    # Ajusta repo_id a la versión de Llama 2 que tengas acceso (ej: 'meta-llama/Llama-2-7b-chat-hf')
    repo_id = os.environ.get("HF_LLAMA_REPO_ID", "meta-llama/Llama-2-7b-chat-hf")
    if not HF_TOKEN:
        raise EnvironmentError("Set HUGGINGFACEHUB_API_TOKEN to use HuggingFaceHub.")
    llm = HuggingFaceHub(repo_id=repo_id, model_kwargs={"temperature": 0.2, "max_new_tokens": 512})
    return llm

# Prompt template: el LLM guiará la conversacion, solicitando slots que falten.
PROMPT_TEMPLATE = """
Eres un asistente hipotecario. Tienes que recabar los siguientes datos del cliente para hacer una simulación:
- nombre_completo
- dni_nie_nif
- fecha_nacimiento
- direccion_postal
- telefono_email
- tipo_vivienda (nueva/segunda_mano)
- precio_vivienda
- entrada
- plazo_anos (10,15,20,25,30,35,40)
- tipo_interes (fijo/variable/mixto)
- tasa_interes_anual (si la conoce)
- ingresos_netos_mensuales
- fuente_ingresos
- gastos_mensuales_est
- situacion_laboral
- aportaciones_adicionales
- avalista (si/no)
- consentimiento_ficheros (sí/no)
- consentimiento_tratamiento_datos (sí/no)

Responde de forma natural, pero siempre verifica y solicita sólo los campos que faltan. Formatea la salida final como JSON con los slots completados.
Si recibes un número o campo mal formateado, pide confirmación.
Usuario: {user_input}
Slots previos: {slots_json}
"""

PROMPT = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["user_input", "slots_json"])

def run_agent_interaction(user_input: str, slots: Dict[str, Any]):
    """
    Ejecuta el LLM para pedir el siguiente dato o finalizar.
    """
    # Si el token no está presente, fallback a un mensaje local
    if not HF_TOKEN:
        # simple local fallback: ask the next missing slot
        for s in slots_order:
            if slots.get(s) in (None, ""):
                question = next(slot_map[s]['prompt'] for _ in [0])
                return {"response_text": f"{question}", "updated_slots": slots}
        return {"response_text": "Tengo todos los datos. ¿Quieres que calcule la simulación?", "updated_slots": slots}

    llm = create_llm()
    chain = LLMChain(llm=llm, prompt=PROMPT)
    slots_json = json.dumps(slots_json, ensure_ascii=False)
    out = chain.run({"user_input": user_input, "slots_json": slots_json})
    # El LLM debe devolver JSON final o pregunta. Aquí devolvemos texto crudo.
    return {"response_text": out, "updated_slots": slots}

# -------------------------
# 5) Ejemplo de uso (script)
# -------------------------
slot_map = {
    "cliente_es_cliente_banco": {"prompt": "¿Eres cliente del banco? (sí/no)"},
    "nombre_completo": {"prompt": "Dime tu nombre completo"},
    "dni_nie_nif": {"prompt": "Dime tu DNI/NIE/NIF"},
    "fecha_nacimiento": {"prompt": "Fecha de nacimiento (DD/MM/YYYY)"},
    "direccion_postal": {"prompt": "Dirección postal"},
    "telefono_email": {"prompt": "Teléfono o email"},
    "tipo_vivienda": {"prompt": "Tipo de vivienda (nueva/segunda_mano)"},
    "precio_vivienda": {"prompt": "Precio de la vivienda en €"},
    "entrada": {"prompt": "Entrada disponible en €"},
    "plazo_anos": {"prompt": "Plazo en años (ej: 30)"},
    "tipo_interes": {"prompt": "Tipo de interés (fijo/variable/mixto)"},
    "tasa_interes_anual": {"prompt": "Tasa nominal anual (%) o 'no'"},
    "ingresos_netos_mensuales": {"prompt": "Ingresos netos mensuales (€)"},
    "fuente_ingresos": {"prompt": "Fuente de ingresos (nomina/autonomo/pension)"},
    "gastos_mensuales_est": {"prompt": "Gastos mensuales estimados (€)"},
    "situacion_laboral": {"prompt": "Situación laboral"},
    "aportaciones_adicionales": {"prompt": "Aportaciones adicionales (€)"},
    "avalista": {"prompt": "¿Tienes avalista? (sí/no)"},
    "consentimiento_ficheros": {"prompt": "¿Das consentimiento para consultar ficheros? (sí/no)"},
    "consentimiento_tratamiento_datos": {"prompt": "¿Das consentimiento para el tratamiento de datos? (sí/no)"}
}
slots_order = list(slot_map.keys())

def ejemplo_workflow_sin_llm():
    # ejemplo minimalista sin LLM: rellenamos algunos datos, luego calculamos
    slots = {
        "cliente_es_cliente_banco": True,
        "nombre_completo": "María Pérez",
        "dni_nie_nif": "12345678A",
        "fecha_nacimiento": "01/01/1990",
        "direccion_postal": "C/ Falsa 123, Madrid, 28001",
        "telefono_email": "+34 600000000 / mperez@example.com",
        "tipo_vivienda": "segunda_mano",
        "precio_vivienda": 220000,
        "entrada": 40000,
        "plazo_anos": 30,
        "tipo_interes": "fijo",
        "tasa_interes_anual": 3.5,
        "ingresos_netos_mensuales": 2400,
        "fuente_ingresos": "nomina",
        "gastos_mensuales_est": 400,
        "situacion_laboral": "indefinido",
        "aportaciones_adicionales": 5000,
        "avalista": False,
        "consentimiento_ficheros": True,
        "consentimiento_tratamiento_datos": True
    }

    # mock checks
    asnef_res = mock_check_asnef(slots["dni_nie_nif"])
    cirbe_res = mock_check_cirbe(slots["dni_nie_nif"])

    # compute financing
    importe_financiar = slots.get("precio_vivienda") - slots.get("entrada")
    cuota = cuota_mensual(importe_financiar, slots.get("tasa_interes_anual", 0.0), slots.get("plazo_anos"))
    tabla = generar_tabla_amortizacion(importe_financiar, slots.get("tasa_interes_anual", 0.0), slots.get("plazo_anos"))

    # export
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = f"simulacion_{slots['dni_nie_nif']}_{timestamp}.csv"
    pdf_path = f"simulacion_{slots['dni_nie_nif']}_{timestamp}.pdf"
    export_csv(tabla, csv_path)

    meta = {
        "cliente": slots["nombre_completo"],
        "dni": slots["dni_nie_nif"],
        "importe_financiar": round(importe_financiar, 2),
        "plazo_anos": slots["plazo_anos"],
        "tasa_interes_anual": slots["tasa_interes_anual"],
        "cuota_mensual": round(cuota, 2),
        "asnef": asnef_res,
        "cirbe": cirbe_res
    }
    export_pdf_summary(meta, tabla, pdf_path)

    return {
        "meta": meta,
        "csv_path": csv_path,
        "pdf_path": pdf_path,
        "tabla_head": tabla.head(12).to_dict(orient="records")
    }

# -------------------------
# Si ejecutamos como script
# -------------------------
if __name__ == "__main__":
    result = ejemplo_workflow_sin_llm()
    print("Simulación generada:")
    print(json.dumps(result["meta"], indent=2, ensure_ascii=False))
    print("CSV:", result["csv_path"])
    print("PDF:", result["pdf_path"])
    print("Primeros meses (muestra):")
    for r in result["tabla_head"]:
        print(r)
