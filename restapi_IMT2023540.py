"""
REST API for Task Handling
Author: <Your Name> (Roll Number: <Your Roll Number>)
Description: Flask-based REST API that allows CRUD operations on tasks
"""

from flask import Flask, request, jsonify
from datetime import datetime
import uuid

# Initialize Flask app
application = Flask(__name__)

# In-memory storage (simulate DB)
task_list = []

# Default tasks to start with
default_tasks = [
    {
        "task_id": str(uuid.uuid4()),
        "name": "Finish API homework",
        "details": "Write Flask REST API with CRUD endpoints",
        "state": "in_progress",
        "created": "2025-09-30T10:00:00",
        "modified": "2025-09-30T10:00:00"
    },
    {
        "task_id": str(uuid.uuid4()),
        "name": "Prepare for SE exam",
        "details": "Revise Flask, REST fundamentals",
        "state": "pending",
        "created": "2025-09-30T09:00:00",
        "modified": "2025-09-30T09:00:00"
    }
]

task_list.extend(default_tasks)


# Utility: find task by ID
def get_task(task_id):
    return next((item for item in task_list if item["task_id"] == task_id), None)


# Utility: validate task input
def check_task_payload(payload, must_have=None):
    if must_have is None:
        must_have = ["name"]

    for key in must_have:
        if key not in payload or not str(payload[key]).strip():
            return False, f"'{key}' is required and cannot be empty"

    valid_states = ["pending", "in_progress", "completed"]
    if "state" in payload and payload["state"] not in valid_states:
        return False, f"State must be one of: {', '.join(valid_states)}"

    return True, ""


# --------------------- ROUTES ---------------------

# Root endpoint (API info)
@application.route('/', methods=['GET'])
def home():
    return jsonify({
        "ok": True,
        "meta": {
            "api": "Task Handling API",
            "version": "1.0",
            "available": len(task_list),
            "allowed_states": ["pending", "in_progress", "completed"]
        },
        "routes": {
            "GET /tasks": "Fetch all tasks (filter with ?state=)",
            "GET /tasks/<task_id>": "Fetch one task",
            "POST /tasks": "Add a new task",
            "PUT /tasks/<task_id>": "Modify an existing task",
            "DELETE /tasks/<task_id>": "Remove a task",
            "DELETE /tasks": "Remove all tasks",
            "GET /status": "API health status"
        }
    })


# Health check
@application.route('/status', methods=['GET'])
def health():
    return jsonify({
        "ok": True,
        "time": datetime.now().isoformat(),
        "task_count": len(task_list),
        "server_status": "running"
    })


# Get all tasks (with optional filter)
@application.route('/tasks', methods=['GET'])
def fetch_tasks():
    try:
        filter_state = request.args.get('state')
        if filter_state:
            filtered = [t for t in task_list if t["state"] == filter_state]
            return jsonify({"ok": True, "total": len(filtered), "items": filtered}), 200
        return jsonify({"ok": True, "total": len(task_list), "items": task_list}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# Get task by ID
@application.route('/tasks/<string:task_id>', methods=['GET'])
def fetch_task(task_id):
    task = get_task(task_id)
    if not task:
        return jsonify({"ok": False, "error": "Task not found"}), 404
    return jsonify({"ok": True, "task": task}), 200


# Create task
@application.route('/tasks', methods=['POST'])
def add_task():
    payload = request.get_json()
    if not payload:
        return jsonify({"ok": False, "error": "Missing JSON data"}), 400

    valid, msg = check_task_payload(payload, ["name"])
    if not valid:
        return jsonify({"ok": False, "error": msg}), 400

    now = datetime.now().isoformat()
    new_task = {
        "task_id": str(uuid.uuid4()),
        "name": payload["name"].strip(),
        "details": payload.get("details", "").strip(),
        "state": payload.get("state", "pending"),
        "created": now,
        "modified": now
    }
    task_list.append(new_task)
    return jsonify({"ok": True, "task": new_task}), 201


# Update task
@application.route('/tasks/<string:task_id>', methods=['PUT'])
def modify_task(task_id):
    task = get_task(task_id)
    if not task:
        return jsonify({"ok": False, "error": "Task not found"}), 404

    payload = request.get_json()
    if not payload:
        return jsonify({"ok": False, "error": "Missing JSON data"}), 400

    valid, msg = check_task_payload(payload, [])
    if not valid:
        return jsonify({"ok": False, "error": msg}), 400

    if "name" in payload and payload["name"].strip():
        task["name"] = payload["name"].strip()
    if "details" in payload:
        task["details"] = payload["details"].strip()
    if "state" in payload:
        task["state"] = payload["state"]

    task["modified"] = datetime.now().isoformat()
    return jsonify({"ok": True, "task": task}), 200


# Delete task
@application.route('/tasks/<string:task_id>', methods=['DELETE'])
def remove_task(task_id):
    task = get_task(task_id)
    if not task:
        return jsonify({"ok": False, "error": "Task not found"}), 404
    task_list.remove(task)
    return jsonify({"ok": True, "deleted": task_id}), 200


# Delete all tasks
@application.route('/tasks', methods=['DELETE'])
def clear_tasks():
    deleted = len(task_list)
    task_list.clear()
    return jsonify({"ok": True, "removed_count": deleted}), 200


# Error handlers
@application.errorhandler(404)
def not_found(e):
    return jsonify({"ok": False, "error": "Endpoint not found"}), 404

@application.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"ok": False, "error": "HTTP method not allowed"}), 405

@application.errorhandler(500)
def server_error(e):
    return jsonify({"ok": False, "error": "Internal server error"}), 500


if __name__ == "__main__":
    print(">>> Task Handling API is live at http://127.0.0.1:5000")
    application.run(debug=True)
