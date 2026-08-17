from fastapi import FastAPI,HTTPException

app = FastAPI(title="Task API", version="1.0")
tasks = [
    {"id": 1, "title": "Read the assignment brief", "done": True},
    {"id": 2, "title": "Build the CRUD API", "done": False},
    {"id": 3, "title": "Write the README", "done": False},
]

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def list_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id:int):
    for task in tasks:
        if task["id"]==task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")