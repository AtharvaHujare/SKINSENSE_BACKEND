# SkinSense AI - Backend Foundation

SkinSense AI is a production-grade backend service built with [FastAPI](https://fastapi.tiangolo.com/) for an AI-powered Skin Cancer Detection System.

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/          # API Controllers & Route definitions (Health, Scans, Reports)
│   ├── auth/         # Reserved for Authentication & Authorization logic
│   ├── core/         # Cross-cutting concerns (Security, Logging, Constants)
│   ├── database/     # DB connection engine, session management
│   ├── models/       # Database ORM Entity Models (SQLAlchemy / SQLModel)
│   ├── schemas/      # Pydantic schemas for data validation and serialization
│   ├── repositories/ # Data Access Layer abstraction (DAOs)
│   ├── services/     # Business logic & domain service orchestrators
│   ├── ai/           # AI inference engine, preprocessing, & CV pipelines
│   ├── middleware/   # Custom ASGI middlewares (CORS, Rate Limiting, Logging)
│   ├── utils/        # Generic helper utilities & stateless functions
│   ├── workers/      # Background task queue handlers (Celery/Redis workers)
│   ├── config.py     # Centralized application settings (Pydantic Settings)
│   ├── main.py       # FastAPI application factory & startup entrypoint
│   └── __init__.py   # App package marker
│
├── uploads/          # Directory for uploaded skin lesion images
├── reports/          # Directory for generated PDF diagnostic reports
├── trained_models/   # Directory for AI model weights and weights configurations
├── tests/            # Test suite (unit, integration, and endpoint tests)
│
├── .env.example      # Template for environment configuration variables
├── .gitignore        # Git ignore rules for Python & local build outputs
├── Dockerfile        # Containerization deployment specification
├── docker-compose.yml# Multi-container orchestration definitions (Commented)
├── requirements.txt  # Python package dependency specifications
└── README.md         # Backend foundation overview documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Virtualenv / Conda

### Running Locally

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

## 🔍 Health & Verification Endpoints

- **Root Status**: `GET /`
  ```json
  {
    "message": "SkinSense AI Backend Running"
  }
  ```

- **System Health Check**: `GET /health`
  ```json
  {
    "status": "healthy"
  }
  ```

- **Interactive API Documentation**:
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`

---

## 🧪 Testing

Run pytest to execute the unit test suite:
```bash
pytest
```
