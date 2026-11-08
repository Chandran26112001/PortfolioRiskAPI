# Portfolio Risk API: learning project

## Why this project exists

Chandran is a backend engineer with about 3.5 years of production experience in Java, Spring Boot, Oracle SQL, Angular and AWS. He is moving to a quant risk analysis team whose platform is built on Python and FastAPI, with Oracle as the database.

The goal is **not** just a working app. The goal is that Chandran can build, explain and defend every part of a production-style FastAPI service, end to end, so he works confidently in the new team from day one.

## How to work with Chandran (read this first)

- **Build in stages, one stage per sitting.** Never build the whole project at once. Finish a stage, make sure it runs, then stop and wait.
- **Chandran runs every command himself.** Give him the exact command, explain what it does, and wait for him to confirm the result before moving on.
- **Explain the why, not only the what.** For each new concept, say why it's done that way and what the common alternatives are.
- **Map to Spring Boot where it helps.** Example: FastAPI `Depends` ≈ Spring dependency injection; Pydantic models ≈ DTOs with Bean Validation; Alembic ≈ Flyway/Liquibase; routers ≈ `@RestController` classes.
- **End each stage with "What a reviewer would ask":** 3 to 5 questions a senior engineer would ask about that stage's code, with short answers.
- **Keep a learning log** in `NOTES.md`: for each stage, a few lines on what was learned, in Chandran's terms.
- **He is on Windows.** Give PowerShell-friendly commands.
- Keep code idiomatic and production-style: type hints everywhere, small functions, clear names, no clever tricks.

## What the service does

A small version of a risk platform:

- Stores **funds**, their **positions** (fund, security, quantity, as-of date) and **securities** (symbol, name, sector, currency).
- Loads **daily prices** through a batch job.
- Returns **market value**, **weights** and **sector exposure** per fund.
- Runs **historical VaR and Expected Shortfall** as an asynchronous job: submit a run, get a run ID, poll for the result.

Domain notes:

- Market value = quantity × price. Weight = position market value ÷ fund market value.
- Historical VaR (99%, 1-day): apply each of the last N days' price returns to today's positions, giving N possible P&Ls; the loss at the worst 1% is the VaR. Expected Shortfall = the average loss beyond VaR.
- Use `Decimal` for money that must be exact (stored amounts, reported market values). Use NumPy `float64` inside the VaR calculation (it's a statistical estimate, and speed matters). Explain this choice when it comes up.

## Tech choices

| Area | Choice |
| --- | --- |
| Language | Python 3.12+ |
| Package and env manager | uv |
| Web framework | FastAPI, Pydantic v2, pydantic-settings for config |
| Database access | SQLAlchemy 2.0 (typed ORM) + Alembic migrations |
| Database | SQLite for early stages and tests; Oracle Database Free in Docker from stage 8, via python-oracledb (thin mode) |
| Auth | OAuth2 password flow with JWT and scopes (simulating what enterprise SSO would provide) |
| Maths | NumPy, pandas |
| Tests | pytest, FastAPI TestClient / httpx, dependency overrides |
| Quality | ruff (lint and format) |
| Packaging and deploy | Docker, docker compose, GitHub Actions, AWS |

## Stage plan

0. **Setup:** uv project, folder layout, ruff, first endpoint, `/docs` and `/health`. Explain ASGI and Uvicorn.
1. **Domain models and API without a database:** Pydantic models for securities, funds, positions and prices; routers; validation; HTTP status codes; error handling; Decimal vs float.
2. **Database:** SQLAlchemy models, a session provided through a `yield` dependency, a repository layer, Alembic migrations, pagination.
3. **Valuation endpoints:** market value, weights and sector exposure. Compare doing the aggregation in SQL vs pandas; show the N+1 query problem and how to avoid it.
4. **Testing:** pytest fixtures, a test database, dependency overrides, testing validation errors, coverage.
5. **Auth:** OAuth2 + JWT, scopes such as `positions:write` and `risk:read`, protecting routes with dependencies, password hashing.
6. **Batch price load:** a command-line job that loads a prices CSV into the database idempotently (upsert), validates data (missing or negative prices, unknown securities), logs a summary with a run ID, and can be safely re-run.
7. **Risk engine and async jobs:** VaR and ES with NumPy; `POST /risk-runs` returns a run ID immediately; the calculation runs in a `ProcessPoolExecutor`; `GET /risk-runs/{id}` returns status and results. Explain the GIL, why processes and not threads, and limiting concurrency with a bounded pool or semaphore.
8. **Oracle:** run Oracle Database Free in Docker, switch the connection, explain bind variables, bulk fetches and reading an execution plan.
9. **Containerise:** multi-stage Dockerfile, docker compose (API + Oracle), configuration through environment variables, health checks.
10. **CI:** GitHub Actions running ruff, tests and an image build on every push.
11. **Deploy and observe:** deploy to AWS, structured logging, basic metrics. **Before creating anything on AWS that can cost money, tell Chandran the expected cost and get his OK, and show him how to delete it afterwards.**

Optional extra: publish a "prices loaded" event to Kafka that triggers a risk run, to show event-driven design.

## Definition of done for each stage

- The code runs, and Chandran has run it himself.
- Tests pass (from stage 4 onwards, every stage adds tests).
- `NOTES.md` is updated.
- The "What a reviewer would ask" questions have been covered.
