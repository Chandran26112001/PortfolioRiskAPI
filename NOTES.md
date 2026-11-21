# Learning log

## Stage 0: Setup (completed 2026-11-15)

- **uv** is Maven plus SDKMAN in one tool. `pyproject.toml` is the `pom.xml`, `uv.lock` pins every package exactly (commit both), and `.venv` is this project's private package folder. Add packages with `uv add`, never `pip install`, and use `uv run` to run commands inside `.venv`.
- **Dev dependencies** (`uv add --dev`) are like Maven's `test` scope: ruff is only needed during development.
- **ruff** does both linting (`ruff check`) and formatting (`ruff format`). It exits with code 1 on problems, which is what will fail CI. `ANN` enforces type hints exist; it doesn't check they're correct.
- **Layout:** code lives in the `app/` package, and `__init__.py` marks a folder as a package. Folders get added when a stage needs them, not up front.
- **Routers** are `@RestController` classes and `@router.get` is `@GetMapping`, but routers are registered explicitly with `include_router`, not found by component scanning.
- **The return type annotation** (`-> HealthResponse`) drives response validation, filtering and the OpenAPI docs, so the docs can't drift from the code.
- **`async def` vs `def`:** `async def` runs on the single-threaded event loop, so it must never block. `def` runs in a thread pool. Blocking calls inside `async def` stall every request.
- **Liveness vs readiness:** `/health` only says the process is up. The database check belongs in a separate readiness probe (Stage 6).
- **ASGI** is Python's Servlet API: one `async def app(scope, receive, send)` contract. Uvicorn is the Tomcat, Starlette the `DispatcherServlet`, FastAPI the Spring MVC layer on top.
- **Scaling:** because of the GIL, one Python process effectively uses one CPU core for Python code. More cores means more processes (`--workers` or more containers).
- **PowerShell tip:** use `curl.exe`, because plain `curl` is an alias for `Invoke-WebRequest`.

## Stage 1: Domain models and API without a database (completed 2026-11-20)

- **Decimal vs float:** float is Java's `double` and can't hold 0.1 exactly. `Decimal` is `BigDecimal`. Always build it from a string: `Decimal("0.1")`, never `Decimal(0.1)`. Money stays `Decimal`; only the VaR maths (Stage 10) uses floats.
- **Pydantic models** are DTOs and Bean Validation in one step. If the object exists, it's valid. All errors are reported at once.
- **Reusable types** (`Symbol = Annotated[str, ...]`) are like a custom `@Symbol` constraint: one rule, used everywhere.
- **`BeforeValidator`** runs on raw input before the checks. I needed it because `pattern` checks the raw value, not the stripped/uppercased one. Lesson: test validation order, don't assume.
- **Create vs Read models:** Create forbids unknown fields (catches client typos), Read doesn't. Decimals go out as JSON strings so clients don't lose precision.
- **`Depends`** is `@Autowired`: a route declares `store: StoreDep` and FastAPI passes it in. Tests will swap it with `dependency_overrides` (like `@MockBean`).
- **`async def` + shared state:** no race in check-then-insert because there's no `await` in between and it all runs on one thread. With `def` routes (thread pool) I'd need a lock.
- **Errors:** the store raises `NotFoundError`/`ConflictError` (no HTTP knowledge); `error_handlers.py` maps them to 404/409 with one JSON shape. That's `@ControllerAdvice`. Also covers 422, unknown paths, 405 and crashes (500 hides internals).
- **In-memory data** is lost on every reload and isn't shared between worker processes: the database fixes this in Stage 2.

## Parked for later stages

- GIL in depth: CPU-bound vs I/O-bound work, and its effect on the web server (Stage 10).
- How many Uvicorn workers to run against CPU cores and memory, and checking with a load test (Stage 6), then replicas vs workers in Kubernetes (Stage 7).
- Deploying the app (Stage 13).
