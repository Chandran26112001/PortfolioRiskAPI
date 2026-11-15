# Learning log

## Stage 0: Setup (completed 2026-11-15)

- **uv** is Maven plus SDKMAN in one tool. `pyproject.toml` is the `pom.xml`, `uv.lock` pins every package exactly (commit both), and `.venv` is this project's private package folder. Add packages with `uv add`, never `pip install`, and use `uv run` to run commands inside `.venv`.
- **Dev dependencies** (`uv add --dev`) are like Maven's `test` scope: ruff is only needed during development.
- **ruff** does both linting (`ruff check`) and formatting (`ruff format`). It exits with code 1 on problems, which is what will fail CI. `ANN` enforces type hints exist; it doesn't check they're correct.
- **Layout:** code lives in the `app/` package, and `__init__.py` marks a folder as a package. Folders get added when a stage needs them, not up front.
- **Routers** are `@RestController` classes and `@router.get` is `@GetMapping`, but routers are registered explicitly with `include_router`, not found by component scanning.
- **The return type annotation** (`-> HealthResponse`) drives response validation, filtering and the OpenAPI docs, so the docs can't drift from the code.
- **`async def` vs `def`:** `async def` runs on the single-threaded event loop, so it must never block. `def` runs in a thread pool. Blocking calls inside `async def` stall every request.
- **Liveness vs readiness:** `/health` only says the process is up. The database check belongs in a separate readiness probe (Stage 9).
- **ASGI** is Python's Servlet API: one `async def app(scope, receive, send)` contract. Uvicorn is the Tomcat, Starlette the `DispatcherServlet`, FastAPI the Spring MVC layer on top.
- **Scaling:** because of the GIL, one Python process effectively uses one CPU core for Python code. More cores means more processes (`--workers` or more containers).
- **PowerShell tip:** use `curl.exe`, because plain `curl` is an alias for `Invoke-WebRequest`.

## Parked for later stages

- GIL in depth: CPU-bound vs I/O-bound work, and its effect on the web server (Stage 7).
- How many Uvicorn workers to run against CPU cores and memory, and checking with a load test (Stage 9).
- Deploying the app (Stage 11).
