import json
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont
from tkinter import messagebox, ttk

# Store tasks in a JSON file beside this Python program
DATA_FILE = Path(__file__).with_name("tasks.json")


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My To-Do List")
        self.root.geometry("550x500")
        self.root.minsize(400, 400)

        self.tasks = []
        self.load_tasks()

        # Fonts that adapt to the platform's default settings
        base = tkfont.nametofont("TkDefaultFont").copy()
        self.heading_font = base.copy()
        self.heading_font.configure(size=20, weight="bold")

        # Layout: the list row (row 2) expands when the window is resized
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        # Heading
        ttk.Label(root, text="My To-Do List", font=self.heading_font).grid(
            row=0, column=0, pady=(20, 10)
        )

        # Task input area
        input_frame = ttk.Frame(root, padding=10)
        input_frame.grid(row=1, column=0, sticky="ew")
        input_frame.columnconfigure(0, weight=1)

        self.task_entry = ttk.Entry(input_frame)
        self.task_entry.grid(row=0, column=0, sticky="ew")
        self.task_entry.bind("<Return>", self.add_task)

        ttk.Button(input_frame, text="Add Task", command=self.add_task).grid(
            row=0, column=1, padx=(8, 0)
        )

        # Task list with scrollbar
        list_frame = ttk.Frame(root, padding=(15, 5))
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.task_list = tk.Listbox(list_frame, selectmode=tk.SINGLE, activestyle="dotbox")
        self.task_list.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.task_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_list.config(yscrollcommand=scrollbar.set)

        # Double-click toggles a task; clicks on empty space are ignored
        self.task_list.bind("<Double-Button-1>", self.on_double_click)

        # Action buttons
        button_frame = ttk.Frame(root, padding=10)
        button_frame.grid(row=3, column=0, sticky="ew")

        ttk.Button(button_frame, text="Complete / Undo", command=self.toggle_task).pack(side="left", padx=3)
        ttk.Button(button_frame, text="Delete Task", command=self.delete_task).pack(side="left", padx=3)
        ttk.Button(button_frame, text="Clear All", command=self.clear_tasks).pack(side="left", padx=3)

        # Status line
        self.status_label = ttk.Label(root, text="")
        self.status_label.grid(row=4, column=0, pady=(0, 15))

        self.refresh_list()
        self.task_entry.focus()

    # ---------- Data handling ----------

    def load_tasks(self):
        """Load saved tasks from the JSON file."""
        try:
            if DATA_FILE.exists():
                with DATA_FILE.open("r", encoding="utf-8") as file:
                    data = json.load(file)

                if isinstance(data, list) and all(
                    isinstance(task, dict)
                    and isinstance(task.get("title"), str)
                    and isinstance(task.get("done"), bool)
                    for task in data
                ):
                    self.tasks = data
                else:
                    messagebox.showwarning(
                        "Warning", "Saved tasks have an unexpected format. Starting empty."
                    )
        except (OSError, json.JSONDecodeError):
            messagebox.showwarning(
                "Warning", "Saved tasks could not be loaded. Starting with an empty list."
            )

    def save_tasks(self):
        """Save tasks to the JSON file."""
        try:
            with DATA_FILE.open("w", encoding="utf-8") as file:
                json.dump(self.tasks, file, indent=4, ensure_ascii=False)
        except OSError as error:
            messagebox.showerror("Save Error", f"Could not save tasks:\n{error}")

    def get_selected_index(self):
        """Return the selected task index, or None (with a message) if nothing is selected."""
        selection = self.task_list.curselection()
        if not selection:
            messagebox.showinfo("Select Task", "Please select a task first.")
            return None
        return selection[0]

    # ---------- Actions ----------

    def add_task(self, event=None):
        """Add a new task from the entry box."""
        title = self.task_entry.get().strip()

        if not title:
            messagebox.showinfo("Empty Task", "Please enter a task first.")
            return

        self.tasks.append({"title": title, "done": False})
        self.task_entry.delete(0, tk.END)
        self.save_tasks()
        self.refresh_list()
        self.task_entry.focus()

    def on_double_click(self, event):
        """Toggle a task on double-click, ignoring clicks on empty space."""
        index = self.task_list.nearest(event.y)
        bbox = self.task_list.bbox(index)

        # Only act if the click landed on an actual item
        if bbox is None or not (bbox[1] <= event.y <= bbox[1] + bbox[3]):
            return

        self.task_list.selection_clear(0, tk.END)
        self.task_list.selection_set(index)
        self._toggle_index(index)

    def toggle_task(self):
        """Toggle the selected task from the button."""
        index = self.get_selected_index()
        if index is not None:
            self._toggle_index(index)

    def _toggle_index(self, index):
        self.tasks[index]["done"] = not self.tasks[index]["done"]
        self.save_tasks()
        self.refresh_list()
        self.task_list.selection_set(index)

    def delete_task(self):
        """Delete the selected task."""
        index = self.get_selected_index()
        if index is None:
            return

        del self.tasks[index]
        self.save_tasks()
        self.refresh_list()

    def clear_tasks(self):
        """Remove all tasks after confirmation."""
        if not self.tasks:
            messagebox.showinfo("Empty List", "There are no tasks to clear.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete all tasks?"):
            self.tasks.clear()
            self.save_tasks()
            self.refresh_list()

    # ---------- Display ----------

    def refresh_list(self):
        """Rebuild the Listbox and status line from self.tasks."""
        self.task_list.delete(0, tk.END)

        for task in self.tasks:
            prefix = "[DONE]" if task["done"] else "[TODO]"
            self.task_list.insert(tk.END, f"{prefix} {task['title']}")

        completed = sum(1 for task in self.tasks if task["done"])
        total = len(self.tasks)

        self.status_label.config(
            text=f"Total: {total} | Completed: {completed} | Remaining: {total - completed}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()