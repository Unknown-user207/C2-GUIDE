import os

def get_project_structure(root):
    structure = {}
    for root, dirs, files in os.walk(root):
        if "file_history" in root or "__pycache__" in root or ".git" in root:
            continue
        rel_path = os.path.relpath(root, root)
        structure[rel_path] = files[:10]
    return structure