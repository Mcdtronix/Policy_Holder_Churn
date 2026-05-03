# Nyaradzo Insurance Churn Prediction System

An end-to-end insurance operations platform with machine learning-driven churn prediction.

This repository contains:
- A Django REST API backend for customer, policy, claims, payment, analytics, and authentication workflows.
- A React + TypeScript frontend for operational dashboards and churn intelligence.
- ML integration for churn scoring with a rule-based fallback when model artifacts are unavailable.

## Key Features

- JWT authentication with email-based login and role-aware user payloads.
- Policyholder management and policy registration workflows.
- Claims filing and claims management pages.
- Payment updates and matured policy tracking.
- Churn analytics dashboards and individual churn prediction views.
- Batch and single-customer prediction support through API endpoints.
- Health endpoints for service monitoring.

## Tech Stack

- Backend: Django, Django REST Framework, SimpleJWT, django-filter, CORS headers
- Frontend: React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui, React Query
- ML: scikit-learn, xgboost, pandas, numpy, joblib
- Database: SQLite (default for development)

## Repository Structure

```text
Insuarance_Churn_Prediction/
├── Backend/                      # Django API + ML integration
│   ├── churn/
│   ├── ml_engine/
│   ├── manage.py
│   └── requirements.txt
├── Frontend/                     # React app
│   ├── src/
│   └── package.json
├── nyaradzo_churn_dataset_5000_customers.csv
└── README.md
```

## Quick Start

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Git

## 1. Clone Repository

```bash
git clone <your-repo-url>
cd Insuarance_Churn_Prediction
```

## 2. Backend Setup

```bash
cd Backend
python -m venv ../env
source ../env/bin/activate   # Windows: ..\env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend runs at:
- http://127.0.0.1:8000

### Optional: Load Sample Customers

From the `Backend/` directory:

```bash
python manage.py import_customers ../nyaradzo_churn_dataset_5000_customers.csv
```

## 3. Frontend Setup

Open a second terminal at project root:

```bash
cd Frontend
npm install
npm run dev
```

Frontend runs at:
- http://127.0.0.1:5173

## Environment Variables

### Frontend

Create `Frontend/.env` if needed:

```env
VITE_API_URL=http://127.0.0.1:8000
```

### Backend (optional, recommended)

Set environment variables before running production-like environments:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG` (set to `False` in production)
- `ALLOWED_HOSTS` (space-separated values)

## API Overview

Base API path:
- `/api/v1/`

Common endpoints:
- `GET /api/v1/customers/`
- `GET /api/v1/policies/`
- `GET /api/v1/claims/`
- `GET /api/v1/payments/`
- `GET /api/v1/dashboard/`
- `GET /api/v1/analytics/`
- `GET /api/v1/health/`

Authentication endpoints:
- `POST /api/token/`
- `POST /api/token/refresh/`
- `POST /api/logout/`
- `GET /api/auth/health/`
- `GET /api/token/verify/`

OpenAPI / Swagger docs:
- `GET /api/schema/`
- `GET /api/docs/`
- `GET /api/docs/redoc/`

## Machine Learning Integration

The backend supports two prediction modes:
- ML model mode (when artifacts are available)
- Rule-based fallback mode (default fallback)

To enable ML model mode, place artifacts in:

```text
Backend/ml_engine/artifacts/
├── churn_model.pkl
├── scaler.pkl
└── label_encoders.pkl
```

## Running Tests

### Backend

From `Backend/`:

```bash
python manage.py test
```

### Frontend

From `Frontend/`:

```bash
npm run test
```

## Main Application Routes (Frontend)

- `/` (login)
- `/dashboard`
- `/policyholders`
- `/register-policy`
- `/claims/new`
- `/claims`
- `/payments`
- `/matured`
- `/churn`
- `/churn-prediction`
- `/reports`

## Project Documentation

Additional implementation documents are available at repository root, including:

- `DEVELOPER_REFERENCE.md`
- `IMPLEMENTATION_STATUS.md`
- `PROJECT_COMPLETION_SUMMARY.md`
- `ML_MODEL_INTEGRATION_GUIDE.md`
- `AUTHENTICATION_IMPLEMENTATION_GUIDE.md`
- `POLICY_REGISTRATION_TESTING_GUIDE.md`

## Current Status

This project includes completed modules for:
- Authentication and user management
- Policy registration and policyholder management
- Claims filing and claims management
- Payment and matured policy workflows
- Churn analytics and prediction integration

## License

This project is for educational and internal development use unless otherwise specified.
# Churn Prediction App
