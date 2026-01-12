from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, date
import os 


DB_PATH = os.path.join(os.path.dirname(__file__), "todo.db")

app = Flask(__name__)

# ---------- DATABASE ----------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)  # <-- use DB_PATH here
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            due_date TEXT,
            priority TEXT,
            completed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
init_db()

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("todo_name")
        due_date = request.form.get("due_date")  # can be empty
        priority = request.form.get("priority", "Medium")

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO todos (name, due_date, priority) VALUES (?, ?, ?)",
            (name, due_date, priority)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("home"))

    # Fetch todos from database
    conn = get_db_connection()
    todos = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    conn.close()

    today = date.today()
    todo_list = []
    for t in todos:
        due = None
        if t["due_date"] and t["due_date"].strip() != "":
            try:
                due = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
            except ValueError:
                due = None

        todo_list.append({
            "id": t["id"],
            "name": t["name"],
            "due_date": t["due_date"],
            "priority": t["priority"],
            "checked": bool(t["completed"]),
            "is_overdue": due is not None and due < today and not t["completed"]
        })

    return render_template("index.html", items=todo_list)

# ---------- TOGGLE COMPLETION ----------
@app.route("/checked/<int:todo_id>", methods=["POST"])
def checked_todo(todo_id):
    conn = get_db_connection()
    todo = conn.execute("SELECT completed FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if todo:
        new_status = 0 if todo["completed"] == 1 else 1
        conn.execute("UPDATE todos SET completed = ? WHERE id = ?", (new_status, todo_id))
        conn.commit()
    conn.close()
    return redirect(url_for("home"))

# ---------- DELETE TODO ----------
@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

# ---------- MAIN ----------
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))  # default port 10000
    app.run(host="0.0.0.0", port=port, debug=True)
