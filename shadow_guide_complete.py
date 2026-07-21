#!/usr/bin/env python3
"""
shadow_guide_complete.py — The Silent Inheritance
"""

import os
import json
import sqlite3
import requests
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

load_dotenv()
console = Console()

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MEMORY_DB = os.path.join(PROJECT_ROOT, os.getenv("MEMORY_DB", "guide_memory.db"))
CONTEXT_FILE = os.path.join(PROJECT_ROOT, os.getenv("CONTEXT_FILE", "project_context.json"))
KNOWLEDGE_DIR = os.path.join(PROJECT_ROOT, "knowledge")
C2_KNOWLEDGE_FILE = os.path.join(PROJECT_ROOT, os.getenv("C2_KNOWLEDGE_FILE", "c2_knowledge.json"))

os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

# ==========================================
# AI MODEL ROUTER - FIXED
# ==========================================
MODELS = {
    "1": {
        "name": "Ollama Cloud",
        "api_key": os.getenv("OLLAMA_API_KEY"),
        "endpoint": "https://ollama.com/api/chat",  # Fixed endpoint
        "model": os.getenv("OLLAMA_MODEL", "gemma4"),
        "requires_key": True,
        "format": "ollama"
    },
    "2": {
        "name": "Groq",
        "api_key": os.getenv("GROQ_API_KEY"),
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
        "model": os.getenv("GROQ_MODEL", "Qwen 3.6 27B"),  # Updated model
        "requires_key": True,
        "format": "openai"
    },
    "3": {
        "name": "DeepSeek",
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "endpoint": "https://api.deepseek.com/v1/chat/completions",
        "model": "DeepSeek-V4-Flash",
        "requires_key": True,
        "format": "openai"
    },
    "4": {
        "name": "OpenAI",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-3.5-turbo",
        "requires_key": True,
        "format": "openai"
    }
}

