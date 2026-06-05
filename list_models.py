import os
import google.generativeai as genai
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(env_path)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    print("Listing available models for this key:")
    for model in genai.list_models():
        print(f" - {model.name} (supports: {model.supported_generation_methods})")
except Exception as e:
    print(f"Failed to list models: {e}")
