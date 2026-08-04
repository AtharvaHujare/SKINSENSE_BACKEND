# SkinSense AI - Database Implementation (Sprint 1)

This document details the Sprint 1 database layer implementation using **SQLAlchemy 2.0** and **PostgreSQL**.

---

## 1. Overview of Implemented Modules

| File Path | Description |
| :--- | :--- |
| [base.py](file:///e:/skin-ai-backend/backend/app/models/base.py) | Declarative Base class (`Base`) and reusable `TimestampMixin` (`created_at`, `updated_at`). |
| [user.py](file:///e:/skin-ai-backend/backend/app/models/user.py) | `User` entity model storing credentials, RBAC role, account status, and 1-to-1 relationships to profiles. |
| [patient.py](file:///e:/skin-ai-backend/backend/app/models/patient.py) | `Patient` entity model storing DOB, Fitzpatrick skin type classification, and JSONB medical history. |
| [doctor.py](file:///e:/skin-ai-backend/backend/app/models/doctor.py) | `Doctor` entity model storing medical license number, specialization, clinic affiliation, and admin approval status. |
| [__init__.py](file:///e:/skin-ai-backend/backend/app/models/__init__.py) | Package initializers exporting clean ORM symbol imports. |
| [database.py](file:///e:/skin-ai-backend/backend/app/database/database.py) | Asynchronous SQLAlchemy engine setup (`create_async_engine`) and session factory (`AsyncSessionLocal`). |
| [session.py](file:///e:/skin-ai-backend/backend/app/database/session.py) | Asynchronous `get_db()` session generator dependency for FastAPI scope management. |
| [__init__.py](file:///e:/skin-ai-backend/backend/app/database/__init__.py) | Database infrastructure package exports. |

---

## 2. Technical Specifications & Design Choices

### SQLAlchemy 2.0 Mapped Syntax
All models leverage modern SQLAlchemy 2.0 type-annotated declarations using `Mapped[...]` and `mapped_column(...)`, providing complete static typing guarantees and runtime field validation.

```python
id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4
)
```

### UUID Primary Keys
All tables utilize native PostgreSQL `UUID` primary keys generated via Python `uuid.uuid4` to prevent sequential ID enumeration security vulnerabilities.

### Bidirectional One-to-One Relationships
- `User` to `Patient`: `User.patient` <-> `Patient.user` with `cascade="all, delete-orphan"`.
- `User` to `Doctor`: `User.doctor` <-> `Doctor.user` with `cascade="all, delete-orphan"`.

### Asynchronous Session Management
Connection handling leverages `asyncpg` via `create_async_engine(...)` and `async_sessionmaker(...)`, offering non-blocking database queries suitable for high-concurrency FastAPI operations.
