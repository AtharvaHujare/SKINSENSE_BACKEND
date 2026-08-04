# SkinSense AI - Sprint 2 Database Infrastructure Completion

This document details the completed Sprint 2 database infrastructure tasks for **SkinSense AI**, including configuration updates, connection verification, Alembic setup, initial migrations, and application startup integration.

---

## 1. Summary of What Changed & Why

### Configuration & Connection Verification (Tasks 1 & 2)
- **Dynamic Connection Strings**: Updated `app/config.py` to automatically construct `DATABASE_URL` (`postgresql+asyncpg://...`) using `pydantic-settings` from individual `.env` fields (`DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`).
- **Connection Health Check**: Implemented `verify_database_connection()` in `app/database/database.py` that executes a ping (`SELECT 1`) on application startup.
- **FastAPI Lifespan Integration**: Updated `app/main.py` using FastAPI's `@asynccontextmanager` lifespan handler to verify database connectivity during application boot.
- **Prints Confirmation**: Prints `✅ Database Connected Successfully` when PostgreSQL is online and accessible, or outputs an error message on failure.

### Alembic Migration Setup (Tasks 3 & 4)
- **Alembic Initialization**: Created `alembic.ini`, `alembic/env.py`, and `alembic/script.py.mako`.
- **Async Metadata Integration**: Configured `alembic/env.py` to import `Base.metadata` and parse `settings.DATABASE_URL` using `async_engine_from_config` for non-blocking migrations.
- **Initial Migration (`0001_initial_schema.py`)**: Authored the baseline database migration defining DDL for `users`, `patients`, and `doctors` tables with UUID primary keys, foreign keys (`ON DELETE CASCADE`), indexes, and `JSONB` fields.

---

## 2. Directory Structure Changes

```text
backend/
├── alembic/
│   ├── versions/
│   │   └── 0001_initial_schema.py   # Initial migration for users, patients, doctors
│   ├── env.py                       # Async Alembic environment runner
│   └── script.py.mako               # Template for new migrations
├── alembic.ini                      # Alembic CLI configuration
├── app/
│   ├── database/
│   │   ├── database.py              # Added verify_database_connection()
│   │   ├── session.py               # Async session generator
│   │   └── __init__.py
│   ├── config.py                    # Dynamic DATABASE_URL constructor
│   └── main.py                      # Lifespan database verification hook
└── SPRINT2_COMPLETE.md              # Sprint 2 completion guide
```

---

## 3. How to Run & Verification Commands

### Step 1: Set Up Environment Variables
Ensure `.env` exists inside `backend/`:
```bash
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=skinsense_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
```

### Step 2: Apply Database Migrations
Run the initial Alembic migration to create `users`, `patients`, and `doctors` tables:
```bash
cd backend
alembic upgrade head
```

### Step 3: Start FastAPI Application
Start the uvicorn development server:
```bash
uvicorn app.main:app --reload --port 8000
```
*Look for startup logs*:
```text
INFO:     Started server process [12345]
✅ Database Connected Successfully
INFO:     Application startup complete.
```

### Step 4: Verify Database Tables in PostgreSQL
Connect via `psql` to inspect created tables:
```bash
psql -U postgres -d skinsense_db -c "\dt"
```
*Expected Output*:
```text
         List of relations
 Schema |    Name    | Type  |  Owner   
--------+------------+-------+----------
 public | alembic_version | table | postgres
 public | doctors    | table | postgres
 public | patients   | table | postgres
 public | users      | table | postgres
```

---

## 4. Common Errors & Troubleshooting

### Error 1: `ConnectionRefusedError` or `asyncpg.exceptions.CannotConnectNowError`
- **Symptom**: `❌ Database Connection Failed: [Errno 111] Connect call failed ('127.0.0.1', 5432)`
- **Cause**: PostgreSQL service is not running or incorrect host/port in `.env`.
- **Solution**:
  1. Check PostgreSQL service status (`pg_ctl status` or Windows Services).
  2. Verify `DATABASE_HOST` and `DATABASE_PORT` in `.env`.

### Error 2: `asyncpg.exceptions.InvalidPasswordError`
- **Symptom**: `❌ Database Connection Failed: password authentication failed for user "postgres"`
- **Cause**: Incorrect `DATABASE_PASSWORD` in `.env`.
- **Solution**: Update `DATABASE_PASSWORD` in `.env` with your actual local PostgreSQL password.

### Error 3: `asyncpg.exceptions.InvalidCatalogNameError`
- **Symptom**: `❌ Database Connection Failed: database "skinsense_db" does not exist`
- **Cause**: Target database has not been created yet.
- **Solution**: Run `createdb -U postgres skinsense_db` or execute `CREATE DATABASE skinsense_db;` in psql.
