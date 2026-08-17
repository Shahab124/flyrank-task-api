# Task API — FlyRank Internship, Week 2 (Backend Track)

A small CRUD API for managing a to-do list, built with **FastAPI**. Tasks are stored in an
in-memory Python list — no database. Restarting the server resets the data, deliberately
(see [The mortality experiment](#the-mortality-experiment)).

Built by hand, stage by stage, as Assignment A1 of the FlyRank backend track.

---

## Requirements

- Python 3.10 or newer

## Install & run

```bash
git clone https://github.com/Shahab124/flyrank-task-api.git
cd flyrank-task-api
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install "fastapi[standard]"
uvicorn main:app --reload
```

The server starts at **http://localhost:8000**.
Interactive docs: **http://localhost:8000/docs**

---

## Endpoints

| Method | Path              | Purpose                       | Success | Errors                          |
|--------|-------------------|-------------------------------|---------|---------------------------------|
| GET    | `/`               | API description               | 200     | —                               |
| GET    | `/health`         | Liveness check                | 200     | —                               |
| GET    | `/tasks`          | List all tasks                | 200     | —                               |
| GET    | `/tasks/{id}`     | Get one task                  | 200     | 404 unknown id                  |
| POST   | `/tasks`          | Create a task                 | 201     | 400 empty title · 422 no title  |
| PUT    | `/tasks/{id}`     | Update title and/or done flag | 200     | 400 invalid body · 404 unknown  |
| DELETE | `/tasks/{id}`     | Delete a task                 | 204     | 404 unknown id                  |

### Task shape

```json
{ "id": 1, "title": "Buy milk", "done": false }
```

### A note on 400 vs 422

Sending `{}` to `POST /tasks` returns **422**, not 400. That is Pydantic rejecting the request
before my code runs, because the `title` field is required by the request model. Sending
`{"title": "   "}` returns **400** from my own validation, because "is this a string?" is a
question the framework can answer and "is an all-whitespace title meaningful?" is one only I can.
Framework validation handles shape; my code handles meaning. Both are 4xx, both tell the client
it made the mistake.

---

## Example: full CRUD cycle with `curl -i`

<!-- Paste your real terminal output between the fences below. -->

```
PASTE YOUR curl -i OUTPUT HERE
```

---

## Swagger UI

FastAPI generates an OpenAPI spec from the code — the type hints and Pydantic models *are* the
documentation. The raw spec is served at `/openapi.json`; Swagger UI renders it at `/docs`,
where the full create → read → update → delete cycle can be run with "Try it out".

<!-- Add your screenshot to the repo, then update the path below. -->

![Swagger UI showing all endpoints](docs/swagger.png)

---

## The mortality experiment

Create a few tasks, stop the server, start it again, then `GET /tasks`.

<!-- Write your own two sentences here after you actually run it. -->

---

## What I would do next

- Move storage to a real database so data survives a restart (Week 3).
- Add pagination to `GET /tasks` — real APIs never return everything, because "everything"
  grows without limit and one slow client can exhaust the server's memory.
- Split routes out of `main.py` into a router module once the endpoint count grows.

---

## AI vs me

<!-- Stage 7. Paste your full prompt, then the three findings. -->
