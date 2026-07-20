#!/usr/bin/env python3
import os
import json
import re
import readline
from datetime import datetime
from dotenv import load_dotenv
import requests
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

load_dotenv()
console = Console()

# Config
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
FILE_HISTORY_DIR = os.path.join(PROJECT_ROOT, "file_history")
os.makedirs(FILE_HISTORY_DIR, exist_ok=True)

LOG_FILE = "shadow_journal.md"
CONTEXT_FILE = "project_context.json"

MODELS = {
    "1": {"name": "OpenAI", "api_key": os.getenv("OPENAI_API_KEY"), "endpoint": "https://api.openai.com/v1/chat/completions"},
    "2": {"name": "Grok", "api_key": os.getenv("GROK_API_KEY"), "endpoint": "https://api.grok.x.ai/v1/chat/completions"},
    "3": {"name": "DeepSeek", "api_key": os.getenv("DEEPSEEK_API_KEY"), "endpoint": os.getenv("DEEPSEEK_ENDPOINT", "https://api.deepseek.com/v1/chat/completions")},
}

def load_context():
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r") as f:
            return json.load(f)
    return {"project": "ShadowC2", "phase": "Development", "notes": [], "decisions": []}

def save_context(context):
    with open(CONTEXT_FILE, "w") as f:
        json.dump(context, f, indent=2)

def log_to_journal(entry):
    with open(LOG_FILE, "a") as f:
        f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{entry}\n")

def save_version(filename, content):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    version_file = os.path.join(FILE_HISTORY_DIR, f"{timestamp}_{safe_name}")
    with open(version_file, "w") as f:
        f.write(content)
    return version_file

def handle_file_command(user_input):
    parts = user_input.split(" ", 2)
    if len(parts) < 3:
        return None
    cmd, filename, content = parts[0].lower(), parts[1], parts[2]
    if cmd in ["create", "save", "write"]:
        full_path = os.path.join(PROJECT_ROOT, filename)
        if os.path.exists(full_path):
            with open(full_path, "r") as f:
                save_version(filename, f.read())
        with open(full_path, "w") as f:
            f.write(content)
        log_to_journal(f"**File {cmd}ed:** `{filename}`")
        return f"✅ File `{filename}` {cmd}ed successfully."
    return None

def ask_model(choice, message, context):
    model = MODELS[choice]
    if not model["api_key"]:
        return "❌ API key missing."
    payload = {
        "model": "gpt-4" if choice == "1" else "grok-1" if choice == "2" else "deepseek-chat",
        "messages": [
            {"role": "system", "content": f"You are Shadow Guide, mentor for {context['project']}. Phase: {context['phase']}."},
            {"role": "user", "content": message}
        ]
    }
    headers = {"Authorization": f"Bearer {model['api_key']}", "Content-Type": "application/json"}
    try:
        resp = requests.post(model["endpoint"], headers=headers, json=payload, timeout=30)
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error: {e}"

def main():
    console.print(Panel.fit("🧙‍♂️ Shadow Guide — AI Dev Mentor", style="bold cyan"))
    context = load_context()
    console.print(f"[green]📁 {context['project']} — Phase: {context['phase']}[/green]\n")

    console.print("[bold]Select model:[/bold]")
    for k, v in MODELS.items():
        console.print(f"  {k}. {v['name']} {'✅' if v['api_key'] else '❌'}")
    choice = Prompt.ask("[bold]Choice[/bold]", choices=list(MODELS.keys()))

    while True:
        user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
        if user_input.lower() in ["exit", "quit"]:
            break
        if user_input.lower().startswith("create ") or user_input.lower().startswith("save "):
            result = handle_file_command(user_input)
            console.print(f"[green]{result}[/green]" if "✅" in result else f"[red]{result}[/red]")
            continue
        console.print("[dim]Thinking...[/dim]")
        response = ask_model(choice, user_input, context)
        console.print(Panel(Markdown(response), title="🧙‍♂️ Guide", style="magenta"))
        log_to_journal(f"**Q:** {user_input}\n\n**A:** {response}")

if __name__ == "__main__":
    main()