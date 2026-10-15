from flask import Flask, render_template, request, redirect, url_for
import json
from pathlib import Path

app = Flask(__name__)
DATA_FILE = Path(__file__).with_name("tasks.json")


def load_tasks():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)


@app.route("/", methods=["GET", "POST"])
def index():
    tasks = load_tasks()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if title:
            tasks.append({"title": title, "done": False})
            save_tasks(tasks)
        return redirect(url_for("index"))

    return render_template("index.html", tasks=tasks)


@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        tasks[task_id]["done"] = not tasks[task_id].get("done", False)
        save_tasks(tasks)
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)