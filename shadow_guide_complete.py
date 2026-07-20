#!/usr/bin/env python3
"""
shadow_guide_complete.py — The Silent Inheritance
A mute, server-ready companion with memory, project awareness, and offline fallback.
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

# Load environment variables first
load_dotenv()
console = Console()

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MEMORY_DB = os.path.join(PROJECT_ROOT, os.getenv("MEMORY_DB", "guide_memory.db"))
CONTEXT_FILE = os.path.join(PROJECT_ROOT, os.getenv("CONTEXT_FILE", "project_context.json"))
KNOWLEDGE_DIR = os.path.join(PROJECT_ROOT, "knowledge")
C2_KNOWLEDGE_FILE = os.path.join(PROJECT_ROOT, "c2_knowledge.json")
FILE_HISTORY_DIR = os.path.join(PROJECT_ROOT, "file_history")

# Create required directories
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
os.makedirs(FILE_HISTORY_DIR, exist_ok=True)

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
# PROJECT AWARENESS
# ==========================================
def get_project_structure():
    structure = {}
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if "file_history" in root or "__pycache__" in root or ".git" in root:
            continue
        rel_path = os.path.relpath(root, PROJECT_ROOT)
        structure[rel_path] = files[:10]
    return structure

# ==========================================
# KNOWLEDGE FOLDER — Manual & Auto-Loaded
# ==========================================
def load_knowledge_files():
    """Load all .md and .txt files from the knowledge folder."""
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
                knowledge[filename] = f"⚠️ Error reading file: {e}"
    return knowledge

def search_knowledge(query):
    """Search all knowledge files for a keyword."""
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

# ==========================================
# C2 PROJECT KNOWLEDGE
# ==========================================
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
# AI MODEL ROUTER
# ==========================================
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
            {"role": "system", "content": f"You are Shadow Guide. Project: {context['project']}. Phase: {context['phase']}. Help with code, architecture, and life."},
            {"role": "user", "content": message}
        ]
    }
    headers = {"Authorization": f"Bearer {model['api_key']}", "Content-Type": "application/json"}
    try:
        resp = requests.post(model["endpoint"], headers=headers, json=payload, timeout=30)
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        console.print(f"[red]⚠️ API error: {e}. Falling back to local...[/red]")
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
        return "🌑 I'm offline, but I'm still with you. Try again when the internet returns."

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
    
    # Model selection
    console.print("[bold]Select a guide persona:[/bold]")
    for k, v in MODELS.items():
        status = "✅" if v["api_key"] else "🌐" if k == "4" else "❌"
        console.print(f"  {k}. {v['name']} {status}")
    choice = Prompt.ask("[bold]Choice[/bold]", choices=list(MODELS.keys()))
    
    console.print("[dim]Type 'help' for commands, 'exit' to quit.[/dim]\n")
    
    while True:
        user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
        
        # ----- EXIT -----
        if user_input.lower() in ["exit", "quit"]:
            console.print("[red]🕯️ Guide falls silent. Inheritance complete.[/red]")
            break
        
        # ----- HELP -----
        if user_input.lower() in ["help", "?"]:
            console.print(Panel("""
[bold]Available Commands:[/bold]

[cyan]General[/cyan]
  help, ?         Show this help
  exit, quit      Close the guide

[cyan]Knowledge[/cyan]
  knowledge       List all files in the knowledge folder
  read <file>     Read a specific knowledge file
  search <term>   Search all knowledge files for a term
  addnote <text>  Add a note to manual_notes.md

[cyan]Project[/cyan]
  roadmap         Show the ShadowC2 roadmap
  status          Show project status
  files           Show project file structure

[cyan]Memory[/cyan]
  recall <term>   Search memory for past conversations
  note <text>     Save a note to project context

[cyan]Master[/cyan]
  master, void    Read the master's scroll
  who are you     Same as master
