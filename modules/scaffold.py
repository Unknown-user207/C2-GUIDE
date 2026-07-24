"""
scaffold.py — Auto-creates project files and folders.

On startup, ensures the expected directory layout exists.
Also exposes create_path(), used by the CLI's `create` command
and by the web interface's file-generation feature, which will
make any missing parent directories automatically.
"""

import os
import re
from datetime import datetime

DEFAULT_LAYOUT = [
    "knowledge/",
    "file_history/",
    "generated/",
]


def ensure_layout(root):
    """Create the standard folders if they don't already exist."""
    created = []
    for rel in DEFAULT_LAYOUT:
        full = os.path.join(root, rel)
        if not os.path.exists(full):
            os.makedirs(full, exist_ok=True)
            created.append(rel)
    return created


def create_path(root, relative_path, content=""):
    """
    Create (or overwrite) a file at relative_path under root,
    auto-creating any missing parent folders. Returns the full path.
    """
    full_path = os.path.join(root, relative_path)
    parent = os.path.dirname(full_path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
    return full_path


def _backup_existing(generated_root, backup_root, rel_path):
    """If rel_path exists under generated_root, copy its current content into
    backup_root with a timestamp, preserving the original relative path."""
    full_path = os.path.join(generated_root, rel_path)
    if not os.path.exists(full_path):
        return None
    with open(full_path, "r", errors="replace") as f:
        old_content = f.read()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    backup_rel = os.path.join(os.path.dirname(rel_path), f"{timestamp}__{os.path.basename(rel_path)}")
    backup_path = os.path.join(backup_root, backup_rel)
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    with open(backup_path, "w") as f:
        f.write(old_content)
    return backup_path


def parse_and_save_files(text, generated_root, backup_root=None):
    """
    Scan an assistant response for:
        FILE: relative/path.ext
        ```lang
        ...content...
        ```
    to create or overwrite a file, and:
        DELETE: relative/path.ext
    (on its own line) to remove one.

    Any file being overwritten or deleted first has its current content
    copied into backup_root (default: <generated_root>/../generated_backups),
    timestamped, so nothing is ever silently lost.

    Returns {"saved": [...], "deleted": [...]} — relative paths.
    """
    if backup_root is None:
        backup_root = os.path.join(os.path.dirname(os.path.normpath(generated_root)), "generated_backups")

    saved, deleted = [], []

    file_pattern = re.compile(r'FILE:\s*(\S+)[ \t]*\n```[^\n]*\n(.*?)```', re.DOTALL)
    for match in file_pattern.finditer(text):
        rel_path = match.group(1).strip()
        content = match.group(2)

        safe_rel = os.path.normpath(rel_path).lstrip(os.sep)
        if safe_rel.startswith(".."):
            continue  # refuse to write outside generated_root

        _backup_existing(generated_root, backup_root, safe_rel)
        full_path = create_path(generated_root, safe_rel, content)
        saved.append(os.path.relpath(full_path, generated_root))

    delete_pattern = re.compile(r'^DELETE:\s*(\S+)\s*$', re.MULTILINE)
    for match in delete_pattern.finditer(text):
        rel_path = match.group(1).strip()
        safe_rel = os.path.normpath(rel_path).lstrip(os.sep)
        if safe_rel.startswith(".."):
            continue

        full_path = os.path.join(generated_root, safe_rel)
        if os.path.exists(full_path):
            _backup_existing(generated_root, backup_root, safe_rel)
            os.remove(full_path)
            deleted.append(safe_rel)

    return {"saved": saved, "deleted": deleted}


def list_generated_files(generated_root):
    """Return a flat list of relative paths under generated_root."""
    files = []
    if not os.path.exists(generated_root):
        return files
    for dirpath, _, filenames in os.walk(generated_root):
        for fn in filenames:
            if fn == ".gitkeep":
                continue
            full = os.path.join(dirpath, fn)
            files.append(os.path.relpath(full, generated_root))
    return sorted(files)


def save_version(history_dir, filename, content):
    """Keep a timestamped copy of a file's previous content before overwriting."""
    os.makedirs(history_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    version_path = os.path.join(history_dir, f"{timestamp}_{safe_name}")
    with open(version_path, "w") as f:
        f.write(content)
    return version_path


def create_or_update_file(root, history_dir, relative_path, content):
    """Create a file, versioning the old content first if it already exists."""
    full_path = os.path.join(root, relative_path)
    if os.path.exists(full_path):
        with open(full_path, "r") as f:
            save_version(history_dir, relative_path, f.read())
    return create_path(root, relative_path, content)
