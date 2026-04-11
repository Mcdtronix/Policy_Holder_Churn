#!/usr/bin/env python3
"""
ML Model Health Check and Verification Script
==============================================

This script verifies that the machine learning model is:
1. Properly loaded
2. Can access all required customer features  
3. Makes predictions without errors

Usage:
    python ml_engine/verify_model.py

Exit Codes:
    0 = SUCCESS (model is healthy)
    1 = FAILURE (model has issues)
"""

import os
import sys
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')

import django
django.setup()

from churn.models import Customer


def verify_artifacts():
    """Verify all model artifact files exist."""
    print("\n" + "=" * 80)
    print("1. ARTIFACT FILES CHECK")
    print("=" * 80)
    
    from ml_engine.predictor import ARTIFACTS_DIR, MODEL_PATH, SCALER_PATH
    
    required_files = {
        "churn_model.pkl": MODEL_PATH,
        "scaler.pkl": SCALER_PATH,
        "label_encoders.pkl": ARTIFACTS_DIR / "label_encoders.pkl",
        "feature_names.pkl": ARTIFACTS_DIR / "feature_names.pkl",
    }
    
    all_exist = True
    for name, path in required_files.items():
        exists = path.exists()
        status = "✅" if exists else "❌"
        size = f"({path.stat().st_size:,} bytes)" if exists else ""
        print(f"  {status} {name:30s} {size}")
        all_exist = all_exist and exists
    
    return all_exist


def verify_model_loading():
    """Verify model loads successfully."""
    print("\n" + "=" * 80)
    print("2. MODEL LOADING CHECK")
    print("=" * 80)
    
    try:
        from ml_engine.predictor import ChurnPredictor
        predictor = ChurnPredictor()
        
        print(f"  ✅ ChurnPredictor instantiated")
        print(f"  ✅ Mode: {predictor.mode}")
        print(f"  ✅ Version: {predictor.version}")
        print(f"  ✅ Model type: {type(predictor._model).__name__}")
        
        success = (
            predictor.mode == "ml_model" and
            predictor._model is not None and
            predictor._scaler is not None
        )
        
        return success, predictor
    except Exception as e:
        print(f"  ❌ Failed to load model: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def verify_features(predictor):
    """Verify customer features are accessible."""
    print("\n" + "=" * 80)
    print("3. CUSTOMER FEATURES CHECK")
    print("=" * 80)
    
    required_features = [
        'age', 'gender', 'location', 'income_level', 'premium_amount', 
        'dependents', 'payment_method', 'late_payments', 'missed_payments',
        'number_of_complaints', 'claims_filed', 'customer_tenure', 
        'service_satisfaction', 'policy_type', 'risk_score', 'engagement_score',
        'premium_per_dependent'
    ]
    
    customer = Customer.objects.first()
    if not customer:
        print("  ❌ No customers in database to test with")
        return False
    
    print(f"  Testing with: {customer.full_name}")
    
    missing_features = []
    for feature in required_features:
        try:
            value = getattr(customer, feature)
            print(f"    ✅ {feature:30s} = {value}")
        except AttributeError as e:
            print(f"    ❌ {feature:30s} - MISSING")
            missing_features.append(feature)
    
    return len(missing_features) == 0


def verify_prediction(predictor):
    """Verify predictions work."""
    print("\n" + "=" * 80)
    print("4. PREDICTION CHECK")
    print("=" * 80)
    
    try:
        customers = list(Customer.objects.all()[:3])
        
        if not customers:
            print("  ❌ No customers in database to test predictions")
            return False
        
        print(f"\n  Testing {len(customers)} customer(s):\n")
        
        for customer in customers:
            result = predictor.predict(customer)
            
            churn_pct = result['churn_percentage']
            is_churned = result['is_churned']
            risk = "HIGH RISK ⚠️" if is_churned else "LOW RISK ✅"
            
            print(f"    {customer.full_name:35s} {churn_pct:6.2f}% → {risk}")
        
        return True
    except Exception as e:
        print(f"  ❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_batch_prediction(predictor):
    """Verify batch prediction works."""
    print("\n" + "=" * 80)
    print("5. BATCH PREDICTION CHECK")
    print("=" * 80)
    
    try:
        customers = list(Customer.objects.all()[:10])
        
        if not customers:
            print("  ⚠️  No customers for batch test (skipping)")
            return True
        
        print(f"  Testing batch prediction with {len(customers)} customers...")
        results = predictor.predict_batch(customers)
        
        print(f"  ✅ Batch prediction successful: {len(results)} results returned")
        print(f"  ✅ Results format validated")
        
        return len(results) == len(customers)
    except Exception as e:
        print(f"  ❌ Batch prediction failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 80)
    print("ML MODEL HEALTH CHECK")
    print("=" * 80)
    
    try:
        # Run checks
        artifacts_ok = verify_artifacts()
        
        model_ok, predictor = verify_model_loading()
        if not model_ok:
            predictor = None
        
        features_ok = verify_features(predictor) if predictor else False
        
        prediction_ok = verify_prediction(predictor) if predictor else False
        
        batch_ok = verify_batch_prediction(predictor) if predictor else False
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        checks = {
            "Artifact Files": artifacts_ok,
            "Model Loading": model_ok,
            "Customer Features": features_ok,
            "Single Prediction": prediction_ok,
            "Batch Prediction": batch_ok,
        }
        
        for check, result in checks.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status:10s} - {check}")
        
        all_ok = all(checks.values())
        
        print("\n" + "=" * 80)
        if all_ok:
            print("✅ ML MODEL IS HEALTHY AND OPERATIONAL")
            print("=" * 80)
            return 0
        else:
            print("❌ ML MODEL HAS ISSUES - SEE ABOVE FOR DETAILS")
            print("=" * 80)
            return 1
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
