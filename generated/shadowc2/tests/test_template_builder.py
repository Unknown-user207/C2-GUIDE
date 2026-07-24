import shutil
import unittest
from pathlib import Path
from shadowc2.payloads.template_builder import create_template

class TestTemplateBuilder(unittest.TestCase):
    def setUp(self):
        self.gen_dir = Path("shadowc2/payloads/generated")
        if self.gen_dir.exists():
            shutil.rmtree(self.gen_dir)

    def test_java_template(self):
        root = create_template("java", "TestApp")
        self.assertTrue(root.exists())
        self.assertTrue((root / "build.gradle").exists())
        self.assertTrue((root / "src/main/java/com/example/Main.java").exists())

    def test_kotlin_template(self):
        root = create_template("kotlin", "KotlinApp")
        self.assertTrue(root.exists())
        self.assertTrue((root / "build.gradle").exists())
        self.assertTrue((root / "src/main/kotlin/com/example/Main.kt").exists())

    def tearDown(self):
        if self.gen_dir.exists():
            shutil.rmtree(self.gen_dir)

if __name__ == "__main__":
    unittest.main()
