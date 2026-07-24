#!/usr/bin/env python3
"""
main.py — Personal AI project assistant (CLI).

Persistent memory across model switches, auto-scaffolded project
folders, and a lightweight knowledge base you can search.
"""

import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from dotenv import load_dotenv

from modules.models import MODELS, ask_model, summarize_history
from modules.memory import (
    init_memory, save_memory, recall_memory, last_session,
    get_context_window, set_summary_state, get_max_id, history_since,
)
from modules.context import load_context, save_context
from modules import scaffold

load_dotenv()
console = Console()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MEMORY_DB = os.path.join(PROJECT_ROOT, os.getenv("MEMORY_DB", "memory.db"))
CONTEXT_FILE = os.path.join(PROJECT_ROOT, os.getenv("CONTEXT_FILE", "project_context.json"))
KNOWLEDGE_DIR = os.path.join(PROJECT_ROOT, "knowledge")
HISTORY_DIR = os.path.join(PROJECT_ROOT, "file_history")
GENERATED_DIR = os.path.join(PROJECT_ROOT, "generated")

HELP_TEXT = """
[bold]Available Commands:[/bold]

  help, ?                 Show this help
  exit, quit               Close the assistant
  model                    Switch the active AI model
  knowledge                List knowledge files
  read <file>               Read a knowledge file
  search <term>             Search knowledge files
  recall <term>             Search past conversation memory
  note <text>               Save a project note
  create <path>             Create a file/folder (auto-scaffolds parents)
  status                    Show project context
"""


def load_knowledge_files():
    knowledge = {}
    if not os.path.exists(KNOWLEDGE_DIR):
        return knowledge
    for filename in os.listdir(KNOWLEDGE_DIR):
        if filename.endswith((".md", ".txt")):
            with open(os.path.join(KNOWLEDGE_DIR, filename), "r", encoding="utf-8") as f:
                knowledge[filename] = f.read()
    return knowledge


def search_knowledge(query):
    results = []
    for filename, content in load_knowledge_files().items():
        if query.lower() in content.lower():
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if query.lower() in line.lower():
                    snippet = "\n".join(lines[max(0, i - 1):i + 2]).strip()
                    results.append({"file": filename, "snippet": snippet})
                    break
    return results


def show_resume_recap():
    """On startup, show the tail of the last session so you know where you left off,
    regardless of which model(s) were used to produce it."""
    turns = last_session(MEMORY_DB, limit=6)
    if not turns:
        return  # first run ever, nothing to resume

    lines = []
    for _id, ts, role, model, content in turns:
        label = "You" if role == "user" else f"Assistant ({model or 'unknown model'})"
        preview = content if len(content) <= 200 else content[:200] + "…"
        lines.append(f"[dim]{ts.split('T')[0]}[/dim] [bold]{label}:[/bold] {preview}")

    console.print(Panel("\n\n".join(lines), title="Picking up where you left off", style="green"))
    console.print()


def show_external_updates(last_seen_id):
    """
    Check for turns saved by another running interface (e.g. the web
    UI) since we last looked, and print them. Returns the updated
    cursor. Called at the top of each loop iteration — cheap enough
    (one indexed SQLite query) to not slow down typing, and never
    touches anything mid-send, since it only runs between turns.
    """
    new_rows = history_since(MEMORY_DB, last_seen_id, limit=50)
    if not new_rows:
        return last_seen_id

    lines = []
    for row_id, ts, role, model, content in new_rows:
        label = "You (web)" if role == "user" else f"Assistant ({model or 'unknown'}, via web)"
        preview = content if len(content) <= 300 else content[:300] + "…"
        lines.append(f"[bold]{label}:[/bold] {preview}")
        last_seen_id = row_id

    console.print(Panel("\n\n".join(lines), title="New activity from the web interface", style="blue"))
    return last_seen_id


def choose_model():
    console.print("[bold]Select a model:[/bold]")
    for k, v in MODELS.items():
        status = "✅" if v["api_key"] else "⚠️ (will fall back to Ollama)"
        console.print(f"  {k}. {v['name']} {status}")
    return Prompt.ask("[bold]Choice[/bold]", choices=list(MODELS.keys()), default="4")


