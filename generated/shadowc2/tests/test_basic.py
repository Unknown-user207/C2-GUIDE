import unittest
from shadowc2.core.manager import PluginManager

class TestPluginManager(unittest.TestCase):
    def test_load_plugins(self):
        manager = PluginManager("shadowc2/plugins")
        manager.load_plugins()
        self.assertTrue(len(manager.plugins) >= 1)

if __name__ == "__main__":
    unittest.main()
