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

def handle_database_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return None
    return wrapper

@handle_database_errors
def update_task(task_id, new_data):
    task_id = validate_task_id(task_id)
    task_exists(task_id)
    # Continue with update operation...

@handle_database_errors
def delete_task(task_id):
    task_id = validate_task_id(task_id)
    task_exists(task_id)
    # Continue with delete operation...

In this updated code, we've added a `validate_task_id` function to ensure the task ID is an integer, and a `task_exists` function to check if a task with the given ID exists in the database. We've also added a `handle_database_errors` decorator to catch and handle any database errors that occur during task operations. This decorator is applied to the `update_task` and `delete_task` functions to ensure they handle database errors gracefully.