import unittest
from shadowc2.handlers.command_handler import CommandHandler
from shadowc2.core.manager import PluginManager

class DummyPlugin:
    def __init__(self):
        self.executed = False

    def execute(self):
        self.executed = True

class TestCommandHandler(unittest.TestCase):
    def setUp(self):
        # Create a manager with a dummy plugin
        self.manager = PluginManager("shadowc2/plugins")
        self.manager.plugins = [DummyPlugin()]
        self.cmd_handler = CommandHandler(self.manager)

    def test_run_command_executes_plugin(self):
        self.cmd_handler.handle("run")
        for plugin in self.manager.plugins:
            self.assertTrue(plugin.executed)

    def test_unknown_command(self):
        # Capture stdout
        import io, sys
        captured = io.StringIO()
        sys.stdout = captured
        self.cmd_handler.handle("foobar")
        sys.stdout = sys.__stdout__
        self.assertIn("Unknown command", captured.getvalue())

if __name__ == "__main__":
    unittest.main()
