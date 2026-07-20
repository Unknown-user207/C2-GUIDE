import sqlite3
from datetime import datetime

def init_memory(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  role TEXT,
                  content TEXT)''')
    conn.commit()
    conn.close()

def save_memory(db_path, role, content):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO memories (timestamp, role, content) VALUES (?, ?, ?)",
              (datetime.now().isoformat(), role, content))
    conn.commit()
    conn.close()

def recall_memory(db_path, query, limit=5):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT content FROM memories WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
              (f"%{query}%", limit))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]