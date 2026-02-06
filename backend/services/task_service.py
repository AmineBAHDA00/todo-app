from models.task_model import get_all_tasks, create_task, delete_task, update_task

def format_task(task):
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "completed": task.get("completed", False)
    }
