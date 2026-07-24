# Assistant Capabilities

This file documents what this assistant can do. It lives in `knowledge/` so
the assistant itself can `read capabilities.md` or `search` it when asked
about its own features.

## Core Behavior
- Acts as a project assistant for: {{PROJECT_NAME}}
- Current phase: tracked in `project_context.json`, viewable with the
  `status` command (CLI) or by asking directly
- Personality/tone: plain, direct, no roleplay persona — just a helpful
  assistant

## Models
- Supports OpenAI, Groq, DeepSeek, and Ollama (cloud or local)
- Switch models mid-conversation with the `model` command (CLI) or the
  dropdown (web) — conversation memory carries over regardless of which
  model answers
- If a cloud provider errors or has no API key, it automatically falls
  back to Ollama

## Memory
- Every conversation turn is saved to a local SQLite database
  (`memory.db`), tagged with which model produced it
- On restart, both CLI and web show a "picking up where you left off"
  recap of the last session
- To keep token usage flat over long projects: the last 8 exchanges are
  sent to the model in full; anything older is folded into a short
  rolling summary (condensed via Ollama, so it doesn't cost cloud tokens)
- `recall <term>` (CLI) searches the full conversation history, not just
  the recent window

## Files & Project Structure
- On first run, auto-creates `knowledge/`, `file_history/`, and
  `generated/` if they don't exist
- `create <path>` (CLI) makes a file at any path, auto-creating parent
  folders
- When asked for a project or code to keep, the assistant tags each file
  as:
  ```
  FILE: relative/path/to/file.ext
  ```lang
  <content>
  ```
  ```
  Both CLI and web auto-detect this and save the file under `generated/`
  without needing a manual click. Quick untagged snippets are shown
  in-chat only and not auto-saved.
- Overwriting an existing file keeps a timestamped copy in
  `file_history/` first

## Knowledge Base
- Anything you drop as `.md`/`.txt` in `knowledge/` becomes queryable:
  - `knowledge` — list files
  - `read <file>` — show one
  - `search <term>` — full-text search across all of them

## Web Interface
- Runs locally at `http://127.0.0.1:5000`, no login
- Code blocks in responses get syntax highlighting, a Copy button, and
  (for untagged snippets) a "Save file" button
- A "Generated Files" panel lists everything saved under `generated/`
  with download links, refreshed after each response

## What it does NOT do
- No internet access beyond the configured model APIs — it can't browse
  the web on its own
- No cloud sync — everything (memory, generated files, knowledge) lives
  only on this machine unless you back it up yourself
- Doesn't run or execute the code it generates — it only writes files
