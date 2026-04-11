"""
ml_engine/predictor.py — Churn Prediction Engine
==================================================
Encapsulates all machine learning logic behind a clean interface.
The engine supports two modes:

  1. Trained model mode  — loads a serialised scikit-learn / XGBoost
     pipeline from disk (artifacts/churn_model.pkl) and runs inference.

  2. Rule-based fallback — if no model file is found (e.g. first boot
     before training has been run), a transparent weighted scoring
     formula is used. This guarantees the API always returns meaningful
     results and makes the system self-contained for development.

The public surface is a single class: ChurnPredictor
  predictor = ChurnPredictor()
  result    = predictor.predict(customer)            # → dict
  results   = predictor.predict_batch(customers)     # → list[dict]
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from churn.models import Customer

logger = logging.getLogger(__name__)

# ── Artifact paths ─────────────────────────────────────────────────────────────
_BASE_DIR     = Path(__file__).resolve().parent
ARTIFACTS_DIR = _BASE_DIR / "artifacts"
MODEL_PATH    = ARTIFACTS_DIR / "churn_model.pkl"
SCALER_PATH   = ARTIFACTS_DIR / "scaler.pkl"
ENCODERS_PATH = ARTIFACTS_DIR / "label_encoders.pkl"

MODEL_VERSION = "1.0.0"

# ── Encoding maps (must mirror the LabelEncoder fit order in the notebook) ─────
_GENDER_MAP    = {"Female": 0, "Male": 1}
_LOCATION_MAP  = {
    "Bindura": 0, "Bulawayo": 1, "Chegutu": 2, "Chitungwiza": 3,
    "Gweru": 4, "Harare": 5, "Hwange": 6, "Kadoma": 7, "Kariba": 8,
    "Kwekwe": 9, "Marondera": 10, "Masvingo": 11, "Mutare": 12,
    "Norton": 13, "Victoria Falls": 14,
}
_INCOME_MAP    = {"High": 0, "Low": 1, "Medium": 2}
_POLICY_MAP    = {"Family": 0, "Individual": 1}
_PAYMENT_MAP   = {"Bank Debit": 0, "Cash": 1, "Ecocash": 2, "Mobile Money": 3}

# ── Feature order — must exactly match X.columns in the training notebook ──────
FEATURE_ORDER = [
    "Age", "Gender", "Location", "Income_Level", "Policy_Type",
    "Premium_Amount", "Dependents", "Payment_Method",
    "Late_Payments", "Missed_Payments", "Number_of_Complaints",
    "Claims_Filed", "Customer_Tenure", "Service_Satisfaction",
    # Engineered features
    "Risk_Score", "Engagement_Score", "Premium_per_Dependent",
    "Has_Complaint", "Has_Claim",
]


class ChurnPredictor:
    """
    Thread-safe singleton-friendly churn prediction engine.

    Usage
    -----
    predictor = ChurnPredictor()
    result    = predictor.predict(customer_instance)
    """

    def __init__(self):
        self._model   = None
        self._scaler  = None
        self._encoders = None
        self._mode    = "rule_based"
        logger.info("\n" + "="*80)
        logger.info("🚀 [INIT] ChurnPredictor initializing...")
        logger.info("="*80)
        print("\n" + "="*80)
        print("🚀 [INIT] ChurnPredictor initializing...")
        print(f"   MODEL_PATH: {MODEL_PATH}")
        print(f"   SCALER_PATH: {SCALER_PATH}")
        print(f"   ARTIFACTS_DIR: {ARTIFACTS_DIR}")
        print("="*80 + "\n")
        self._load_artifacts()
        logger.info(f"🔚 [INIT] Initialization complete. Mode: {self._mode}")
        print(f"✅ [INIT] Complete. Mode: {self._mode}\n")

    # ── Private: artifact loading ──────────────────────────────────────────────

    def _load_artifacts(self) -> None:
        """
        Load serialised model artifacts from disk.
        PRODUCTION MODE: Enforces ML model usage (no fallback).
        """
        print(f"\n📂 [LOAD_ARTIFACTS] Starting artifact loading...")
        print(f"   MODEL_PATH: {MODEL_PATH}")
        print(f"   SCALER_PATH: {SCALER_PATH}")
        print(f"   Checking if files exist...")
        print(f"   MODEL_PATH exists: {MODEL_PATH.exists()}")
        print(f"   SCALER_PATH exists: {SCALER_PATH.exists()}\n")
        
        try:
            import joblib

            if not (MODEL_PATH.exists() and SCALER_PATH.exists()):
                print(f"❌ [LOAD_ARTIFACTS] FILES NOT FOUND - RAISING ERROR")
                raise FileNotFoundError(
                    f"❌ CRITICAL: Model artifacts not found at {ARTIFACTS_DIR}. "
                    f"Required files:\n"
                    f"  - {MODEL_PATH}\n"
                    f"  - {SCALER_PATH}\n"
                    f"Cannot proceed without trained model."
                )

            print(f"✅ Files found. Loading artifacts...")
            logger.info(f"🔄 [LOAD] Loading model from: {MODEL_PATH}")
            print(f"   Loading model: {MODEL_PATH}")
            model = joblib.load(MODEL_PATH)
            print(f"   ✅ Model loaded. Type: {type(model)}")
            logger.info(f"✅ Model loaded successfully. Type: {type(model)}")

            print(f"   Loading scaler: {SCALER_PATH}")
            logger.info(f"🔄 [LOAD] Loading scaler from: {SCALER_PATH}")
            scaler = joblib.load(SCALER_PATH)
            print(f"   ✅ Scaler loaded. Type: {type(scaler)}")
            logger.info(f"✅ Scaler loaded successfully. Type: {type(scaler)}")

            print(f"   Loading encoders: {ENCODERS_PATH}")
            encoders = joblib.load(ENCODERS_PATH) if ENCODERS_PATH.exists() else None
            if encoders:
                print(f"   ✅ Encoders loaded. Type: {type(encoders)}")
                logger.info(f"✅ Encoders loaded successfully")
            else:
                print(f"   ⚠️ Encoders not found (optional)")

            self._model = model
            self._scaler = scaler
            self._encoders = encoders
            self._mode = "ml_model"
            print(f"\n🎯 [SUCCESS] MODE: {self._mode}")
            print(f"🎯 [SUCCESS] ML MODEL READY FOR PREDICTIONS\n")
            logger.info(f"🎯 PRODUCTION MODE: Using trained ML model for all predictions")

        except Exception as exc:
            print(f"\n❌ [ERROR] ARTIFACT LOADING FAILED")
            print(f"❌ Exception type: {type(exc).__name__}")
            print(f"❌ Exception message: {str(exc)}\n")
            logger.error(f"❌ Exception: {exc}", exc_info=True)
            raise RuntimeError(
                f"❌ CRITICAL: Failed to load ML model artifacts. Error: {str(exc)}"
            ) from exc

    # ── Public interface ───────────────────────────────────────────────────────

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def version(self) -> str:
        return MODEL_VERSION

    def predict(self, customer: "Customer") -> dict:
        """
        Compute the churn percentage for a single Customer instance.

        Returns
        -------
        dict with keys:
          churn_percentage  float   0–100
          is_churned        bool    churn_percentage >= 70
          feature_snapshot  dict    exact inputs used
          model_version     str
        """
        print(f"\n[PREDICT] Starting for customer: {customer.id}")
        print(f"[PREDICT] Mode: {self._mode}, Model: {self._model is not None}, Scaler: {self._scaler is not None}")
        
        features    = self._extract_features(customer)
        snapshot    = self._build_snapshot(customer)
        
        print(f"[PREDICT] Features shape: {features.shape}, values: {features}")

        if self._mode != "ml_model" or self._model is None or self._scaler is None:
            msg = (
                f"❌ Mode: {self._mode}, Model: {self._model is not None}, "
                f"Scaler: {self._scaler is not None}. Cannot proceed."
            )
            print(f"\n{msg}\n")
            raise RuntimeError(msg)

        try:
            print(f"[PREDICT] Calling _ml_predict...")
            churn_pct = self._ml_predict(features)
            print(f"[PREDICT] ✅ Result: {churn_pct:.2f}%\n")
            logger.debug(f"✅ Customer {customer.id}: {churn_pct:.2f}% churn")
        except Exception as exc:
            msg = f"❌ Inference failed: {str(exc)}"
            print(f"\n{msg}\n")
            logger.error(msg, exc_info=True)
            raise

        return {
            "churn_percentage": round(churn_pct, 2),
            "is_churned":       churn_pct >= 70.0,
            "feature_snapshot": snapshot,
            "model_version":    MODEL_VERSION,
        }

    def predict_batch(self, customers: list["Customer"]) -> list[dict]:
        """
        Compute churn for a list of Customer instances efficiently.
        Uses vectorised prediction when in ML mode.

        Returns a list of result dicts in the same order as input.
        """
        if not customers:
            return []

        if self._mode != "ml_model" or self._model is None or self._scaler is None:
            raise RuntimeError(
                f"❌ CRITICAL: ML model not available for batch prediction. "
                f"Cannot proceed without trained model."
            )

        try:
            logger.info(f"🔄 [BATCH_PREDICT] Processing {len(customers)} customers with trained ML model")
            results = self._ml_predict_batch(customers)
            logger.info(f"✅ [BATCH_PREDICT] Completed {len(results)} predictions")
            return results
        except Exception as exc:
            raise RuntimeError(
                f"❌ CRITICAL: ML batch inference failed. Error: {str(exc)}"
            ) from exc

    # ── Feature extraction ─────────────────────────────────────────────────────

    def _extract_features(self, customer: "Customer") -> np.ndarray:
        """
        Build a 1-D numpy array from a Customer instance, encoding
        categorical variables and engineering derived features.
        The order must exactly match FEATURE_ORDER / X.columns in training.
        """
        risk_score            = customer.late_payments + (customer.missed_payments * 2) + customer.number_of_complaints
        engagement_score      = customer.service_satisfaction * customer.customer_tenure
        premium_per_dependent = customer.premium_amount / (customer.dependents + 1)
        has_complaint         = int(customer.number_of_complaints > 0)
        has_claim             = int(customer.claims_filed > 0)

        feature_vector = [
            customer.age,
            _GENDER_MAP.get(customer.gender, 0),
            _LOCATION_MAP.get(customer.location, 0),
            _INCOME_MAP.get(customer.income_level, 0),
            _POLICY_MAP.get(customer.policy_type, 0),
            customer.premium_amount,
            customer.dependents,
            _PAYMENT_MAP.get(customer.payment_method, 0),
            customer.late_payments,
            customer.missed_payments,
            customer.number_of_complaints,
            customer.claims_filed,
            customer.customer_tenure,
            customer.service_satisfaction,
            # Engineered
            risk_score,
            engagement_score,
            premium_per_dependent,
            has_complaint,
            has_claim,
        ]
        return np.array(feature_vector, dtype=float).reshape(1, -1)

    def _build_snapshot(self, customer: "Customer") -> dict:
        """Build a JSON-serialisable dict of all feature values for audit storage."""
        return {
            "age":                   customer.age,
            "gender":                customer.gender,
            "location":              customer.location,
            "income_level":          customer.income_level,
            "policy_type":           customer.policy_type,
            "premium_amount":        customer.premium_amount,
            "dependents":            customer.dependents,
            "payment_method":        customer.payment_method,
            "late_payments":         customer.late_payments,
            "missed_payments":       customer.missed_payments,
            "number_of_complaints":  customer.number_of_complaints,
            "claims_filed":          customer.claims_filed,
            "customer_tenure":       customer.customer_tenure,
            "service_satisfaction":  customer.service_satisfaction,
            # Engineered
            "risk_score":            customer.risk_score,
            "engagement_score":      customer.engagement_score,
            "premium_per_dependent": customer.premium_per_dependent,
        }

    # ── ML model inference ─────────────────────────────────────────────────────

    def _ml_predict(self, features: np.ndarray) -> float:
        """Run a single feature vector through the loaded ML pipeline."""
        scaled = self._scaler.transform(features)
        proba  = self._model.predict_proba(scaled)[0][1]   # P(churned=1)
        return proba * 100.0

    def _ml_predict_batch(self, customers: list["Customer"]) -> list[dict]:
        """Vectorised batch prediction using numpy stacking."""
        feature_matrix = np.vstack([self._extract_features(c) for c in customers])
        scaled         = self._scaler.transform(feature_matrix)
        probas         = self._model.predict_proba(scaled)[:, 1] * 100.0

        results = []
        for customer, churn_pct in zip(customers, probas):
            results.append({
                "churn_percentage": round(float(churn_pct), 2),
                "is_churned":       float(churn_pct) >= 70.0,
                "feature_snapshot": self._build_snapshot(customer),
                "model_version":    MODEL_VERSION,
            })
        return results

    # ── Rule-based fallback [DISABLED] ─────────────────────────────────────────
    # 
    # ❌ RULE-BASED FALLBACK DISABLED IN PRODUCTION
    # 
    # Reason: The rule-based formula was causing discrepancies between Google Colab 
    # model predictions (100% churn) and application predictions (30.2% churn).
    #
    # The trained ML model from Google Colab is the source of truth.
    # All predictions must use the serialized model artifacts.
    #
    # If you need the rule-based logic for testing, it's preserved below as a reference.
    # Uncomment at your own risk - it will cause incorrect predictions.
    
    # def _rule_based_predict(self, customer: "Customer") -> float:
    #     """
    #     [DEPRECATED] Transparent weighted scoring formula.
    #     DO NOT USE - causes incorrect predictions. Use trained ML model instead.
    #     """
    #     score = 0.0
    #     score += min(customer.missed_payments, 10) * 6.0     # up to +60
    #     score += min(customer.late_payments,   10) * 3.0     # up to +30
    #     score += (6 - customer.service_satisfaction) * 4.0   # up to +20
    #     score += min(customer.number_of_complaints, 5) * 3.0  # up to +15
    #     tenure_factor = max(0, 10 - customer.customer_tenure) * 0.8  # up to +8
    #     score += tenure_factor
    #     income_risk = {"Low": 5.0, "Medium": 2.5, "High": 0.0}
    #     score += income_risk.get(customer.income_level, 0.0)
    #     payment_risk = {"Cash": 3.0, "Mobile Money": 2.0, "Ecocash": 1.0, "Bank Debit": 0.0}
    #     score += payment_risk.get(customer.payment_method, 0.0)
    #     ppd = customer.premium_per_dependent
    #     if ppd > 30:
    #         score += 4.0
    #     elif ppd > 15:
    #         score += 2.0
    #     if customer.claims_filed == 0 and customer.customer_tenure > 3:
    #         score += 2.0
    #     if customer.age < 30:
    #         score += 3.0
    #     elif customer.age < 40:
    #         score += 1.5
    #     churn_pct = min((score / 148.0) * 100.0, 100.0)
    #     churn_pct = max(churn_pct, 8.0)
    #     return round(churn_pct, 2)


# ── Module-level singleton (import and reuse across the Django app) ────────────
predictor = ChurnPredictor()
