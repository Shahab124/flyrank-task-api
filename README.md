# Task API — FlyRank Internship, Backend Track (Weeks 2–3)

A CRUD API for managing a to-do list, built with **FastAPI** and backed by **SQLite**.

Built across two assignments: Week 2 stored tasks in an in-memory Python list, Week 3 moved that
storage to a real database. The endpoints did not change — only what sits behind them.

---

## Requirements

- Python 3.10 or newer

## Install & run

```bash
git clone https://github.com/Shahab124/flyrank-task-api.git
cd flyrank-task-api
py -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install "fastapi[standard]"
uvicorn main:app --reload
```

That is the one command. `tasks.db` is not in this repo and does not need to be — the app
creates the file, creates the `tasks` table, and seeds three example tasks on first run. A fresh
clone is a working app with data in it.

- Server: **http://localhost:8000**
- Interactive docs: **http://localhost:8000/docs**

---

## Endpoints

| Method | Path          | Purpose                       | Success | Errors                          |
|--------|---------------|-------------------------------|---------|---------------------------------|
| GET    | `/`           | API description               | 200     | —                               |
| GET    | `/health`     | Liveness check                | 200     | —                               |
| GET    | `/tasks`      | List all tasks                | 200     | —                               |
| GET    | `/tasks/{id}` | Get one task                  | 200     | 404 unknown id                  |
| POST   | `/tasks`      | Create a task                 | 201     | 400 empty title · 422 no title  |
| PUT    | `/tasks/{id}` | Update title and/or done flag | 200     | 400 invalid body · 404 unknown  |
| DELETE | `/tasks/{id}` | Delete a task                 | 204     | 404 unknown id                  |

### Task shape

```json
{ "id": 1, "title": "Buy milk", "done": false }
```

### A note on 400 vs 422

`POST /tasks` with `{}` returns **422**, not 400. That is Pydantic rejecting the request before
my code runs, because `title` is required by the request model. `{"title": "   "}` returns
**400** from my own validation, because "is this a string?" is a question the framework can
answer and "is an all-whitespace title a meaningful task?" is one only I can. Framework
validation handles shape; my code handles meaning. Both are 4xx and both tell the client it made
the mistake.

---

## Why SQLite

- **It is one file.** `tasks.db` sits next to the code. No server to install, no port, no
  credentials, no Docker.
- **Zero setup for whoever clones this.** The file and the table create themselves on first run,
  which is what keeps the install instructions above at one command.
- **The data survives a restart** — the one thing the in-memory version could not do, and the
  entire point of this assignment.

SQLite is not right for everything. It is a single file on one machine, so it does not suit an
app with many servers writing at once; that is where Postgres earns its keep. For a project this
size the trade is free.

---

## Database

One table, created automatically if missing:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT    NOT NULL,
    done  INTEGER NOT NULL DEFAULT 0
);
```

Notes on the shape and the decisions behind it:

- **SQLite has no boolean type.** `done` is stored as `0` or `1`; the Pydantic response model
  converts it back to `true` / `false`, so the JSON a client sees is byte-for-byte what Week 2
  returned. The storage layer's limitation never reaches the client.
- **The database assigns ids.** Week 2 generated them in Python with `max(...) + 1`. That code is
  gone.
- **Seeding runs only once.** The app counts the rows before inserting and only seeds when the
  table is empty, so restarting never multiplies the examples. Empty the table and the next
  restart restores them.
- **Every query is parameterized.** Values are passed as `?` placeholders, never glued into the
  SQL string. That is what stops a title containing an apostrophe from breaking the query, and
  what stops a title containing SQL from being executed as SQL.
- **Reads happen after writes.** `POST` and `PUT` re-read the row from the database before
  returning it, instead of returning a dict built in Python. Slightly slower, but the response is
  then what is actually stored rather than what I assumed would be stored.

`tasks.db` is git-ignored. It is generated data, not source, so every clone starts fresh.

---

## Example: `curl -i` against the database

Real terminal output. Note the ids — the API had already issued id 4, so this new task is 5.

```
> curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Test task\"}"
HTTP/1.1 201 Created
server: uvicorn
content-type: application/json

{"id":5,"title":"Test task","done":false}

> curl -i http://localhost:8000/tasks
HTTP/1.1 200 OK
server: uvicorn
content-type: application/json

[{"id":1,"title":"Read the assignment brief","done":true},
 {"id":2,"title":"Build the CRUD API","done":false},
 {"id":3,"title":"Write the README","done":false},
 {"id":5,"title":"Test task","done":false}]

> curl -i -X PUT http://localhost:8000/tasks/4 -H "Content-Type: application/json" -d "{\"done\":true}"
HTTP/1.1 404 Not Found
server: uvicorn
content-type: application/json

{"detail":"Task 4 not found"}

> curl -i -X DELETE http://localhost:8000/tasks/999
HTTP/1.1 404 Not Found
server: uvicorn
content-type: application/json

{"detail":"Task 999 not found"}
```

Task 4 had been created and deleted earlier in the session, which is why both requests aimed at
it return 404 rather than an empty 200. An id that no longer exists is a client error, and the
status code says so.

### What the ids taught me

The database hands out ids and never reuses them. I created a task, deleted it, then created
another — and the new one came back as **id 5, not id 4**. SQLite records the highest id it has
ever issued in its own `sqlite_sequence` table, created automatically when I used
`AUTOINCREMENT`.

My Week 2 version would have reused id 4 immediately, because `max(...) + 1` only looks at what
is still in the list. That matters as soon as anything outside the database holds a reference to
a task: a reused id silently points an old link at a new row.

### Persistence

Create a task, stop the server with Ctrl+C, start it again, then call `GET /tasks` — the task is
still there. In the Week 2 version it would have been gone, because the list lived inside the
process and the process had ended. Across every restart this week, the count stayed at three
seeded tasks plus whatever I had created: the seed guard held.

---

## SQL run by hand

Opened `tasks.db` in DB Browser for SQLite with the server still running, and ran these in the
Execute SQL tab:

```sql
SELECT * FROM tasks;
SELECT * FROM tasks WHERE done = 1;
SELECT COUNT(*) FROM tasks;
SELECT * FROM tasks WHERE title LIKE '%task%';
```

`SELECT * FROM tasks WHERE done = 1;` returned only the completed tasks — filtered by the
database rather than by a loop in my Python code. In Week 2 that same filter would have been a
list comprehension inside the endpoint.

Two programs were reading the same file at the same time: my running FastAPI server and DB
Browser. There is no syncing step between them because there is nothing to sync. The database is
the single source of truth, and the API is one of its clients rather than the owner of the data.

![tasks table open in DB Browser for SQLite](docs/db-browser.png)

---

## Swagger UI

FastAPI generates an OpenAPI spec from the type hints and Pydantic models, so the documentation
comes out of the code instead of being written by hand. The raw spec is at `/openapi.json`; the
interactive page at `/docs` runs the full CRUD cycle with "Try it out".

![Swagger UI showing all endpoints](docs/swagger.png)

---

## What I would do next

- Move search and filtering into SQL (`WHERE title LIKE ?`, `WHERE done = ?`) so the database
  does the work my Python loops would otherwise do.
- Add an index on any column I filter by, once there are enough rows for it to matter.
- Add `created_at` / `updated_at` columns — which means changing the shape of a table that
  already has data in it, and that problem is what migrations exist to solve.
- Add tests. There are none. Every endpoint in this repo is currently verified by hand with
  `curl`, which does not scale past the point where I can remember what to check.
