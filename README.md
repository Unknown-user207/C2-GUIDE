# Project Assistant

A personal AI assistant with persistent memory, multi-model support, project
auto-scaffolding, and an optional web chat interface.

## Features
- **Persistent memory** — conversation history is stored in SQLite and survives
  switching between AI providers mid-conversation
- **Multi-model support** — OpenAI, Groq, DeepSeek, or Ollama (cloud or local), with automatic
  fallback to local if a cloud provider is unavailable
- **Auto-scaffolding** — creates the expected project folders on first run, and the
  `create <path>` command / web "Save file" button will create any missing parent
  folders automatically
- **Web interface** — local-only chat UI with syntax-highlighted code blocks, a
  one-click copy button, and a "Save file" button that writes the snippet to
  `generated/` and downloads it

## Quick Start
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in whichever API keys you have
python main.py
```

## Web Interface
```bash
cd web_interface
python app.py
# open http://127.0.0.1:5000
```
Runs locally only (127.0.0.1), no login required.

## CLI Commands
Type `help` inside the assistant for the full list: `model`, `knowledge`, `read`,
`search`, `recall`, `note`, `create`, `status`.

## Notes
Put your own reference material as `.md`/`.txt` files under `knowledge/` — the
assistant can list, read, and search them with the `knowledge`/`read`/`search`
commands.
