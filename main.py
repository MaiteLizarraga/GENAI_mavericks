import streamlit as st
from src.database import fetch_properties
from src.validation import Property
from src.agents import create_agent, ask_agent

st.title("Sistema Inteligente de Gestión de Propiedades (SIGP)")

# Mostrar propiedades
properties = fetch_properties()
st.write(properties)

# Crear agente y hacer preguntas
agent = create_agent()
question = st.text_input("Pregunta al agente:")
if question:
    answer = ask_agent(agent, question)
    st.write(answer)
