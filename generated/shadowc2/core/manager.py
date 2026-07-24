"""
Core manager to load and manage plugins.
"""

import importlib
import os
import sys
from pathlib import Path

class PluginManager:
    def __init__(self, plugin_dir):
        self.plugin_dir = Path(plugin_dir)
        self.plugins = []

    def load_plugins(self):
        if not self.plugin_dir.exists():
            return

        sys.path.insert(0, str(self.plugin_dir))
        for p in self.plugin_dir.glob("*.py"):
            if p.name == "__init__.py":
                continue
            mod_name = p.stem
            try:
                mod = importlib.import_module(mod_name)
                if hasattr(mod, "Plugin"):
                    instance = mod.Plugin()
                    self.plugins.append(instance)
            except Exception as e:
                print(f"Failed to load plugin {mod_name}: {e}")

    def run_all(self):
        for plugin in self.plugins:
            try:
                plugin.execute()
            except Exception as e:
                print(f"Plugin {plugin} failed: {e}")