def main():
    scaffold.ensure_layout(PROJECT_ROOT)
    init_memory(MEMORY_DB)

    console.print(Panel.fit("Shadow Guide", style="bold cyan"))
    console.print("[dim]Persistent memory, project-aware, multi-model.[/dim]\n")

    context = load_context(CONTEXT_FILE)
    if not os.path.exists(CONTEXT_FILE):
        save_context(CONTEXT_FILE, context)

    show_resume_recap()
    last_seen_id = get_max_id(MEMORY_DB)

    choice = choose_model()
    console.print(f"[dim]Using: {MODELS[choice]['name']} ({MODELS[choice]['model']})[/dim]\n")
    console.print("[dim]Type 'help' for commands, 'exit' to quit.[/dim]\n")

    system_prompt = (
        f"You are Shadow Guide, a wise assistant for the ShadowC2 project. Project: {context.get('project')}. Phase: {context.get('phase')}. "
        "When the user asks you to create a project, script, or any code they'll want saved as a real file, "
        "output each file as:\nFILE: relative/path/to/file.ext\n```lang\n<full file content>\n```\n"
        "One FILE line + code block per file — you can output several files this way in one response. "
        "Using the same FILE: path again overwrites that file (the previous version is backed up "
        "automatically, nothing is lost). "
        "To remove a file the user no longer wants, output a line: DELETE: relative/path/to/file.ext "
        "(no code block needed) — the old content is backed up before it's deleted. "
        "For quick snippets or examples the user isn't asking to keep, skip the FILE: tag."
    )

    while True:
        last_seen_id = show_external_updates(last_seen_id)

        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye.[/yellow]")
            break

        if not user_input.strip():
            continue

        cmd = user_input.strip()
        low = cmd.lower()

        if low in ("exit", "quit"):
            console.print("[yellow]Goodbye.[/yellow]")
            break

        if low in ("help", "?"):
            console.print(Panel(HELP_TEXT, title="Help", style="yellow"))
            continue

        if low == "model":
            choice = choose_model()
            console.print(f"[dim]Switched to: {MODELS[choice]['name']}[/dim]")
            continue

        if low == "knowledge":
            files = list(load_knowledge_files().keys())
            console.print(Panel("\n".join(files) if files else "No knowledge files yet.", title="Knowledge Files"))
            continue

        if low.startswith("read "):
            filename = cmd[5:].strip()
            knowledge = load_knowledge_files()
            if filename in knowledge:
                console.print(Panel(Markdown(knowledge[filename]), title=filename))
            else:
                console.print(f"[red]File '{filename}' not found.[/red]")
            continue

        if low.startswith("search "):
            query = cmd[7:].strip()
            results = search_knowledge(query)
            if results:
                for r in results:
                    console.print(f"[bold]{r['file']}[/bold]\n{r['snippet']}\n")
            else:
                console.print(f"[yellow]No results for '{query}'.[/yellow]")
            continue

        if low.startswith("recall "):
            query = cmd[7:].strip()
            memories = recall_memory(MEMORY_DB, query)
            if memories:
                for ts, role, content in memories:
                    console.print(f"[dim]{ts}[/dim] [bold]{role}:[/bold] {content}")
            else:
                console.print("[yellow]No memories found.[/yellow]")
            continue

        if low.startswith("note "):
            note = cmd[5:].strip()
            context.setdefault("notes", []).append(note)
            save_context(CONTEXT_FILE, context)
            note_id = save_memory(MEMORY_DB, "user", f"[note] {note}")
            last_seen_id = max(last_seen_id, note_id or 0)
            console.print("[green]Note saved.[/green]")
            continue

        if low.startswith("create "):
            rel_path = cmd[7:].strip()
            full = scaffold.create_path(PROJECT_ROOT, rel_path)
            console.print(f"[green]Created:[/green] {full}")
            continue

        if low == "status":
            console.print(Panel(json.dumps(context, indent=2), title="Project Context"))
            continue

        # Normal chat turn — use a rolling summary for anything beyond the
        # last 8 exchanges, so token usage stays flat as the project grows,
        # regardless of which model produced the older turns.
        summary, recent, rows_needing_summary, window_start_id = get_context_window(MEMORY_DB, keep_recent_exchanges=8)

        if rows_needing_summary:
            summary = summarize_history(rows_needing_summary, existing_summary=summary)
            set_summary_state(MEMORY_DB, summary, window_start_id)

        full_system_prompt = system_prompt
        if summary:
            full_system_prompt += f"\n\nSummary of earlier conversation (for background context): {summary}"

        response = ask_model(choice, user_input, history=recent, system_prompt=full_system_prompt)

        user_id = save_memory(MEMORY_DB, "user", user_input, model=MODELS[choice]["name"])
        assistant_id = save_memory(MEMORY_DB, "assistant", response, model=MODELS[choice]["name"])
        last_seen_id = max(last_seen_id, user_id or 0, assistant_id or 0)

        console.print(Panel(Markdown(response), title=MODELS[choice]["name"], style="magenta"))

        saved_files = scaffold.parse_and_save_files(response, GENERATED_DIR)
        if saved_files["saved"]:
            listing = "\n".join(f"• generated/{p}" for p in saved_files["saved"])
            console.print(Panel(listing, title="Files saved", style="green"))
        if saved_files["deleted"]:
            listing = "\n".join(f"• generated/{p}" for p in saved_files["deleted"])
            console.print(Panel(listing, title="Files deleted (backed up first)", style="red"))


if __name__ == "__main__":
    main()
