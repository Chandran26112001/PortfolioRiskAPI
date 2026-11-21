# Portfolio Risk API: learning project

## Why this project exists

Chandran is a backend engineer with about 3.5 years of production experience in Java, Spring Boot, Oracle SQL, Angular and AWS. He is moving to a quant risk analysis team whose platform is built on Python and FastAPI, with Oracle as the database, and whose applications run on Docker and Kubernetes. He knows Oracle from Java; using it from Python is new.

The goal is **not** just a working app. The goal is that Chandran can build, explain and defend every part of a production-style FastAPI service, end to end, so he works confidently in the new team from day one.

## How to work with Chandran (read this first)

- **Build in stages, one stage per sitting.** Never build the whole project at once. Finish a stage, make sure it runs, then stop and wait.
- **Chandran runs every command himself.** Give him the exact command, explain what it does, and wait for him to confirm the result before moving on.
- **Explain the why, not only the what.** For each new concept, say why it's done that way and what the common alternatives are.
- **Map to Spring Boot where it helps.** Example: FastAPI `Depends` ≈ Spring dependency injection; Pydantic models ≈ DTOs with Bean Validation; Alembic ≈ Flyway/Liquibase; routers ≈ `@RestController` classes.
- **End each stage with "What a reviewer would ask":** 3 to 5 questions a senior engineer would ask about that stage's code, with short answers.
- **Keep a learning log** in `NOTES.md`: for each stage, a few lines on what was learned, in Chandran's terms.
- **He is on Windows.** Give PowerShell-friendly commands. Docker is installed on his machine.
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
| Database | Oracle Database Free in Docker from stage 2, for development and tests, via python-oracledb (thin mode) |
| Auth | OAuth2 / OpenID Connect with JWT and scopes; Keycloak in Docker as a local stand-in for enterprise SSO |
| Maths | NumPy, pandas, JupyterLab for prototyping |
| Messaging | Kafka |
| Tests | pytest, FastAPI TestClient / httpx, dependency overrides |
| Quality | ruff (lint and format) |
| Packaging and deploy | Docker, docker compose, Kubernetes (Docker Desktop locally, Kustomize for config), GitHub Actions (plus a Jenkinsfile for comparison), Terraform, AWS |

## Stage plan

0. **Setup:** uv project, folder layout, ruff, first endpoint, `/docs` and `/health`. Explain ASGI and Uvicorn.
1. **Domain models and API without a database:** Pydantic models for securities, funds, positions and prices; routers; validation; HTTP status codes; error handling; Decimal vs float.
2. **Database on Oracle:** run Oracle Database Free in Docker with docker compose; SQLAlchemy 2.0 models over python-oracledb (thin mode); a session provided through a `yield` dependency; a repository layer replacing the in-memory store; Alembic migrations; pagination; constraints (primary key, foreign key, unique, check) and indexes. Explain bind variables and how Oracle types map to Python (`NUMBER` to `Decimal`, `DATE`, identity columns).
3. **Valuation endpoints:** market value, weights and sector exposure. Compare doing the aggregation in SQL vs pandas; show the N+1 query problem and how to avoid it; read the Oracle execution plan of the valuation query. Add data-quality checks (positions with no price, weights that don't sum to 100%).
4. **Testing:** pytest fixtures, tests running against Oracle in Docker (a disposable test schema), dependency overrides, testing validation errors, coverage. Explain why tests use Oracle and not SQLite (dialect differences, such as Oracle treating an empty string as NULL).
5. **Flask and Django comparison (short):** rebuild a few endpoints in Flask to see a WSGI framework next to FastAPI, and compare Django's ORM with SQLAlchemy, so either looks familiar on the team. Throwaway code, kept out of the main app.
6. **Containerise:** multi-stage Dockerfile, docker compose (API + Oracle), configuration through environment variables with pydantic-settings, liveness and readiness checks. Worker processes: how many Uvicorn workers to run (`uvicorn --workers N` vs one process per container), sizing against CPU cores and memory, and checking the choice with a simple load test.
7. **Kubernetes (local, Docker Desktop):** Deployment, Service, ConfigMap and Secret, liveness and readiness probes, resource requests and limits, rolling updates, scaling replicas vs Uvicorn workers, Kustomize for per-environment config. Oracle stays outside the app's Deployment, as a production database would be managed separately.
8. **Auth and SSO:** first learn the mechanics with the OAuth2 password flow, our own JWTs and password hashing; then switch to real SSO with Keycloak in Docker as the identity provider (OpenID Connect, validating tokens against its public keys). Scopes such as `positions:write` and `risk:read`, protecting routes with dependencies, and client credentials for service-to-service calls. Secrets come from Kubernetes Secrets.
9. **Batch price load:** a command-line job that loads a prices CSV into the database idempotently (upsert with Oracle `MERGE`, bulk writes with `executemany`), validates data (missing or negative prices, unknown securities), calls a PL/SQL procedure from Python (for example, a post-load check), logs a summary with a run ID, and can be safely re-run. Runs as a Kubernetes CronJob.
10. **Risk engine and async jobs:** prototype VaR and ES in a JupyterLab notebook against the Oracle data first (how quants work), then move the code into the service. `POST /risk-runs` returns a run ID immediately; the calculation runs in a `ProcessPoolExecutor`; `GET /risk-runs/{id}` returns status and results. Explain the GIL in depth (what it is, why it matters for CPU-bound vs I/O-bound work, how it affects the web server as well as the risk engine), why processes and not threads, and limiting concurrency with a bounded pool or semaphore. Size the pool from the container's CPU limit, not the host's core count.
11. **Event-driven with Kafka:** run Kafka in Docker; the batch job publishes a "prices loaded" event and a consumer starts a risk run. Cover at-least-once delivery, idempotent consumers and a dead-letter topic.
12. **CI:** GitHub Actions running ruff, tests against Oracle, and an image build on every push. Write a Jenkinsfile doing the same steps, to compare the two.
13. **Deploy and observe:** build the AWS infrastructure with Terraform, so `terraform destroy` removes it all; deploy (compare EKS and ECS); structured logging, basic metrics. **Before creating anything on AWS that can cost money, tell Chandran the expected cost and get his OK, and show him how to delete it afterwards.**

Out of scope by Chandran's choice: a branch and pull request per stage, and a TypeScript client or frontend.

## Definition of done for each stage

- The code runs, and Chandran has run it himself.
- Tests pass (from stage 4 onwards, every stage adds tests).
- `NOTES.md` is updated.
- The "What a reviewer would ask" questions have been covered.