""", title="📖 Help", style="yellow"))
            continue
        
        # ----- MASTER SCROLL -----
        if user_input.lower() in ["master", "void", "who are you"]:
            master_scroll = os.path.join(KNOWLEDGE_DIR, "master_void_scroll.md")
            if os.path.exists(master_scroll):
                with open(master_scroll, "r", encoding="utf-8") as f:
                    content = f.read()
                console.print(Panel(Markdown(content), title="🧙‍♂️ The Master's Scroll", style="bold magenta"))
            else:
                console.print("[yellow]The master's scroll is not yet written.[/yellow]")
            continue
        
        # ----- FILES -----
        if user_input.lower() == "files":
            console.print(Panel(json.dumps(get_project_structure(), indent=2), title="📁 Project Files", style="blue"))
            continue
        
        # ----- KNOWLEDGE LIST -----
        if user_input.lower() == "knowledge":
            files = list(load_knowledge_files().keys())
            if files:
                console.print(Panel("\n".join(files), title="📚 Knowledge Files", style="cyan"))
            else:
                console.print("[yellow]No knowledge files found. Add .md or .txt files to the knowledge/ folder.[/yellow]")
            continue
        
        # ----- READ KNOWLEDGE FILE -----
        if user_input.lower().startswith("read "):
            filename = user_input[5:].strip()
            knowledge = load_knowledge_files()
            if filename in knowledge:
                console.print(Panel(Markdown(knowledge[filename]), title=f"📄 {filename}", style="magenta"))
            else:
                matches = [f for f in knowledge.keys() if filename.lower() in f.lower()]
                if matches:
                    console.print(f"[yellow]Did you mean one of these?[/yellow]")
                    for m in matches:
                        console.print(f"  - {m}")
                else:
                    console.print(f"[red]File '{filename}' not found in knowledge/.[/red]")
            continue
        
        # ----- SEARCH KNOWLEDGE -----
        if user_input.lower().startswith("search "):
            query = user_input[7:].strip()
            if not query:
                console.print("[yellow]Please provide a search term.[/yellow]")
                continue
            results = search_knowledge(query)
            if results:
                console.print(Panel(f"Found {len(results)} result(s):", title=f"🔍 Search: '{query}'", style="green"))
                for r in results:
                    console.print(f"[bold]{r['file']}[/bold]\n{r['snippet']}\n")
            else:
                console.print(f"[yellow]No results found for '{query}'.[/yellow]")
            continue
        
        # ----- ADD NOTE TO KNOWLEDGE -----
        if user_input.lower().startswith("addnote "):
            note = user_input[8:].strip()
            if not note:
                console.print("[yellow]Please provide a note.[/yellow]")
                continue
            filename = "manual_notes.md"
            filepath = os.path.join(KNOWLEDGE_DIR, filename)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(f"\n## {timestamp}\n{note}\n")
            console.print(f"[green]✅ Note added to {filename}[/green]")
            continue
        
        # ----- ROADMAP -----
        if user_input.lower() == "roadmap":
            roadmap = get_roadmap()
            if roadmap:
                console.print(Panel(json.dumps(roadmap, indent=2), title="🗺️ ShadowC2 Roadmap", style="green"))
            else:
                console.print("[yellow]No roadmap found. Add c2_knowledge.json to the root folder.[/yellow]")
            continue
        
        # ----- STATUS -----
        if user_input.lower() == "status":
            status = get_project_status()
            if status:
                console.print(Panel(json.dumps(status, indent=2), title="📊 Project Status", style="cyan"))
            else:
                console.print("[yellow]No status data found. Add c2_knowledge.json to the root folder.[/yellow]")
            continue
        
        # ----- RECALL MEMORY -----
        if user_input.lower().startswith("recall "):
            query = user_input[7:].strip()
            if not query:
                console.print("[yellow]Please provide a search term.[/yellow]")
                continue
            memories = recall_memory(query)
            if memories:
                console.print(Panel("\n".join(memories), title="🧠 Memories", style="magenta"))
            else:
                console.print("[yellow]No memories found.[/yellow]")
            continue
        
        # ----- SAVE NOTE TO CONTEXT -----
        if user_input.lower().startswith("note "):
            note = user_input[5:].strip()
            if not note:
                console.print("[yellow]Please provide a note.[/yellow]")
                continue
            context["notes"].append(note)
            with open(CONTEXT_FILE, "w") as f:
                json.dump(context, f, indent=2)
            save_memory("note", note)
            console.print("[green]✅ Note saved to project context.[/green]")
            continue
        
        # ----- FALLBACK: ASK THE GUIDE -----
        console.print("[dim]⏳ Consulting the shadows...[/dim]")
        response = ask_model(choice, user_input, context)
        
        # Save to memory
        save_memory("user", user_input)
        save_memory("guide", response)
        
        # Display
        console.print(Panel(Markdown(response), title="🧙‍♂️ Guide", style="magenta"))
        
        # Update context if phase changed
        if "phase" in response.lower() and "change" in response.lower():
            new_phase = Prompt.ask("📌 Update project phase? (leave blank to skip)")
            if new_phase:
                context["phase"] = new_phase
                with open(CONTEXT_FILE, "w") as f:
                    json.dump(context, f, indent=2)
                console.print(f"[green]✅ Phase updated: {new_phase}[/green]")

if __name__ == "__main__":
    main()