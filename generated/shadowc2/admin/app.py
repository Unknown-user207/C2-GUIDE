# Existing imports
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
# Add new import
from payloads.template_builder import create_template
# ... rest unchanged ...

# ----------------------------------------------------------------------
# New REST endpoint: Create a template payload project
# ----------------------------------------------------------------------
@app.route("/api/payloads/template", methods=["POST"])
def create_payload_template():
    """
    Create a minimal Java/Kotlin Gradle project.
    Expected JSON:
        {
            "language": "java" | "kotlin",
            "name": "MyApp"
        }
    """
    data = request.get_json(force=True)
    language = data.get("language", "").lower()
    name = data.get("name", "").strip()

    if not language or not name:
        return jsonify({"error": "Both 'language' and 'name' are required."}), 400

    try:
        root_path = create_template(language, name)
    except FileExistsError:
        return jsonify({"error": f"Project '{name}' already exists."}), 409
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"status": "created", "path": str(root_path)}), 201

# ----------------------------------------------------------------------
# Existing code remains unchanged
# ----------------------------------------------------------------------
if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5001, debug=True)
