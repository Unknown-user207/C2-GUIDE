from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.models import MODELS, ask_model, list_models, summarize_history
from modules.context import load_context, save_context
from modules.memory import (
    init_memory, save_memory, last_session,
    get_context_window, set_summary_state, history_since,
)
from modules import scaffold

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTEXT_FILE = os.path.join(PROJECT_ROOT, "project_context.json")
MEMORY_DB = os.path.join(PROJECT_ROOT, "memory.db")
GENERATED_DIR = os.path.join(PROJECT_ROOT, "generated")

app = Flask(__name__)

scaffold.ensure_layout(PROJECT_ROOT)
init_memory(MEMORY_DB)


@app.route("/")
def index():
    return render_template("index.html", models=list_models())


@app.route("/api/history")
def history():
    """Return the last session's turns so the UI can show where you left off,
    regardless of which model or interface (CLI/web) produced them."""
    turns = last_session(MEMORY_DB, limit=12)
    return jsonify({
        "turns": [
            {"id": row_id, "timestamp": ts, "role": role, "model": model, "content": content}
            for row_id, ts, role, model, content in turns
        ]
    })


@app.route("/api/poll")
def poll():
    """
    Return any turns saved after the given id — used to pick up messages
    typed in the CLI (or another browser tab) while this page is open,
    without re-fetching anything already shown. Cheap indexed query, safe
    to call every few seconds.
    """
    after_id = request.args.get("after_id", 0, type=int)
    rows = history_since(MEMORY_DB, after_id, limit=50)
    return jsonify({
        "turns": [
            {"id": row_id, "timestamp": ts, "role": role, "model": model, "content": content}
            for row_id, ts, role, model, content in rows
        ]
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    model_choice = data.get("model", "4")
    message = data.get("message", "")
    if not message.strip():
        return jsonify({"error": "empty message"}), 400

    context = load_context(CONTEXT_FILE)
    system_prompt = (
        f"You are a helpful project assistant. Project: {context.get('project')}. Phase: {context.get('phase')}. "
        "When the user asks you to create a project, script, or any code they'll want saved as a real file, "
        "output each file as:\nFILE: relative/path/to/file.ext\n```lang\n<full file content>\n```\n"
        "One FILE line + code block per file — you can output several files this way in one response. "
        "Using the same FILE: path again overwrites that file (the previous version is backed up "
        "automatically, nothing is lost). "
        "To remove a file the user no longer wants, output a line: DELETE: relative/path/to/file.ext "
        "(no code block needed) — the old content is backed up before it's deleted. "
        "For quick snippets or examples the user isn't asking to keep, skip the FILE: tag."
    )

    summary, recent, rows_needing_summary, window_start_id = get_context_window(MEMORY_DB, keep_recent_exchanges=8)
    if rows_needing_summary:
        summary = summarize_history(rows_needing_summary, existing_summary=summary)
        set_summary_state(MEMORY_DB, summary, window_start_id)

    full_system_prompt = system_prompt
    if summary:
        full_system_prompt += f"\n\nSummary of earlier conversation (for background context): {summary}"

    response = ask_model(model_choice, message, history=recent, system_prompt=full_system_prompt)

    user_id = save_memory(MEMORY_DB, "user", message, model=MODELS.get(model_choice, {}).get("name"))
    assistant_id = save_memory(MEMORY_DB, "assistant", response, model=MODELS.get(model_choice, {}).get("name"))

    file_ops = scaffold.parse_and_save_files(response, GENERATED_DIR)

    return jsonify({
        "response": response,
        "saved_files": file_ops["saved"],
        "deleted_files": file_ops["deleted"],
        "last_id": max(user_id or 0, assistant_id or 0),
    })


@app.route("/api/files")
def files():
    """List everything currently saved under generated/, for the file browser panel."""
    return jsonify({"files": scaffold.list_generated_files(GENERATED_DIR)})


@app.route("/api/save-file", methods=["POST"])
def save_file():
    """Save a code snippet from the chat as a real file under generated/."""
    data = request.json or {}
    filename = data.get("filename", "").strip()
    content = data.get("content", "")
    if not filename:
        return jsonify({"error": "filename required"}), 400

    # Keep saves confined to the generated/ folder
    safe_rel = os.path.normpath(filename).lstrip(os.sep)
    if safe_rel.startswith(".."):
        return jsonify({"error": "invalid filename"}), 400

    full_path = scaffold.create_path(GENERATED_DIR, safe_rel, content)
    return jsonify({"saved": True, "path": os.path.relpath(full_path, PROJECT_ROOT)})


@app.route("/generated/<path:filename>")
def download_generated(filename):
    return send_from_directory(GENERATED_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
