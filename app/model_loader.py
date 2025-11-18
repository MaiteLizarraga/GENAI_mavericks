from dotenv import load_dotenv
import os
import logging
import warnings
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login

# --- Silenciar Warnings ---
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)


# --- Modelo ---
load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

login(token=hf_token)

# model_name = "Qwen/Qwen2.5-0.5B-Instruct"
model_name = "meta-llama/Llama-3.2-1B-Instruct"

# tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    # token=hf_token,
    device_map="auto",
    offload_folder="offload",
    torch_dtype="auto"
)

# print("Modelo cargado correctamente.")
