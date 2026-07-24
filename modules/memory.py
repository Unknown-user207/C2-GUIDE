"""
memory.py — Persistent conversation memory.

All turns are stored in one SQLite database regardless of which
model answered them, so switching providers mid-conversation
(e.g. OpenAI -> Ollama) still recalls the full history.
"""

import sqlite3
from datetime import datetime


def _connect(db_path):
    """
    Shared connection helper: WAL mode lets one process write while
    another reads without locking errors, and busy_timeout makes any
    brief write/write contention wait instead of raising
    'database is locked' — needed since the CLI and web app can both
    have the same memory.db open at once.
    """
    conn = sqlite3.connect(db_path, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=10000")
    return conn


def init_memory(db_path):
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  role TEXT,
                  model TEXT,
                  content TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS summary_state
                 (id INTEGER PRIMARY KEY CHECK (id = 1),
                  summary TEXT,
                  summarized_up_to_id INTEGER)''')
    c.execute("INSERT OR IGNORE INTO summary_state (id, summary, summarized_up_to_id) VALUES (1, '', 0)")
    conn.commit()
    conn.close()


def save_memory(db_path, role, content, model=None):
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute(
        "INSERT INTO memories (timestamp, role, model, content) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), role, model or "", content),
    )
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def recent_history(db_path, limit=20):
    """Return the last N turns as (role, content) tuples, oldest first.

    Role is normalized to 'user' or 'assistant' so it can be fed
    straight into any provider's chat message format, no matter
    which model actually produced a given assistant turn.
    """
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute("SELECT role, content FROM memories ORDER BY id DESC LIMIT ?", (limit,))
    rows = list(reversed(c.fetchall()))
    conn.close()
    normalized = []
    for role, content in rows:
        norm_role = "user" if role == "user" else "assistant"
        normalized.append((norm_role, content))
    return normalized


def get_summary_state(db_path):
    """Return (summary_text, summarized_up_to_id)."""
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute("SELECT summary, summarized_up_to_id FROM summary_state WHERE id = 1")
    row = c.fetchone()
    conn.close()
    return row if row else ("", 0)


def set_summary_state(db_path, summary, summarized_up_to_id):
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute(
        "UPDATE summary_state SET summary = ?, summarized_up_to_id = ? WHERE id = 1",
        (summary, summarized_up_to_id),
    )
    conn.commit()
    conn.close()


def rows_to_fold(db_path, after_id, up_to_id):
    """Rows older than the recent window that haven't been folded into the summary yet."""
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute(
        "SELECT id, role, content FROM memories WHERE id > ? AND id <= ? ORDER BY id ASC",
        (after_id, up_to_id),
    )
    rows = c.fetchall()
    conn.close()
    return rows


def get_context_window(db_path, keep_recent_exchanges=8):
    """
    Returns (summary_text, recent_history, rows_needing_summary, window_start_id):
    - summary_text: existing rolling summary of everything older than the window
    - recent_history: (role, content) tuples for the last N exchanges, full text
    - rows_needing_summary: raw rows just outside the window not yet folded in
    - window_start_id: id boundary — call set_summary_state(db, new_summary, window_start_id)
      after folding rows_needing_summary into the summary
    """
    keep_rows = keep_recent_exchanges * 2  # user + assistant per exchange
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute("SELECT MAX(id) FROM memories")
    max_id = c.fetchone()[0] or 0
    conn.close()

    summary, summarized_up_to_id = get_summary_state(db_path)
    window_start_id = max(0, max_id - keep_rows)

    recent = recent_history(db_path, limit=keep_rows)

    rows_needing_summary = []
    if window_start_id > summarized_up_to_id:
        rows_needing_summary = rows_to_fold(db_path, summarized_up_to_id, window_start_id)

    return summary, recent, rows_needing_summary, window_start_id


def get_max_id(db_path):
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute("SELECT MAX(id) FROM memories")
    max_id = c.fetchone()[0] or 0
    conn.close()
    return max_id


def history_since(db_path, after_id, limit=50):
    """
    Return turns with id > after_id, oldest first, as
    (id, timestamp, role, model, content) tuples.

    Used by both the CLI and web interface to notice turns written by
    the *other* one — e.g. the web app polls this to pick up a message
    typed in the terminal, and vice versa — without re-fetching or
    re-displaying anything already seen.
    """
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute(
        "SELECT id, timestamp, role, model, content FROM memories WHERE id > ? ORDER BY id ASC LIMIT ?",
        (after_id, limit),
    )
    rows = c.fetchall()
    conn.close()
    return rows


def last_session(db_path, limit=6):
    """Return the last N raw turns (id, timestamp, role, model, content), oldest first.

    Unlike recent_history(), this keeps the original model tag, role
    label, and row id so it can be displayed to the person as a
    human-readable recap of exactly where they left off, no matter
    which model or interface (CLI/web) produced it — and so the id can
    seed a sync cursor for polling.
    """
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, timestamp, role, model, content FROM memories ORDER BY id DESC LIMIT ?", (limit,))
    rows = list(reversed(c.fetchall()))
    conn.close()
    return rows


def recall_memory(db_path, query, limit=5):
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute(
        "SELECT timestamp, role, content FROM memories WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
        (f"%{query}%", limit),
    )
    rows = c.fetchall()
    conn.close()
    return rows
