# SkinSense AI - Sprint 3 Authentication & Authorization Module

This document provides a comprehensive guide to the **Sprint 3 Authentication & Authorization System** implemented for **SkinSense AI**.

---

## 📁 Implemented File Architecture

```text
backend/app/
├── auth/
│   ├── dependencies.py    # get_current_user, get_current_active_user, RoleChecker(RBAC)
│   ├── hashing.py         # Passlib bcrypt password hashing and verification
│   ├── jwt.py             # JWT Access (30m) & Refresh (7d) token creation & verification
│   ├── routes.py          # FastAPI endpoints (/auth/register, /auth/login, /auth/refresh, /auth/logout, /auth/me)
│   ├── services.py        # Registration, login, token rotation, and revocation service logic
│   └── __init__.py
├── repositories/
│   └── auth_repository.py # Database operations for User, Patient, Doctor, and RefreshToken
├── schemas/
│   ├── auth.py            # Pydantic schemas (UserRegisterRequest, UserLoginRequest, TokenResponse, etc.)
│   └── __init__.py
├── config.py              # Added SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
└── main.py                # Mounted auth_router into FastAPI application
```

---

## 🔒 Security Specifications

- **Password Hashing**: Utilizes `passlib` with `bcrypt` (never stores plain-text passwords).
- **JWT Architecture**:
  - **Access Token**: Signed with `HS256`, 30-minute expiration, contains user UUID `sub` and `role`.
  - **Refresh Token**: Signed with `HS256`, 7-day expiration.
- **Refresh Token Storage & Rotation**:
  - Raw refresh tokens are issued to clients; cryptographic SHA-256 hashes of the tokens are saved in the `refresh_tokens` database table.
  - On `/auth/refresh`, the old refresh token is revoked and deleted, and a new token pair is issued (**Token Rotation**).
- **Role-Based Access Control (RBAC)**: Supported via `RoleChecker(["PATIENT", "DOCTOR", "ADMIN"])`.

---

## 🚀 Swagger UI Interactive Testing Guide

1. Start the FastAPI development server:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. Open your browser and navigate to Interactive API Docs:
   `http://localhost:8000/docs`

### Test 1: User Registration
- Open `POST /auth/register`.
- Click **Try it out**.
- Submit sample JSON payload:
  ```json
  {
    "email": "patient1@example.com",
    "password": "SecurePassword123!",
    "role": "PATIENT",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```
- **Expected Response**: `201 Created` returning user UUID, email, role, and active status.

### Test 2: User Login
- Open `POST /auth/login`.
- Submit JSON login credentials:
  ```json
  {
    "email": "patient1@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Expected Response**: `200 OK` returning:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
    "token_type": "bearer"
  }
  ```

### Test 3: Authenticate Swagger UI
- Copy the `access_token` string from the login response.
- Scroll to the top of Swagger UI and click the green **Authorize** button.
- Paste the token into the Value box and click **Authorize**.

### Test 4: Access Protected Profile Endpoint
- Open `GET /auth/me`.
- Click **Try it out** -> **Execute**.
- **Expected Response**: `200 OK` returning authenticated user profile details.

### Test 5: Token Refreshing & Rotation
- Open `POST /auth/refresh`.
- Submit payload with raw `refresh_token`:
  ```json
  {
    "refresh_token": "<YOUR_REFRESH_TOKEN>"
  }
  ```
- **Expected Response**: `200 OK` returning a brand new token pair (old token is revoked).

### Test 6: User Logout
- Open `POST /auth/logout`.
- Submit payload with `refresh_token`.
- **Expected Response**: `200 OK` with `{"message": "Successfully logged out"}`.
