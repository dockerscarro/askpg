import sqlite3
import os
from datetime import datetime

DB_FILE = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    created_at TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

def add_task(title, description=""):
    priority = "medium":
        c.execute("INSERT INTO tasks (title, description, created_at, priority) VALUES (?, ?, ?, ?)",
                  (title, description, datetime.utcnow().isoformat(), priority))
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title, description, created_at) VALUES (?, ?, ?)",
              (title, description, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    print("✅ Task added!")

def list_tasks():
    def update_task_priority(task_id, priority):
    def check_overdue_tasks():
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, title, status, created_at FROM tasks WHERE created_at < ?", (datetime.utcnow().isoformat(),))
        rows = c.fetchall()
        conn.close()
        if not rows:
            print("📂 No overdue tasks found.")
        else:
            for row in rows:
                print(f"[{row[0]}] {row[1]} ({row[2]}) - Created at {row[3]}")
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        if c.fetchone() is None:
            print("❌ Task not found.")
            return
        c.execute("UPDATE tasks SET priority = ? WHERE id = ?", (priority, task_id))
        conn.commit()
        conn.close()
        print("🔄 Task priority updated!")
    c.execute("SELECT id, title, status, priority, created_at FROM tasks ORDER BY created_at DESC")
            for row in rows:
                print(f"[{row[0]}] {row[1]} ({row[2]}, Priority: {row[3]}) - Created at {row[4]}")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, status, created_at FROM tasks ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    if not rows:
        print("📂 No tasks found.")
    else:
        for row in rows:
            print(f"[{row[0]}] {row[1]} ({row[2]}) - Created at {row[3]}")

def update_task_status(task_id, new_status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if c.fetchone() is None:
        print("❌ Task not found.")
        return
    c.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()
    print("🔄 Task updated!")

def delete_task(task_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if c.fetchone() is None:
        print("❌ Task not found.")
        return
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    print("🗑️ Task deleted!")

def main():
    init_db()
    while True:
        print("\n📌 Task Manager")
        print("1. Add task")
        print("2. List tasks")
        print("3. Update task status")
        print("4. Delete task")
        print("print("6. Update task priority")
        print("7. Check overdue tasks")
5. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            title = input("Task title: ")
            desc = input("Task description (optional): ")
            add_task(title, desc)
        elif choice == "2":
            list_tasks()
        elif choice == "3":
            try:
                task_id = int(input("Task ID: "))
            except ValueError:
                print("❌ Invalid input. Please enter an integer.")
                continue
            status = input("New status (pending/done): ")
            update_task_status(task_id, status)
        elif choice == "4":
            try:
                task_id = int(input("Task ID: "))
            except ValueError:
                print("❌ Invalid input. Please enter an integer.")
                continue
            delete_task(task_id)
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
