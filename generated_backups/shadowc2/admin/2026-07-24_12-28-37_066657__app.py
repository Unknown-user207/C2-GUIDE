"""
Simple admin panel based on Flask.
"""

import json
from flask import Flask, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Dummy in‑memory device registry for the dashboard
DEVICES = [
    {"id": 1, "name": "Device_A", "status": "online", "last_seen": datetime.utcnow().isoformat()},
    {"id": 2, "name": "Device_B", "status": "offline", "last_seen": datetime.utcnow().isoformat()},
    {"id": 3, "name": "Device_C", "status": "online", "last_seen": datetime.utcnow().isoformat()},
]

# Very small HTML template to display device stats
dashboard_template = """
<!doctype html>
<title>Device Dashboard</title>
<h1>Device Living Dashboard</h1>
<table border=1 cellpadding=5 cellspacing=0>
<tr><th>ID</th><th>Name</th><th>Status</th><th>Last Seen</th></tr>
{% for d in devices %}
<tr>
<td>{{ d.id }}</td>
<td>{{ d.name }}</td>
<td>{{ d.status }}</td>
<td>{{ d.last_seen }}</td>
</tr>
{% endfor %}
</table>
"""

@app.route("/")
def dashboard():
    return render_template_string(dashboard_template, devices=DEVICES)

@app.route("/api/devices", methods=["GET"])
def api_devices():
    return jsonify(DEVICES)

# To run the panel:
#   export FLASK_APP=shadowc2.admin.app
#   flask run --port 5001
