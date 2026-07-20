import os
import requests
from dotenv import load_dotenv

load_dotenv()

MODELS = {
    "1": {"name": "OpenAI", "api_key": os.getenv("OPENAI_API_KEY"), "endpoint": "https://api.openai.com/v1/chat/completions"},
    "2": {"name": "Grok", "api_key": os.getenv("GROK_API_KEY"), "endpoint": "https://api.grok.x.ai/v1/chat/completions"},
    "3": {"name": "DeepSeek", "api_key": os.getenv("DEEPSEEK_API_KEY"), "endpoint": os.getenv("DEEPSEEK_ENDPOINT", "https://api.deepseek.com/v1/chat/completions")},
    "4": {"name": "Local (Ollama)", "api_key": "none", "endpoint": "http://localhost:11434/api/generate"},
}

def ask_model(choice, message, context):
    model = MODELS[choice]
    if choice == "4" or not model["api_key"]:
        return ask_local_ollama(message)
    
    payload = {
        "model": "gpt-4" if choice == "1" else "grok-1" if choice == "2" else "deepseek-chat",
        "messages": [
            {"role": "system", "content": f"You are Shadow Guide. Project: {context['project']}. Phase: {context['phase']}."},
            {"role": "user", "content": message}
        ]
    }
    headers = {"Authorization": f"Bearer {model['api_key']}", "Content-Type": "application/json"}
    try:
        resp = requests.post(model["endpoint"], headers=headers, json=payload, timeout=30)
        return resp.json()["choices"][0]["message"]["content"]
    except:
        return ask_local_ollama(message)

def ask_local_ollama(message):
    try:
        resp = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama2",
            "prompt": f"You are Shadow Guide. Help: {message}",
            "stream": False
        }, timeout=30)
        return resp.json()["response"]
    except:
        return "🌑 I'm offline, but I'm still with you."