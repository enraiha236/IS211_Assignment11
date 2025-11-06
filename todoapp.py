from flask import Flask, request, redirect, url_for, render_template
import re
import os
import pickle

app = Flask(__name__)
DATA_FILE = 'todo_data.pkl'

# in memory store
todos = []
next_id = 0

def is_email(s):
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', s))

def load_data():
    global todos, next_id
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'rb') as f:
                todos = pickle.load(f)
            if todos:
                # compute next id so we do not reuse ids
                max_id = max(item.get('id', 0) for item in todos)
                next_id = max_id + 1
            else:
                next_id = 0
        except Exception:
            todos = []
            next_id = 0
    else:
        todos = []
        next_id = 0

def save_data():
    try:
        with open(DATA_FILE, 'wb') as f:
            pickle.dump(todos, f)
        return True
    except Exception:
        return False

# load on startup
load_data()

@app.route('/')
def index():
    msg = request.args.get('msg')
    err = request.args.get('error')
    return render_template('todo_list.html', todos=todos, msg=msg, error=err)

@app.route('/submit', methods=['POST'])
def submit():
    global next_id
    task = request.form.get('task', '').strip()
    email = request.form.get('email', '').strip()
    priority = request.form.get('priority', '').strip()
    if not task:
        return redirect(url_for('index', error='Task cannot be empty'))
    if not is_email(email):
        return redirect(url_for('index', error='Invalid email address'))
    if priority not in ('Low', 'Medium', 'High'):
        return redirect(url_for('index', error='Invalid priority'))
    new_item = {'id': next_id, 'task': task, 'email': email, 'priority': priority}
    todos.append(new_item)
    next_id += 1
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear():
    todos.clear()
    save_data()
    return redirect(url_for('index', msg='List cleared'))

@app.route('/save', methods=['POST'])
def save_route():
    ok = save_data()
    if ok:
        return redirect(url_for('index', msg='List saved'))
    return redirect(url_for('index', error='Save failed'))

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    before = len(todos)
    todos[:] = [t for t in todos if t.get('id') != item_id]
    if len(todos) < before:
        save_data()
        return redirect(url_for('index', msg='Item deleted'))
    return redirect(url_for('index', error='Item not found'))

if __name__ == '__main__':
    app.run()
