import json
import os

def load_context(context_file):
    if os.path.exists(context_file):
        with open(context_file, "r") as f:
            return json.load(f)
    return {"project": "ShadowC2", "phase": "Development", "notes": []}

def save_context(context_file, context):
    with open(context_file, "w") as f:
        json.dump(context, f, indent=2)