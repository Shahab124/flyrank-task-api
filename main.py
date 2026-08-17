from fastapi import FastAPI,HTTPException, Response
from pydantic import BaseModel
from db import get_conn, init_db

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

class Task(BaseModel):
    id: int
    title: str
    done: bool

app = FastAPI(title="Task API", version="1.0")
init_db()

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

@app.get("/tasks", response_model=list[Task], summary="List all tasks")
def list_tasks():
    """Return every task in the database."""
    conn = get_conn()
    rows = conn.execute("SELECT id, title, done FROM tasks").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/tasks/{task_id}", response_model=Task, summary="Get one task")
def get_task(task_id: int):
    """Return a single task by id. Returns 404 if it does not exist."""
    conn = get_conn()
    row = conn.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return dict(row)

@app.post("/tasks", response_model=Task, status_code=201, summary="Create a task")
def create_task(payload: TaskCreate):
    """Create a task with the given title. Returns 400 if the title is empty."""
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title must not be empty")

    conn = get_conn()
    cursor = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)", (title, 0)
    )
    conn.commit()
    new_id = cursor.lastrowid
    row = conn.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (new_id,)
    ).fetchone()
    conn.close()

    return dict(row)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            if payload.title is None and payload.done is None:
                raise HTTPException(status_code=400, detail="Nothing to update")
            if payload.title is not None:
                title = payload.title.strip()
                if not title:
                    raise HTTPException(status_code=400, detail="Title must not be empty")
                task["title"] = title
            if payload.done is not None:
                task["done"] = payload.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return Response(status_code=204)
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")