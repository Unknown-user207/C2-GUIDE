"""context.py — Simple project context (name, phase, notes) persisted to JSON."""

import json
import os


def load_context(context_file):
    if os.path.exists(context_file):
        with open(context_file, "r") as f:
            return json.load(f)
    return {"project": "My Project", "phase": "planning", "notes": ['we are starting from scratch so it might be a lot of work we are building something like Medusa rat or similar variants and l3mon rat but our own is going to be powerful and the admin panel or control panel will be on static web or terminal controls so it is going to be all platform support.', 'only for educational purposes and research']}


def save_context(context_file, context):
    with open(context_file, "w") as f:
        json.dump(context, f, indent=2)
