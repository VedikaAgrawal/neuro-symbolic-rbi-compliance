import os
from google import genai
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(env_path)

try:
    print("Listing available models for this key:")
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    for model in client.models.list():
        print(f" - {model.name} (supports: {model.supported_actions})")
except Exception as e:
    print(f"Failed to list models: {e}")
