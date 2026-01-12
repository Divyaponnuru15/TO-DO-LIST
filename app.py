# from flask import Flask,render_template,url_for,request,redirect
# import random
# from datetime import datetime, date
# import sqlite3

# def init_db():
#     conn = sqlite3.connect("todo.db")
#     cursor = conn.cursor()

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS todos (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             due_date DATE,
#             priority TEXT,
#             completed INTEGER DEFAULT 0
#         )
#     """)

#     conn.commit()
#     conn.close()


# app = Flask(__name__)

# PRIORITY_ORDER = {"High": 1, "Medium": 2, "Low": 3}

# @app.route("/", methods=["GET", "POST"])
# @app.route("/home", methods=["GET", "POST"])
# def home():
#     if request.method == "POST":
#      name = request.form["todo_name"]
#      due_date = request.form.get("due_date")
#      priority = request.form.get("priority", "Medium")

#      conn = get_db_connection()
#      conn.execute(
#         "INSERT INTO todos (name, due_date, priority) VALUES (?, ?, ?)",
#         (name, due_date, priority)
#     )
#      conn.commit()
#      conn.close()

#      return redirect(url_for("home"))

#     # if request.method == "POST":
#     #     todo_name = request.form.get("todo_name", "").strip()
#     #     due_date_str = request.form.get("due_date", "").strip()
#     #     priority = request.form.get("priority", "Medium")

#         # Convert string to date if provided
#     due_date = None
#     if due_date_str:
#         try:
#                 due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
#         except ValueError:
#                 due_date = None

#         cur_id = random.randint(1, 1000)
#         todos.append({
#             'id': cur_id,
#             'name': todo_name,
#             'checked': False,
#             'due_date': due_date,
#             'priority': priority
#         })

#         return redirect(url_for("home"))

#     # Calculate overdue and sort by priority & due date
#     today = date.today()
#     for todo in todos:
#         todo['is_overdue'] = (
#             todo.get('due_date') is not None
#             and todo['due_date'] < today
#             and not todo.get('checked', False)
#         )

#     def sort_key(todo):
#         p = PRIORITY_ORDER.get(todo.get('priority', 'Medium'), 3)
#         d = todo.get('due_date') or date.max
#         return (p, d)

#     todos.sort(key=sort_key)
#     return render_template("index.html", items=todos)

# # })

# # return render_template("index.html",items=todos)
# @app.route("/checked/<int:todo_id>",methods=["POST"])
# def checked_todo(todo_id):
#     for todo in todos:
#         if todo['id']==todo_id:
#             todo['checked'] = not todo['checked']
#             break
#     return redirect(url_for("home"))

# @app.route("/delete/<int:todo_id>",methods=["POST"])
# def delete_todo(todo_id):
#     global todos
#     for todo in todos:
#         if todo['id']==todo_id:
#             todos.remove(todo)
#             return redirect(url_for("home"))
# if __name__ == "__main__":
#     init_db()
#     app.run(debug=True)

# # if __name__=="__main__":
# #     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

# ---------- DATABASE ----------
def get_db_connection():
    conn = sqlite3.connect("todo.db")
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
    app.run(debug=True)
