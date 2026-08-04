# SkinSense AI - Sprint 5 AI Model Integration & Prediction Persistence Completion

This document details the completed **Sprint 5 AI Integration Pipeline** for **SkinSense AI**, covering the end-to-end Machine Learning lifecycle, layered backend architecture, status state machine, error handling, Swagger testing guide, cURL examples, error codes, and future integration blueprints.

---

## 1. System Architecture & Request Lifecycle

The system enforces a strict **Layered Clean Architecture**:

```text
HTTP Client Request (multipart/form-data / JSON)
       │
       ▼
┌────────────────────────────────────────────────────────┐
│  API Layer (app/api/analysis.py)                       │
│  - Bearer JWT Authentication (get_current_active_user) │
│  - Role Authorization (RoleChecker(["PATIENT"]))       │
│  - Swagger / OpenAPI Contract Declarations             │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────┐
│  Service Layer (app/services/analysis_service.py)      │
│  1. Image File Validation (validate_image_file)        │
│  2. Patient Profile Resolution                         │
│  3. Asynchronous Disk Storage (save_uploaded_image)    │
│  4. DB Analysis Record Creation (status="PENDING")     │
│  5. Pre-Inference Status Update (status="PROCESSING")  │
│  6. AI Inference Call (app.ai.predict.predict)         │
│  7. Prediction Persistence (prediction_service)        │
│  8. Post-Inference Status Update (status="COMPLETED")  │
│  9. Rollback & Fail-safe Handling (status="FAILED")    │
└──────────────┬─────────────────────────┬───────────────┘
               │                         │
               ▼                         ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│ Data Layer (app/repositories)│   │ AI Module (app/ai/predict)  │
│ - analysis_repository.py    │   │ - Preprocessing & Tensor    │
│ - prediction_repository.py  │   │ - TensorFlow Model Load     │
│ - PostgreSQL Persistence    │   │ - Grad-CAM Visual Heatmap   │
└─────────────────────────────┘   └─────────────────────────────┘
```

---

## 2. End-to-End Status Lifecycle & Workflow State Machine

The Analysis entity transitions across explicit workflow states during processing:

```text
Upload Lesion Image
        │
        ▼
Create Analysis Record ───► status = "PENDING"
        │
        ▼
Pre-Inference Transition ──► status = "PROCESSING"
        │
        ├──► [AI Inference Exception] ────────► status = "FAILED" (HTTP 500)
        │
Run AI Prediction (app.ai.predict)
        │
        ├──► [Prediction Persistence / DB Rollback Failure] ──► status = "FAILED" (HTTP 500)
        │
Save Prediction Record (prediction_service)
        │
        ▼
Post-Inference Transition ─► status = "COMPLETED" (updated_at timestamp set)
```

---

## 3. Directory & Component Responsibilities

