# Ollama debe estar corriendo localmente en el puerto 11434.
# netstat -ano | findstr 11434

# import shutil
# from pathlib import Path

import pandas as pd
import requests

# # Ruta del archivo descargado desde Colab (en Descargas)
# archivo_descargado = Path(r"C:/Users/maite/Downloads/texto_extraido.csv")

# # Carpeta destino
# carpeta_docs = Path(r"C:/Users/maite/Desktop/DATASCIENCE_1/GENAI_mavericks/SIGP/docs")
# carpeta_docs.mkdir(parents=True, exist_ok=True)

# # Copiar archivo
# shutil.copy2(archivo_descargado, carpeta_docs)
# print(f"Archivo copiado a {carpeta_docs}")

# import torch
# torch.cuda.empty_cache()


# Cargar CSV
df = pd.read_csv(r"C:/Users/maite/Downloads/texto_extraido.csv")
text = df.loc[0, "texto"]

payload = {
    "model": "llama2:7b",
    "prompt": f"Extrae los nombres de personas de este contrato:\n\n{text[:3000]}"
}

response = requests.post("http://localhost:11434/api/generate", json=payload)

# Guardar cada línea de la respuesta en una lista
lines = response.text.split("\n")
print(lines)

resultado = [line.decode("utf-8") for line in response.iter_lines()]
print(resultado)
