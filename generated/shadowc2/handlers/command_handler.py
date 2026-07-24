"""
Basic command handler example.
"""

class CommandHandler:
    def __init__(self, manager):
        self.manager = manager

    def handle(self, command: str):
        if command.lower() == "run":
            self.manager.run_all()
        else:
            print(f"Unknown command: {command}")
