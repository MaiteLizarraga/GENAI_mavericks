from langchain_groq import ChatGroq
from langchain.agents import Tool, initialize_agent
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import re
from dotenv import load_dotenv

# ------------------------------------------
# 1. MODELO GROQ (REMOTO Y GRATIS)
# ------------------------------------------

load_dotenv()

prompt = PromptTemplate(
    input_variables=["input"],
    template="Eres un asistente hipotecario profesional. {input}"
)

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_TOKEN"),
    model_name="llama-3.1-8b-instant",
    temperature=0.2
)

# ------------------------------------------
# 2. TOOLS
# ------------------------------------------

def calcular_cuota_texto(texto):
    numeros = list(map(float, re.findall(r"\d+", texto)))
    if len(numeros) >= 2:
        prestamo = numeros[0]
        anos = numeros[1]
        interes_anual = 0.03
        i = interes_anual / 12
        n = anos * 12
        cuota = prestamo * (i * (1 + i)**n) / ((1 + i)**n - 1)
        return f"La cuota mensual aproximada es {round(cuota,2)} €."
    else:
        return "Por favor dime el monto del préstamo y los años."

def obtener_tipo_interes(texto):
    return "El tipo de interés fijo actual aproximado es del 3%."

tools = [
    Tool(
        name="calcular_cuota",
        func=calcular_cuota_texto,
        description="Calcula la cuota mensual a partir de texto natural."
    ),
    Tool(
        name="obtener_tipo_interes",
        func=obtener_tipo_interes,
        description="Devuelve el tipo de interés fijo actual."
    )
]

# ------------------------------------------
# 3. CREAR AGENTE
# ------------------------------------------

agente = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
    max_iterations=1
)


# ------------------------------------------
# 4. LOOP DE CHAT
# ------------------------------------------
print("Agente hipotecario listo. Escribe 'salir' para cerrar.\n")

while True:
    pregunta = input("Tú: ")
    if pregunta.lower() in ["salir", "exit", "quit"]:
        print("Agente: ¡Hasta luego!")
        break

    respuesta = agente.invoke({"input": pregunta})
    print("Agente:", respuesta)
    print()
