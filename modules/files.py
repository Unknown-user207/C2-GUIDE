import os
import re
import shutil
from datetime import datetime

FILE_HISTORY_DIR = os.path.join(os.path.dirname(__file__), "..", "file_history")
os.makedirs(FILE_HISTORY_DIR, exist_ok=True)

def save_version(filename, content):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    version_file = os.path.join(FILE_HISTORY_DIR, f"{timestamp}_{safe_name}")
    with open(version_file, "w") as f:
        f.write(content)
    return version_file

def create_or_update_file(root, filename, content):
    full_path = os.path.join(root, filename)
    if os.path.exists(full_path):
        with open(full_path, "r") as f:
            save_version(filename, f.read())
    with open(full_path, "w") as f:
        f.write(content)
    return full_path