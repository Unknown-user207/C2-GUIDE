"""
Simple APK payload builder stub.
"""

import os
import pathlib

# In a real implementation this would call the Android SDK build tools.
# Here we just create placeholder files.

BASE_DIR = pathlib.Path(__file__).parent
PAYLOADS_DIR = BASE_DIR / "generated"

def build_simple_apk(name: str, version: str = "1.0", output_dir: str = None) -> pathlib.Path:
    """
    Build a minimal APK file and return its path.

    :param name: Name of the application.
    :param version: Version of the application.
    :param output_dir: Directory to place the APK; defaults to PAYLOADS_DIR.
    :return: Path to the generated APK.
    """
    output_dir = pathlib.Path(output_dir or PAYLOADS_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    apk_name = f"{name}_{version}.apk"
    apk_path = output_dir / apk_name

    # Simulate build process
    content = f"""// Minimal APK placeholder
// App Name: {name}
// Version: {version}
"""
    apk_path.write_text(content)
    return apk_path