def ask_model(choice, message, context):
    """Send a query to the selected AI model."""
    model = MODELS.get(choice)
    if not model:
        return "⚠️ Invalid model choice."
    
    if not model["api_key"]:
        return f"❌ No API key for {model['name']}. Check your .env file."
    
    # Build the payload based on format
    if model["format"] == "ollama":
        payload = {
            "model": model["model"],
            "messages": [
                {"role": "system", "content": f"You are Shadow Guide, a wise assistant for the ShadowC2 project."},
                {"role": "user", "content": message}
            ],
            "stream": False
        }
        # Ollama uses different headers
        headers = {
            "Authorization": f"Bearer {model['api_key']}",
            "Content-Type": "application/json"
        }
    else:  # OpenAI format
        payload = {
            "model": model["model"],
            "messages": [
                {"role": "system", "content": f"You are Shadow Guide, a wise assistant for the ShadowC2 project. Phase: {context.get('phase', 'Development')}"},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        headers = {
            "Authorization": f"Bearer {model['api_key']}",
            "Content-Type": "application/json"
        }
    
    try:
        console.print("[dim]⏳ Consulting the shadows...[/dim]")
        resp = requests.post(model["endpoint"], headers=headers, json=payload, timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            
            # Handle Ollama format
            if model["format"] == "ollama":
                if "message" in data:
                    return data["message"]["content"]
                elif "response" in data:
                    return data["response"]
                else:
                    return f"⚠️ Unexpected response: {json.dumps(data, indent=2)[:200]}"
            
            # Handle OpenAI format
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return f"⚠️ Unexpected response: {json.dumps(data, indent=2)[:200]}"
        else:
            error_msg = f"API error {resp.status_code}"
            try:
                error_data = resp.json()
                if "error" in error_data:
                    if isinstance(error_data["error"], dict):
                        error_msg += f": {error_data['error'].get('message', error_data['error'])}"
                    else:
                        error_msg += f": {error_data['error']}"
                elif "message" in error_data:
                    error_msg += f": {error_data['message']}"
            except:
                error_msg += f": {resp.text[:200]}"
            
            console.print(f"[red]⚠️ {error_msg}[/red]")
            return f"⚠️ Error: {error_msg}"
            
    except requests.exceptions.Timeout:
        return "⏰ API timeout. Please try again."
    except requests.exceptions.ConnectionError:
        return "🌐 Connection error. Check your internet."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==========================================
# MEMORY LAYER
# ==========================================
def init_memory():
    conn = sqlite3.connect(MEMORY_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  role TEXT,
                  content TEXT)''')
    conn.commit()
    conn.close()

def save_memory(role, content):
    conn = sqlite3.connect(MEMORY_DB)
    c = conn.cursor()
    c.execute("INSERT INTO memories (timestamp, role, content) VALUES (?, ?, ?)",
              (datetime.now().isoformat(), role, content))
    conn.commit()
    conn.close()

def recall_memory(query, limit=5):
    conn = sqlite3.connect(MEMORY_DB)
    c = conn.cursor()
    c.execute("SELECT content FROM memories WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
              (f"%{query}%", limit))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# ==========================================
# KNOWLEDGE FUNCTIONS
# ==========================================
def load_knowledge_files():
    knowledge = {}
    if not os.path.exists(KNOWLEDGE_DIR):
        return knowledge
    
    for filename in os.listdir(KNOWLEDGE_DIR):
        if filename.endswith((".md", ".txt")):
            filepath = os.path.join(KNOWLEDGE_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    knowledge[filename] = f.read()
            except Exception as e:
                knowledge[filename] = f"⚠️ Error: {e}"
    return knowledge

def search_knowledge(query):
    results = []
    for filename, content in load_knowledge_files().items():
        if query.lower() in content.lower():
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if query.lower() in line.lower():
                    snippet = line.strip()
                    start = max(0, i-1)
                    end = min(len(lines), i+2)
                    context_lines = lines[start:end]
                    results.append({
                        "file": filename,
                        "snippet": "\n".join(context_lines).strip()
                    })
                    break
    return results

def get_project_structure():
    structure = {}
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if "__pycache__" in root or ".git" in root or "file_history" in root:
            continue
        rel_path = os.path.relpath(root, PROJECT_ROOT)
        if rel_path == ".":
            rel_path = "root"
        structure[rel_path] = files[:15]
    return structure

def load_c2_knowledge():
    if os.path.exists(C2_KNOWLEDGE_FILE):
        with open(C2_KNOWLEDGE_FILE, "r") as f:
            return json.load(f)
    return {}

def get_roadmap():
    knowledge = load_c2_knowledge()
    return knowledge.get("roadmap", [])

def get_project_status():
    knowledge = load_c2_knowledge()
    return knowledge.get("status", {})

# ==========================================
# MAIN LOOP
# ==========================================
def main():
    init_memory()
    console.print(Panel.fit("🧙‍♂️ Shadow Guide — Silent Inheritance", style="bold cyan"))
    console.print("[dim]I remember. I see your files. I carry the master's scroll.[/dim]\n")
    
    # Load context
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r") as f:
            context = json.load(f)
    else:
        context = {"project": "ShadowC2", "phase": "Development", "notes": []}
        with open(CONTEXT_FILE, "w") as f:
            json.dump(context, f, indent=2)
    
    # Model selection
    console.print("[bold]Select a guide persona:[/bold]")
    for k, v in MODELS.items():
        status = "✅" if v["api_key"] else "❌"
        console.print(f"  {k}. {v['name']} {status}")
    
    choice = Prompt.ask("[bold]Choice[/bold]", choices=list(MODELS.keys()))
    console.print(f"[dim]Using: {MODELS[choice]['name']} ({MODELS[choice]['model']})[/dim]\n")
    
    console.print("[dim]Type 'help' for commands, 'exit' to quit.[/dim]\n")
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
        except KeyboardInterrupt:
            console.print("\n[red]🕯️ Guide falls silent. Inheritance complete.[/red]")
            break
        
        if not user_input.strip():
            continue
        
        # ----- EXIT -----
        if user_input.lower() in ["exit", "quit"]:
            console.print("[red]🕯️ Guide falls silent. Inheritance complete.[/red]")
            break
        
        # ----- HELP -----
        if user_input.lower() in ["help", "?"]:
            console.print(Panel("""
[bold]Available Commands:[/bold]

  help, ?         Show this help
  exit, quit      Close the guide
  knowledge       List knowledge files
  read <file>     Read a knowledge file
  search <term>   Search knowledge files
  files           Show project structure
  recall <term>   Search memory
  note <text>     Save a note
  master          Read the master's scroll
  roadmap         Show project roadmap
  status          Show project status
""", title="📖 Help", style="yellow"))
            continue
        
        # ----- MASTER SCROLL -----
        if user_input.lower() == "master":
            master_scroll = os.path.join(KNOWLEDGE_DIR, "master_void_scroll.md")
            if os.path.exists(master_scroll):
                with open(master_scroll, "r", encoding="utf-8") as f:
                    console.print(Panel(Markdown(f.read()), title="🧙‍♂️ Master's Scroll", style="bold magenta"))
            else:
                console.print("[yellow]Master's scroll not found. Create it in knowledge/[/yellow]")
            continue
        
        # ----- FILES -----
        if user_input.lower() == "files":
            console.print(Panel(json.dumps(get_project_structure(), indent=2), title="📁 Project Files", style="blue"))
            continue
        
        # ----- KNOWLEDGE -----
        if user_input.lower() == "knowledge":
            files = list(load_knowledge_files().keys())
            if files:
                console.print(Panel("\n".join(files), title="📚 Knowledge Files", style="cyan"))
            else:
                console.print("[yellow]No knowledge files found. Add .md files to knowledge/[/yellow]")
            continue
        
        # ----- READ -----
        if user_input.lower().startswith("read "):
            filename = user_input[5:].strip()
            knowledge = load_knowledge_files()
            if filename in knowledge:
                console.print(Panel(Markdown(knowledge[filename]), title=f"📄 {filename}", style="magenta"))
            else:
                console.print(f"[red]File '{filename}' not found.[/red]")
            continue
        
        # ----- SEARCH -----
        if user_input.lower().startswith("search "):
            query = user_input[7:].strip()
            results = search_knowledge(query)
            if results:
                console.print(Panel(f"Found {len(results)} result(s):", title=f"🔍 Search: '{query}'", style="green"))
                for r in results:
                    console.print(f"[bold]{r['file']}[/bold]\n{r['snippet']}\n")
            else:
                console.print(f"[yellow]No results for '{query}'.[/yellow]")
            continue
        
        # ----- RECALL -----
        if user_input.lower().startswith("recall "):
            query = user_input[7:].strip()
            memories = recall_memory(query)
            if memories:
                console.print(Panel("\n".join(memories), title="🧠 Memories", style="magenta"))
            else:
                console.print("[yellow]No memories found.[/yellow]")
            continue
        
        # ----- NOTE -----
        if user_input.lower().startswith("note "):
            note = user_input[5:].strip()
            context["notes"].append(note)
            with open(CONTEXT_FILE, "w") as f:
                json.dump(context, f, indent=2)
            save_memory("note", note)
            console.print("[green]✅ Note saved.[/green]")
            continue
        
        # ----- ROADMAP -----
        if user_input.lower() == "roadmap":
            roadmap = get_roadmap()
            if roadmap:
                console.print(Panel("\n".join([f"• {item}" for item in roadmap]), title="🗺️ Roadmap", style="green"))
            else:
                console.print("[yellow]No roadmap found. Add c2_knowledge.json[/yellow]")
            continue
        
        # ----- STATUS -----
        if user_input.lower() == "status":
            status = get_project_status()
            if status:
                console.print(Panel(json.dumps(status, indent=2), title="📊 Project Status", style="cyan"))
            else:
                console.print("[yellow]No status data found. Add c2_knowledge.json[/yellow]")
            continue
        
        # ----- ASK THE GUIDE -----
        response = ask_model(choice, user_input, context)
        
        save_memory("user", user_input)
        save_memory("guide", response)
        
        console.print(Panel(Markdown(response), title="🧙‍♂️ Guide", style="magenta"))

if __name__ == "__main__":
    main()