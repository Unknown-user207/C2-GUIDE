import os
import shutil
import pathlib
import unittest
from shadowc2.payloads.apk_builder import build_simple_apk, PAYLOADS_DIR

class TestAPKBuilder(unittest.TestCase):
    def setUp(self):
        # Ensure clean state
        if PAYLOADS_DIR.exists():
            shutil.rmtree(PAYLOADS_DIR)

    def test_build_simple_apk(self):
        apk_path = build_simple_apk("TestApp", version="0.1")
        self.assertTrue(apk_path.exists())
        content = apk_path.read_text()
        self.assertIn("App Name: TestApp", content)
        self.assertIn("Version: 0.1", content)

    def tearDown(self):
        if PAYLOADS_DIR.exists():
            shutil.rmtree(PAYLOADS_DIR)

if __name__ == "__main__":
    unittest.main()
