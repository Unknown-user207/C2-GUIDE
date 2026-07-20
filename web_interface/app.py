from flask import Flask, render_template, request, jsonify
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.models import ask_model
from modules.context import load_context, save_context
from modules.memory import save_memory, recall_memory

app = Flask(__name__)
CONTEXT_FILE = os.path.join(os.path.dirname(__file__), "..", "project_context.json")
MEMORY_DB = os.path.join(os.path.dirname(__file__), "..", "guide_memory.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    model_choice = data.get("model", "1")
    message = data.get("message", "")
    context = load_context(CONTEXT_FILE)
    
    response = ask_model(model_choice, message, context)
    save_memory(MEMORY_DB, "user", message)
    save_memory(MEMORY_DB, "guide", response)
    
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)