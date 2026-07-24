"""
Utility to scaffold Java/Kotlin Android payload projects.

Each payload will be a minimal Gradle project containing:
- build.gradle
- src/main (Java or Kotlin)
- A hello‑world Main class
"""

from pathlib import Path
import textwrap

JAVA_GRADLE = textwrap.dedent("""
    plugins {
        id 'java'
        id 'application'
    }

    group 'com.example'
    version '1.0.0'

    application {
        mainClassName = 'com.example.Main'
    }

    repositories {
        mavenCentral()
    }

    dependencies {
        // Add dependencies here
    }
""")

KOTLIN_GRADLE = textwrap.dedent("""
    plugins {
        id 'org.jetbrains.kotlin.jvm' version '1.9.10'
        id 'application'
    }

    group 'com.example'
    version '1.0.0'

    application {
        mainClassName = 'com.example.MainKt'
    }

    repositories {
        mavenCentral()
    }

    dependencies {
        implementation "org.jetbrains.kotlin:kotlin-stdlib"
    }
""")

JAVA_MAIN = textwrap.dedent("""
    package com.example;

    public class Main {
        public static void main(String[] args) {
            System.out.println("Hello from {name}!");
        }
    }
""")

KOTLIN_MAIN = textwrap.dedent("""
    package com.example

    fun main(args: Array<String>) {
        println("Hello from {name}!")
    }
""")

def _write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)

def create_template(language: str, name: str) -> Path:
    """
    Creates a minimal Java/Kotlin Gradle project under
    `shadowc2/payloads/generated/<name>`.
    Returns the root path of the created project.
    """
    root = Path("shadowc2/payloads/generated") / name
    if root.exists():
        raise FileExistsError(f"Project {root} already exists.")
    # Common directories
    src_main = root / "src" / "main"
    src_main_java = src_main / "java"
    src_main_kotlin = src_main / "kotlin"

    # Write build.gradle
    if language.lower() == "java":
        gradle_file = root / "build.gradle"
        _write_file(gradle_file, JAVA_GRADLE)
        # Java source
        package_path = src_main_java / "com" / "example"
        main_file = package_path / "Main.java"
        _write_file(main_file, JAVA_MAIN.format(name=name))
    elif language.lower() in ("kotlin", "kt"):
        gradle_file = root / "build.gradle"
        _write_file(gradle_file, KOTLIN_GRADLE)
        package_path = src_main_kotlin / "com" / "example"
        main_file = package_path / "Main.kt"
        _write_file(main_file, KOTLIN_MAIN.format(name=name))
    else:
        raise ValueError(f"Unsupported language: {language}")

    return root
