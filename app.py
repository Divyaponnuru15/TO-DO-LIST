from flask import Flask, render_template, request, redirect, url_for,session, flash
import sqlite3
from datetime import datetime, date
import os 


from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "todo.db") 
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret")
# app.secret_key = "your_secret_key_here"  # change this to a random string

# ---------- DATABASE ----------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)  # <-- use DB_PATH here
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

      # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
#todo table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        due_date TEXT,
        priority TEXT,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")

    conn.commit()
    conn.close()
init_db()

# ---------- ROUTES ----------
# ---------------- ROUTES ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists!", "error")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
     
    if request.method == "POST":
        name = request.form.get("todo_name")
        due_date = request.form.get("due_date")  # can be empty
        priority = request.form.get("priority", "Medium")

        conn = get_db_connection()
        conn.execute(
    "INSERT INTO todos (user_id, name, due_date, priority) VALUES (?, ?, ?, ?)",
    (user_id, name, due_date, priority)
)

       

        conn.commit()
        conn.close()
        return redirect(url_for("home"))

    # Fetch todos from database
    conn = get_db_connection()
    
    todos = conn.execute("SELECT * FROM todos WHERE user_id = ? ORDER BY id DESC",
    (user_id,)
).fetchall()
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
    todo = conn.execute(
        "SELECT completed, user_id FROM todos WHERE id = ?",
        (todo_id,)
    ).fetchone()

    if todo and todo["user_id"] == session.get("user_id"):
        new_status = 0 if todo["completed"] == 1 else 1
        conn.execute(
            "UPDATE todos SET completed = ? WHERE id = ?",
            (new_status, todo_id)
        )
        conn.commit()

    conn.close()
    return redirect(url_for("home"))


# ---------- DELETE TODO ----------
@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    conn = get_db_connection()
    todo = conn.execute("SELECT user_id FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if todo and todo["user_id"] == session.get("user_id"):
       conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
       conn.commit()
    conn.close()
    return redirect(url_for("home"))

# ---------- MAIN ----------
if __name__ == "__main__":
   
    port = int(os.environ.get("PORT", 10000))  # default port 10000
    app.run(host="0.0.0.0", port=port, debug=True)
