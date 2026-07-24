from core.manager import PluginManager
from handlers.command_handler import CommandHandler
from utils.logger import logger

def main():
    manager = PluginManager("shadowc2/plugins")
    manager.load_plugins()

    cmd_handler = CommandHandler(manager)

    # Simple REPL loop
    while True:
        try:
            cmd = input("> ").strip()
            if cmd.lower() in ("exit", "quit"):
                break
            cmd_handler.handle(cmd)
        except KeyboardInterrupt:
            break

    logger.info("Shutting down ShadowC2.")

if __name__ == "__main__":
    main()
