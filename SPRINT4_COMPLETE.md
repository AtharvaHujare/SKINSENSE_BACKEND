# SkinSense AI - Sprint 4 Upload Pipeline Completion

This document details the completed **Sprint 4 Skin Lesion Upload & Storage Pipeline** for **SkinSense AI**, covering architectural design, workflow stages, error handling, curl testing examples, error codes, and future ML integration hooks.

---

## 1. System Architecture & Upload Pipeline

The upload pipeline enforces a clean **Layered Clean Architecture**:

```text
HTTP Client Request (multipart/form-data)
       │
       ▼
┌────────────────────────────────────────────────────────┐
│  API Layer (app/api/analysis.py)                       │
│  - JWT Bearer Authentication (get_current_active_user) │
│  - RBAC Role Authorization (RoleChecker(["PATIENT"]))  │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────┐
│  Service Layer (app/services/analysis_service.py)      │
│  1. Image Validation (validate_image_file)             │
│     - MIME type, extension, empty file, 10MB limit     │
│  2. Patient Profile Resolution                         │
│  3. Asynchronous Storage (save_uploaded_image)         │
│     - Saves to uploads/patients/{patient_id}/{uuid}    │
│  4. Database Persistence (analysis_repository)         │
│  5. Disk Rollback Cleanup (On DB failure)              │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────┐
│  Data Layer (app/repositories/analysis_repository.py)  │
│  - Inserts Analysis row into PostgreSQL (status="PENDING")│
└────────────────────────────────────────────────────────┘
```

---

## 2. Component Directory Responsibilities

| Component | File Path | Responsibility |
| :--- | :--- | :--- |
| **API Endpoint** | [app/api/analysis.py](file:///e:/skin-ai-backend/backend/app/api/analysis.py) | Exposes `POST /analysis/upload`, handles OpenAPI docs, enforces JWT and `PATIENT` RBAC. |
| **Service Layer** | [app/services/analysis_service.py](file:///e:/skin-ai-backend/backend/app/services/analysis_service.py) | Orchestrates validation, disk storage, database creation, and rollback file cleanup. |
| **Repository Layer**| [app/repositories/analysis_repository.py](file:///e:/skin-ai-backend/backend/app/repositories/analysis_repository.py) | Executes async PostgreSQL queries for `Analysis` ORM entities. |
| **Validator Utility**| [app/utils/file_validator.py](file:///e:/skin-ai-backend/backend/app/utils/file_validator.py) | Checks extension (`.jpg`, `.jpeg`, `.png`, `.webp`), MIME type, empty payload, and 10MB limit. |
| **Storage Utility** | [app/utils/file_storage.py](file:///e:/skin-ai-backend/backend/app/utils/file_storage.py) | Asynchronously saves files to `uploads/patients/{patient_id}/{uuid}.{ext}` via threadpool. |

---

## 3. End-to-End Checklist

- [x] **JWT Authentication**: Rejects requests lacking a valid Bearer token (`401 Unauthorized`).
- [x] **Role Authorization**: Restricts access strictly to users with role `PATIENT` (`403 Forbidden`).
- [x] **Image Format Validation**: Checks `.jpg`, `.jpeg`, `.png`, `.webp` extensions and MIME types (`400 Bad Request` / `415 Unsupported Media Type`).
- [x] **File Size Boundaries**: Enforces max size limit of 10 MB and rejects empty files (`413 Payload Too Large` / `400 Bad Request`).
- [x] **Asynchronous Storage**: Writes files to disk using `asyncio.to_thread` to prevent thread blocking.
- [x] **Database Persistence**: Creates an `Analysis` record in PostgreSQL with initial `status="PENDING"`.
- [x] **Rollback Guarantee**: Automatically deletes newly created disk files if the database transaction fails.

---

## 4. Testing & cURL Examples

### Step 1: Start Backend Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Step 2: Login as Patient User to Obtain Access Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
           "email": "patient1@example.com",
           "password": "SecurePassword123!"
         }'
```
*Save the returned `access_token`.*

---

### Step 3: Execute Lesion Upload cURL
```bash
curl -X POST "http://localhost:8000/analysis/upload" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
     -F "file=@/path/to/lesion_sample.jpg;type=image/jpeg" \
     -F "lesion_body_location=Left Forearm"
```

---

## 5. Expected API Responses

### Success Response (`202 Accepted`)
```json
{
  "analysis_id": "7f8c9d21-4a12-4b89-a213-918237192834",
  "status": "PENDING",
  "message": "Analysis created successfully.",
  "image_url": "uploads/patients/5a2d-128b/8f4c2e11a2b34.jpg",
  "created_at": "2026-08-01T22:58:31.123456Z"
}
```

### Error Responses

#### 1. `400 Bad Request` (Invalid Extension / Empty File)
```json
{
  "detail": "Invalid file extension '.pdf'. Allowed extensions are: jpeg, jpg, png, webp"
}
```

#### 2. `401 Unauthorized` (Missing or Expired Token)
```json
{
  "detail": "Could not validate credentials"
}
```

#### 3. `403 Forbidden` (Unauthorized Role - e.g. Doctor User)
```json
{
  "detail": "User role 'DOCTOR' is not authorized to perform this operation"
}
```

#### 4. `413 Payload Too Large` (Exceeds 10 MB Limit)
```json
{
  "detail": "File size (12.45 MB) exceeds maximum allowed limit of 10 MB."
}
```

#### 5. `415 Unsupported Media Type` (Disallowed MIME Type)
```json
{
  "detail": "Unsupported file content type 'application/pdf'. Allowed MIME types are: image/jpeg, image/jpg, image/png, image/webp"
}
```

#### 6. `500 Internal Server Error` (Database Failure / Storage Exception)
```json
{
  "detail": "Failed to persist analysis record in database."
}
```

---

## 6. Future Machine Learning (ML) Integration Point

In **Sprint 5**, the AI Model Inference Pipeline will connect directly to this upload workflow:

```text
PostgreSQL Analysis Record Created (status="PENDING")
                     │
                     ▼
  Dispatch Background Job / Celery / Async Task
  Parameters: (analysis_id, image_url)
                     │
                     ▼
  AI Inference Pipeline (app/ai/inference.py)
  1. Load PyTorch / ONNX model weights from trained_models/
  2. Preprocess image tensor (Resize, DullRazor hair removal, Color norm)
  3. Predict diagnostic class & confidence probabilities
  4. Generate Grad-CAM heatmap overlay image
  5. Store Prediction row in database & update Analysis status -> "COMPLETED"
```
