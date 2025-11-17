import os
import json
import requests
import pyttsx3
import pyaudio
import wave
from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer
from langchain.prompts import ChatPromptTemplate
from langchain.llms.base import LLM
from typing import Optional, List

# 1. CUSTOM LLM: HuggingFace Inference API (LLaMA 2)

# Carga el token de Hugging Face para llama 2

load_dotenv()  # carga automáticamente el .env
hf_token  = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Llama al modelo Llama 2 en Hugging Face

class HFLLama2(LLM):
    hf_model: str = "meta-llama/Llama-2-7b-chat-hf"
    temperature: float = 0.3

    @property
    def _llm_type(self):
        return "huggingface_llama2_inferenceapi"

    def _call(self, prompt: str, stop: Optional[List[str]] = None):
        headers = {
            "Authorization": f"Bearer {hf_token}",  # usamos la variable cargada
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": self.temperature,
                "max_new_tokens": 200
            }
        }
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{self.hf_model}",
            headers=headers,
            data=json.dumps(payload)
        )
        resp_json = response.json()
        if isinstance(resp_json, list):
            return resp_json[0]["generated_text"]
        else:
            return resp_json.get("generated_text", "")
        
# PROBAR EL MODELO

if __name__ == "__main__":
    llm = HFLLama2()

    prompt = "Hola, ¿puedes resumir en una frase qué es una hipoteca?"

    print("Enviando solicitud al modelo...")
    respuesta = llm(prompt)

    print("\n--- RESPUESTA ---\n")
    print(respuesta)