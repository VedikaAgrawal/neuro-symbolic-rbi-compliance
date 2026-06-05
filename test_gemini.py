import os
from dotenv import load_dotenv

# 1. Load environment variables from backend/.env
env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(env_path)

print("===============================================")
echo_key = os.getenv("GEMINI_API_KEY")
if not echo_key:
    print("❌ Error: GEMINI_API_KEY is missing in backend/.env!")
    print("Please paste your key in backend/.env on line 7.")
    exit(1)

print(f"🔑 Loaded GEMINI_API_KEY: {echo_key[:8]}...{echo_key[-4:] if len(echo_key) > 12 else ''}")
print("===============================================")

try:
    print("📦 Importing google-generativeai package...")
    import google.generativeai as genai
except ImportError:
    print("❌ Error: google-generativeai package is not installed in this environment.")
    print("Please run: ./venv/bin/pip install google-generativeai")
    exit(1)

# 2. Configure Gemini API client
genai.configure(api_key=echo_key)

try:
    print("🚀 Initializing model 'gemini-3.5-flash'...")
    model = genai.GenerativeModel("gemini-3.5-flash")
    
    print("📡 Sending test request to Google Servers...")
    prompt = "Hello! Please reply with exactly: 'Gemini API is successfully connected and fully operational!'"
    
    response = model.generate_content(prompt)
    
    print("\n🟢 SUCCESS! Server Response:")
    print("-----------------------------------------------")
    print(response.text.strip())
    print("-----------------------------------------------")
    
except Exception as e:
    print("\n🔴 FAILURE! Gemini connection failed.")
    print("-----------------------------------------------")
    print(f"Error details: {e}")
    print("-----------------------------------------------")
    print("\n💡 Troubleshooting Tips:")
    print("1. Check if your API Key is correct and has no extra spaces or quotation marks.")
    print("2. Check if your computer has an active internet connection.")
    print("3. Verify if your API key has expired or has quota limits on Google AI Studio.")
print("===============================================")
