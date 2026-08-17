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


@app.put("/tasks/{task_id}", response_model=Task, summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    """Update a task's title and/or done flag. 404 if unknown, 400 if nothing to update."""
    if payload.title is None and payload.done is None:
        raise HTTPException(status_code=400, detail="Nothing to update")

    conn = get_conn()
    row = conn.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()

    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    title = row["title"]
    done = row["done"]

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            conn.close()
            raise HTTPException(status_code=400, detail="Title must not be empty")

    if payload.done is not None:
        done = 1 if payload.done else 0

    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?", (title, done, task_id)
    )
    conn.commit()

    updated = conn.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    conn.close()

    return dict(updated)


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    """Delete a task by id. Returns 204 with no body, or 404 if unknown."""
    conn = get_conn()
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return Response(status_code=204)