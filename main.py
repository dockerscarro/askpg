Here is the updated Python code with input validation and error handling:

def validate_task_id(task_id):
    try:
        return int(task_id)
    except ValueError:
        raise ValueError("Task ID must be an integer.")

def task_exists(task_id):
    conn = connect_pg()
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM {TABLE_NAME} WHERE id = %s", (task_id,))
        exists = cur.fetchone() is not None
    conn.close()
    if not exists:
        raise ValueError(f"Task with ID {task_id} does not exist.")
    return True

def safe_execute_db_operation(operation, *args, **kwargs):
    try:
        return operation(*args, **kwargs)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None

# Replace all database operations with safe_execute_db_operation
# For example:
# task_id = safe_execute_db_operation(insert_task_pg, task)

This code adds three new functions:

- `validate_task_id` checks if the task ID is an integer and raises a `ValueError` if not.
- `task_exists` checks if a task with the given ID exists in the database and raises a `ValueError` if not.
- `safe_execute_db_operation` wraps a database operation in a try/except block to catch `psycopg2.Error` exceptions and prevent the app from crashing.

You would need to replace all database operations in your code with calls to `safe_execute_db_operation`. For example, if you have a function `insert_task_pg(task)` that inserts a task into the database, you would replace it with `safe_execute_db_operation(insert_task_pg, task)`.