from flask import Flask,render_template,url_for,request,redirect
import random
from datetime import datetime, date

app = Flask(__name__)

todos=[
   
]

# @app.route("/",methods=["GET","POST"])
# @app.route("/home",methods=["GET","POST"])
# def home():
#     if(request.method=="POST"):
#         todo_name=(request.form["todo_name"])
#         due_date = request.form.get("due_date")
#         cur_id=random.randint(1,1000)
#         todos.append({
#             'id':cur_id,
#             'name':todo_name,
#             'checked':False,
#             'due_date': due_date
PRIORITY_ORDER = {"High": 1, "Medium": 2, "Low": 3}

@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        todo_name = request.form.get("todo_name", "").strip()
        due_date_str = request.form.get("due_date", "").strip()
        priority = request.form.get("priority", "Medium")

        # Convert string to date if provided
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except ValueError:
                due_date = None

        cur_id = random.randint(1, 1000)
        todos.append({
            'id': cur_id,
            'name': todo_name,
            'checked': False,
            'due_date': due_date,
            'priority': priority
        })

        return redirect(url_for("home"))

    # Calculate overdue and sort by priority & due date
    today = date.today()
    for todo in todos:
        todo['is_overdue'] = (
            todo.get('due_date') is not None
            and todo['due_date'] < today
            and not todo.get('checked', False)
        )

    def sort_key(todo):
        p = PRIORITY_ORDER.get(todo.get('priority', 'Medium'), 3)
        d = todo.get('due_date') or date.max
        return (p, d)

    todos.sort(key=sort_key)
    return render_template("index.html", items=todos)

# })

# return render_template("index.html",items=todos)
@app.route("/checked/<int:todo_id>",methods=["POST"])
def checked_todo(todo_id):
    for todo in todos:
        if todo['id']==todo_id:
            todo['checked'] = not todo['checked']
            break
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>",methods=["POST"])
def delete_todo(todo_id):
    global todos
    for todo in todos:
        if todo['id']==todo_id:
            todos.remove(todo)
            return redirect(url_for("home"))

if __name__=="__main__":
    app.run(debug=True)
