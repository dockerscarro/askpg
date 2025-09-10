def main():
    init_db()
    while True:
        print("\n📌 Task Manager")
        print("1. Add task")
        print("2. List tasks")
        print("3. Update task status")
        print("4. Delete task")
        print("5. Exit")
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
                print("❌ Invalid Task ID. Please enter an integer.")
                continue
            status = input("New status (pending/done): ")
            update_task_status(task_id, status)
        elif choice == "4":
            try:
                task_id = int(input("Task ID: "))
            except ValueError:
                print("❌ Invalid Task ID. Please enter an integer.")
                continue
            delete_task(task_id)
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()