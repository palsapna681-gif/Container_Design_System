from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import os
from datetime import datetime

app = Flask(__name__)

DATABASE = "projects.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            project_name TEXT,
            customer_contact TEXT,
            project_date TEXT,
            prepared_by TEXT,
            project_type TEXT,
            project_data TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/projects", methods=["GET"])
def get_projects():
    conn = get_db()

    rows = conn.execute("""
        SELECT id,
               customer_name,
               project_name,
               customer_contact,
               project_date,
               prepared_by,
               project_type,
               created_at,
               updated_at
        FROM projects
        ORDER BY updated_at DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    conn = get_db()

    row = conn.execute(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,)
    ).fetchone()

    conn.close()

    if not row:
        return jsonify({"error": "Project not found"}), 404

    project = dict(row)

    try:
        project["project_data"] = json.loads(project["project_data"] or "{}")
    except json.JSONDecodeError:
        project["project_data"] = {}

    return jsonify(project)


@app.route("/api/projects", methods=["POST"])
def create_project():
    data = request.get_json() or {}

    now = datetime.now().isoformat(timespec="seconds")

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO projects (
            customer_name,
            project_name,
            customer_contact,
            project_date,
            prepared_by,
            project_type,
            project_data,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("customer_name", ""),
        data.get("project_name", ""),
        data.get("customer_contact", ""),
        data.get("project_date", ""),
        data.get("prepared_by", ""),
        data.get("project_type", ""),
        json.dumps(data.get("project_data", {})),
        now,
        now
    ))

    project_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "id": project_id
    })


@app.route("/api/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    data = request.get_json() or {}

    now = datetime.now().isoformat(timespec="seconds")

    conn = get_db()

    cursor = conn.execute("""
        UPDATE projects
        SET customer_name = ?,
            project_name = ?,
            customer_contact = ?,
            project_date = ?,
            prepared_by = ?,
            project_type = ?,
            project_data = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        data.get("customer_name", ""),
        data.get("project_name", ""),
        data.get("customer_contact", ""),
        data.get("project_date", ""),
        data.get("prepared_by", ""),
        data.get("project_type", ""),
        json.dumps(data.get("project_data", {})),
        now,
        project_id
    ))

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Project not found"}), 404

    return jsonify({
        "success": True,
        "id": project_id
    })


@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    conn = get_db()

    cursor = conn.execute(
        "DELETE FROM projects WHERE id = ?",
        (project_id,)
    )

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Project not found"}), 404

    return jsonify({
        "success": True
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
