"""
models.py — Multi-provider chat model router.

Supports OpenAI, Groq, DeepSeek, and Ollama (cloud or local, via OLLAMA_ENDPOINT).
Because conversation memory lives in a single shared database
(see memory.py), switching between providers mid-conversation
does not lose history — every provider is handed the same
recalled context regardless of which one answers a given turn.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

MODELS = {
    "1": {
        "name": "OpenAI",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "format": "openai",
    },
    "2": {
        "name": "Groq",
        "api_key": os.getenv("GROQ_API_KEY"),
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "format": "openai",
    },
    "3": {
        "name": "DeepSeek",
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "endpoint": os.getenv("DEEPSEEK_ENDPOINT", "https://api.deepseek.com/v1/chat/completions"),
        "model": "deepseek-chat",
        "format": "openai",
    },
    "4": {
        "name": "Ollama",
        "api_key": os.getenv("OLLAMA_API_KEY"),  # set this for ollama.com cloud; leave blank for local
        "endpoint": os.getenv("OLLAMA_ENDPOINT", "https://ollama.com/api/chat"),
        "model": os.getenv("OLLAMA_MODEL", "gpt-oss:20b"),
        "format": "ollama",
    },
}


def list_models():
    """Return the model menu with availability flags."""
    result = {}
    for k, v in MODELS.items():
        if v["format"] == "ollama":
            is_local = "localhost" in v["endpoint"] or "127.0.0.1" in v["endpoint"]
            available = bool(v["api_key"]) or is_local
        else:
            available = bool(v["api_key"])
        result[k] = {"name": v["name"], "available": available}
    return result


def summarize_history(rows, existing_summary="", use_local=True):
    """
    Condense old (id, role, content) rows into an updated short summary blurb,
    folding them into whatever summary already existed. Runs on Ollama
    by default, since summarization doesn't need your paid cloud model and
    would otherwise burn tokens on every rollover.
    """
    if not rows:
        return existing_summary

    transcript = "\n".join(f"{role}: {content}" for _, role, content in rows)
    prompt = (
        "Update the running summary below with the new conversation excerpt. "
        "Keep it to 3-5 sentences, factual, no commentary — just what was "
        "discussed/decided, so it can serve as background context later.\n\n"
        f"Existing summary: {existing_summary or '(none yet)'}\n\n"
        f"New excerpt:\n{transcript}\n\n"
        "Updated summary:"
    )

    if use_local:
        result = _ask_ollama(prompt)
    else:
        result = ask_model("1", prompt)

    return result.strip()


def ask_model(choice, message, history=None, system_prompt=None):
    """
    Send a message (plus recent history) to the selected model.
    Falls back to Ollama (cloud or local) if the chosen provider errors out
    or has no API key configured.
    """
    model = MODELS.get(choice)
    if not model:
        return "Invalid model choice."

    if model["format"] != "ollama" and not model["api_key"]:
        return _ask_ollama(message, history, system_prompt)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    for role, content in (history or []):
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})

    try:
        if model["format"] == "ollama":
            return _ask_ollama(
                message, history, system_prompt,
                endpoint=model["endpoint"], model_name=model["model"], api_key=model["api_key"],
            )

        payload = {"model": model["model"], "messages": messages, "temperature": 0.7, "max_tokens": 1000}
        headers = {"Authorization": f"Bearer {model['api_key']}", "Content-Type": "application/json"}
        resp = requests.post(model["endpoint"], headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        fallback = _ask_ollama(message, history, system_prompt)
        return f"[{model['name']} unavailable: {e}]\n{fallback}"


def _ask_ollama(message, history=None, system_prompt=None, endpoint=None, model_name=None, api_key=None):
    endpoint = endpoint or os.getenv("OLLAMA_ENDPOINT", "https://ollama.com/api/chat")
    model_name = model_name or os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
    api_key = api_key if api_key is not None else os.getenv("OLLAMA_API_KEY")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    for role, content in (history or []):
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        resp = requests.post(
            endpoint,
            json={"model": model_name, "messages": messages, "stream": False},
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if "message" in data:
            return data["message"]["content"]
        if "response" in data:
            return data["response"]
        return f"Unexpected Ollama response: {json.dumps(data)[:200]}"
    except Exception as e:
        return f"Ollama unreachable ({e}). Check OLLAMA_API_KEY / OLLAMA_ENDPOINT in .env."
