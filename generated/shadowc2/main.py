"""
Entry point for the core ShadowC2 application.
"""

from core.manager import PluginManager
from handlers.command_handler import CommandHandler
from utils.logger import logger

def main():
    # Load core plugins
    manager = PluginManager("shadowc2/plugins")
    manager.load_plugins()

    cmd_handler = CommandHandler(manager)

    # Simple command‑line REPL
    print("ShadowC2 core. Type 'run' to execute plugins, 'exit' to quit.")
    while True:
        try:
            cmd = input("> ").strip()
            if cmd.lower() in ("exit", "quit"):
                break
            cmd_handler.handle(cmd)
        except KeyboardInterrupt:
            print("\nInterrupted")
            break

    logger.info("Shutting down ShadowC2.")

if __name__ == "__main__":
    main()
