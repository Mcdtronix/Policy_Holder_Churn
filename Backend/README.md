# Nyaradzo Funeral Assurance — Churn Prediction API

Django REST Framework backend for predicting policyholder churn.
The API supports individual and bulk prediction against live database records.

---

## Project Structure

```
nyaradzo_backend/
├── nyaradzo_backend/          # Django project configuration
│   ├── settings.py            # All settings (env-aware)
│   ├── urls.py                # Root URL dispatcher
│   └── wsgi.py
│
├── churn/                     # Core application
│   ├── models.py              # Customer, ChurnPrediction, ChurnBatchJob
│   ├── serializers.py         # DRF serializers (read/write/response)
│   ├── views.py               # All API views
│   ├── urls.py                # App-level URL routing
│   ├── filters.py             # django-filter CustomerFilter
│   ├── admin.py               # Django admin registration
│   └── management/
│       └── commands/
│           └── import_customers.py   # CSV import command
│
├── ml_engine/                 # ML inference layer
│   ├── __init__.py
│   ├── predictor.py           # ChurnPredictor (ML model + rule-based fallback)
│   └── artifacts/             # Place trained model files here
│       ├── churn_model.pkl    # (copy from Colab after training)
│       ├── scaler.pkl
│       └── label_encoders.pkl
│
├── manage.py
└── requirements.txt
```

---

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. Import the dataset
python manage.py import_customers path/to/nyaradzo_churn_dataset_5000_customers.csv

# 5. Create a superuser (optional, for admin panel)
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

The API will be available at **http://127.0.0.1:8000/api/v1/**

---

## Connecting the Trained ML Model

After running the Colab training notebook, download `churn_model_package.zip`
and extract the three artifact files into `ml_engine/artifacts/`:

```
ml_engine/artifacts/
  churn_model.pkl
  scaler.pkl
  label_encoders.pkl
```

Restart the server. The API will automatically detect the artifacts and
switch from rule-based fallback to full ML inference mode. The `/health/`
endpoint will show `"model_mode": "ml_model"` to confirm.

---

## API Reference

### Base URL
```
http://127.0.0.1:8000/api/v1/
```

---

### Customers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers/` | List all customers (paginated) |
| POST | `/customers/` | Create a new customer |
| GET | `/customers/<id>/` | Retrieve customer + latest prediction |
| PUT | `/customers/<id>/` | Full update |
| PATCH | `/customers/<id>/` | Partial update |
| DELETE | `/customers/<id>/` | Delete customer |

**Filtering** (GET `/customers/`):
```
?gender=Female
?location=Harare
?income_level=Low
?policy_type=Family
?payment_method=Ecocash
?age_min=30&age_max=50
?missed_payments_min=3
?search=Tariro
?ordering=-customer_tenure
```

---

### Predictions

#### Predict — Single Customer
```http
POST /api/v1/predict/5/
Content-Type: application/json

{ "save_result": true }
```

```json
{
  "success": true,
  "mode": "single",
  "model_mode": "rule_based",
  "prediction": {
    "id": 42,
    "customer_id": 5,
    "customer_name": "Tariro Mataruse",
    "churn_percentage": 87.3,
    "risk_level": "High",
    "is_churned": true,
    "interpretation": "Tariro shows high churn risk (87.3%). Schedule a proactive retention call within 48 hours.",
    "risk_colour": "#ea580c",
    "feature_snapshot": { ... },
    "model_version": "1.0.0",
    "predicted_at": "2025-03-09T14:22:00Z"
  }
}
```

#### Predict — All Customers
```http
POST /api/v1/predict/all/
Content-Type: application/json

{
  "save_results": true,
  "customer_ids": []    // omit or empty list = process ALL customers
}
```

#### Predict — Selected Customers Only
```http
POST /api/v1/predict/all/
Content-Type: application/json

{
  "save_results": true,
  "customer_ids": [1, 5, 23, 100, 250]
}
```

#### Prediction History
```http
GET /api/v1/predict/history/5/?limit=10
```

---

### Batch Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/batch-jobs/` | List all batch runs |
| GET | `/batch-jobs/<id>/` | Detail + predictions for one batch |
| GET | `/batch-jobs/<id>/?risk_level=Critical` | Filter by risk band |

---

### Utilities

```http
GET /api/v1/dashboard/     # Aggregate stats, top risk customers, trends
GET /api/v1/health/        # Liveness probe
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | insecure default | Set a strong random key in production |
| `DJANGO_DEBUG` | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | `localhost 127.0.0.1` | Space-separated list |

---

## Risk Level Bands

| Level | Range | Colour |
|-------|-------|--------|
| Critical | ≥ 90% | Red |
| High | 70–89% | Orange |
| Moderate | 40–69% | Amber |
| Low | < 40% | Green |

Customers with `churn_percentage >= 70%` are flagged as `is_churned: true`.