| Component | File Path | Responsibility |
| :--- | :--- | :--- |
| **API Endpoints** | [app/api/analysis.py](file:///e:/skin-ai-backend/backend/app/api/analysis.py) | Exposes `POST /upload`, `GET /history`, `GET /{id}`, `GET /{id}/prediction`. Enforces RBAC & JWT. |
| **Analysis Service** | [app/services/analysis_service.py](file:///e:/skin-ai-backend/backend/app/services/analysis_service.py) | Orchestrates validation, disk storage, AI inference invocation, DB persistence, and status lifecycle. |
| **Prediction Service**| [app/services/prediction_service.py](file:///e:/skin-ai-backend/backend/app/services/prediction_service.py) | Business service handling prediction persistence, confidence scaling, and transaction rollbacks. |
| **Analysis Repository**| [app/repositories/analysis_repository.py](file:///e:/skin-ai-backend/backend/app/repositories/analysis_repository.py) | Data Access Object (DAO) for `Analysis` records, eager loading, and status updates. |
| **Prediction Repository**| [app/repositories/prediction_repository.py](file:///e:/skin-ai-backend/backend/app/repositories/prediction_repository.py) | Data Access Object (DAO) for `Prediction` database records. |
| **AI Inference Module**| [app/ai/predict.py](file:///e:/skin-ai-backend/backend/app/ai/predict.py) | Computer vision inference engine (Preprocessing, TensorFlow model prediction, Grad-CAM heatmap generation). |
| **Pydantic Schemas** | [app/schemas/analysis.py](file:///e:/skin-ai-backend/backend/app/schemas/analysis.py) | Request and response schema contracts (`AnalysisUploadResponse`, `AnalysisDetailResponse`, `PredictionResponse`). |

---

## 4. End-to-End Sprint 5 Verification Checklist

- [x] **AI Predict Module Integration**: Integrated `predict()` into `AnalysisService` after file storage and analysis record creation.
- [x] **Prediction Persistence**: Created `PredictionRepository` and `PredictionService` to store `analysis_id`, `predicted_class`, `confidence`, `risk_level`, and `heatmap_path` in PostgreSQL.
- [x] **Status Lifecycle Management**: Automated status transitions from `PENDING` $\rightarrow$ `PROCESSING` $\rightarrow$ `COMPLETED` (or `FAILED` on error).
- [x] **Rollback Guarantee**: In case of prediction persistence failure, transaction is rolled back while keeping the `Analysis` record marked as `FAILED`.
- [x] **Prediction Retrieval Endpoints**:
  - `GET /analysis/history`: Authenticated patient analysis history ordered newest first.
  - `GET /analysis/{analysis_id}`: Full analysis session details with status and prediction object.
  - `GET /analysis/{analysis_id}/prediction`: Dedicated prediction result query.
- [x] **Patient Privacy & Authorization**: Restricted patient access to their own analysis records while maintaining extensibility for Doctor/Admin roles.

---

## 5. Swagger UI & cURL Testing Guide

### Step 1: Start Backend Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
Open interactive Swagger UI docs: `http://localhost:8000/docs`

---

### Step 2: Login as Patient User
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

### Endpoint 1: Upload Lesion Image & Trigger AI Pipeline (`POST /analysis/upload`)
```bash
curl -X POST "http://localhost:8000/analysis/upload" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
     -F "file=@/path/to/lesion_sample.jpg;type=image/jpeg" \
     -F "lesion_body_location=Left Forearm"
```

#### Success Response (`202 Accepted`)
```json
{
  "analysis_id": "7f8c9d21-4a12-4b89-a213-918237192834",
  "prediction": "mel",
  "confidence": 94.52,
  "risk_level": "High",
  "heatmap_path": "uploads/heatmaps/7f8c9d21-4a12-4b89-a213-918237192834_gradcam.png"
}
```

---

### Endpoint 2: Get Patient Analysis History (`GET /analysis/history`)
```bash
curl -X GET "http://localhost:8000/analysis/history" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

#### Success Response (`200 OK`)
```json
[
  {
    "analysis_id": "7f8c9d21-4a12-4b89-a213-918237192834",
    "patient_id": "5a2d128b-3c41-419b-88b1-128491827412",
    "image_url": "uploads/patients/5a2d128b-3c41-419b-88b1-128491827412/8f4c2e11.jpg",
    "lesion_body_location": "Left Forearm",
    "status": "COMPLETED",
    "created_at": "2026-08-04T22:10:00.000000Z",
    "updated_at": "2026-08-04T22:10:02.500000Z",
    "prediction": {
      "predicted_class": "mel",
      "confidence": 94.52,
      "risk_level": "High",
      "heatmap_path": "uploads/heatmaps/7f8c9d21-4a12-4b89-a213-918237192834_gradcam.png"
    }
  }
]
```

---

### Endpoint 3: Get Single Analysis Information (`GET /analysis/{analysis_id}`)
```bash
curl -X GET "http://localhost:8000/analysis/7f8c9d21-4a12-4b89-a213-918237192834" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

#### Success Response (`200 OK`)
```json
{
  "analysis_id": "7f8c9d21-4a12-4b89-a213-918237192834",
  "patient_id": "5a2d128b-3c41-419b-88b1-128491827412",
  "image_url": "uploads/patients/5a2d128b-3c41-419b-88b1-128491827412/8f4c2e11.jpg",
  "lesion_body_location": "Left Forearm",
  "status": "COMPLETED",
  "created_at": "2026-08-04T22:10:00.000000Z",
  "updated_at": "2026-08-04T22:10:02.500000Z",
  "prediction": {
    "predicted_class": "mel",
    "confidence": 94.52,
    "risk_level": "High",
    "heatmap_path": "uploads/heatmaps/7f8c9d21-4a12-4b89-a213-918237192834_gradcam.png"
  }
}
```

---

### Endpoint 4: Get Prediction Details (`GET /analysis/{analysis_id}/prediction`)
```bash
curl -X GET "http://localhost:8000/analysis/7f8c9d21-4a12-4b89-a213-918237192834/prediction" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

#### Success Response (`200 OK`)
```json
{
  "predicted_class": "mel",
  "confidence": 94.52,
  "risk_level": "High",
  "heatmap_path": "uploads/heatmaps/7f8c9d21-4a12-4b89-a213-918237192834_gradcam.png"
}
```

---

## 6. HTTP Error Code Reference Table

| Code | Condition | JSON Response Example |
| :--- | :--- | :--- |
| **`400 Bad Request`** | Invalid file extension or empty file upload | `{"detail": "Invalid file extension '.pdf'. Allowed extensions are: jpeg, jpg, png, webp"}` |
| **`401 Unauthorized`** | Missing or expired JWT Bearer token | `{"detail": "Could not validate credentials"}` |
| **`403 Forbidden`** | Unauthorized role or accessing another patient's analysis | `{"detail": "Access denied. You do not have permission to view this analysis."}` |
| **`404 Not Found`** | Requested analysis session ID or prediction does not exist | `{"detail": "Analysis session not found."}` |
| **`413 Payload Too Large`** | Image file size exceeds 10 MB limit | `{"detail": "File size (12.45 MB) exceeds maximum allowed limit of 10 MB."}` |
| **`415 Unsupported Media Type`** | Disallowed MIME content-type | `{"detail": "Unsupported file content type 'application/pdf'."}` |
| **`500 Internal Server Error`** | AI model inference error or prediction DB persistence failure | `{"detail": "AI prediction inference failed."}` |

---

## 7. Future Integration Roadmap

### 1. Sprint 6: PDF Report Generation Subsystem
- **Trigger**: When an `Analysis` transitions to `COMPLETED`, dispatch background report generation job (`app/workers/report_worker.py`).
- **Rendering**: Generate printable PDF diagnostic report using `ReportLab` or `Jinja2` HTML-to-PDF templates.
- **Persistence**: Store PDF report row in `reports` database table with signed download tokens.

### 2. Sprint 7: Doctor Dashboard & Physician Review Subsystem
- **Assignment**: Route `COMPLETED` high-risk analyses (`risk_level == "High"`) to assigned dermatologists (`doctors.id`).
- **Doctor Endpoints**:
  - `GET /doctor/queue`: View pending patient analysis queue.
  - `POST /doctor/review`: Submit physician diagnostic notes and confirm/modify risk severity score.
- **Appointments Integration**: Schedule follow-up tele-dermatology consultations for urgent high-risk cases.

---

## 8. Sprint 5 Final Declaration

✅ **Sprint 5 AI Model Integration & Prediction Persistence Module is complete, fully verified, and declared PRODUCTION-READY.**
