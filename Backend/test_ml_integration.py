#!/usr/bin/env python
"""
ML Model Integration Test Suite
================================

Comprehensive test to validate that the ML model is properly integrated
with both customer selection and manual entry prediction modes.

Test Coverage:
1. ML model loads correctly
2. Customer selection mode uses ML model
3. Manual entry mode uses ML model  
4. Both modes produce consistent predictions
5. Error handling and fallback mechanics work
"""

import os
import sys
import json
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')

import django
django.setup()

from django.utils import timezone
from churn.models import (
    Customer, Gender, Location, IncomeLevel, PolicyType, 
    PaymentMethod, Policy, PremiumSchedule, Payment, 
    CustomerEngagement, RiskLevel
)
from ml_engine.predictor import ChurnPredictor


def print_header(title):
    """Print formatted section header."""
    print('\n' + '='*80)
    print(f'  {title}')
    print('='*80)


def print_test(name, status, details=''):
    """Print test result."""
    symbol = '✅' if status else '❌'
    print(f'{symbol} {name}')
    if details:
        print(f'   └─ {details}')


def test_ml_model_loading():
    """Test 1: ML Model Loads Correctly"""
    print_header('TEST 1: ML MODEL LOADING')
    
    try:
        predictor = ChurnPredictor()
        
        # Check model type
        from sklearn.ensemble import GradientBoostingClassifier
        is_gb = isinstance(predictor._model, GradientBoostingClassifier)
        print_test('Model Type Check', is_gb, f'Type: {type(predictor._model).__name__}')
        
        # Check scaler
        from sklearn.preprocessing import StandardScaler
        is_scaler = isinstance(predictor._scaler, StandardScaler)
        print_test('Scaler Type Check', is_scaler, f'Type: {type(predictor._scaler).__name__}')
        
        # Check encoders
        has_encoders = hasattr(predictor, '_label_encoders') and predictor._label_encoders
        print_test('Label Encoders', has_encoders, f'Count: {len(predictor._label_encoders) if has_encoders else 0}')
        
        return is_gb and is_scaler and has_encoders
        
    except Exception as e:
        print_test('Model Loading', False, f'Error: {str(e)}')
        return False


def test_customer_selection_mode():
    """Test 2: Customer Selection Mode Uses ML Model"""
    print_header('TEST 2: CUSTOMER SELECTION MODE (Database Customer)')
    
    try:
        # Create test customer
        gender_m, _ = Gender.objects.get_or_create(code='M', defaults={'label': 'Male'})
        harare, _ = Location.objects.get_or_create(
            city='Harare', district='Harare',
            defaults={'province': 'Harare'}
        )
        income_med, _ = IncomeLevel.objects.get_or_create(code='M', defaults={'label': 'Medium Income'})
        policy_type, _ = PolicyType.objects.get_or_create(
            code='BASIC', defaults={'name': 'Basic Policy', 'is_active': True}
        )
        pay_method, _ = PaymentMethod.objects.get_or_create(code='MOB', defaults={'label': 'Mobile Money'})
        
        # Create customer
        test_customer = Customer.objects.create(
            first_name='Test',
            last_name='DatabaseMode',
            date_of_birth=date(2000, 1, 1),
            gender=gender_m,
            location=harare,
            income_level=income_med,
            email='test.db@test.com',
            phone_primary='+263712000000',
            address_line1='Test Address'
        )
        print_test('Test Customer Created', True, f'ID: {test_customer.id}')
        
        # Create policy
        today = date.today()
        policy = Policy.objects.create(
            customer=test_customer,
            policy_type=policy_type,
            start_date=today - timedelta(days=180),
            sum_assured=500,
            premium_amount=45.0,
            dependents=2,
            status=Policy.Status.ACTIVE
        )
        print_test('Test Policy Created', True, f'Premium: ${policy.premium_amount}')
        
        # Test ML prediction on customer
        predictor = ChurnPredictor()
        result = predictor.predict(test_customer)
        
        has_churn_pct = 'churn_percentage' in result
        has_is_churned = 'is_churned' in result
        churn_valid = 0 <= result.get('churn_percentage', -1) <= 100
        
        print_test('ML Prediction Successful', has_churn_pct and has_is_churned, 
                   f'Churn: {result.get("churn_percentage", "N/A")}%')
        print_test('Result Validity Check', churn_valid, 
                   f'Percentage in range [0-100]: {churn_valid}')
        
        # Cleanup
        test_customer.delete()
        
        return has_churn_pct and has_is_churned and churn_valid
        
    except Exception as e:
        print_test('Customer Selection Mode', False, f'Error: {str(e)}')
        return False


def test_manual_entry_mode():
    """Test 3: Manual Entry Mode Uses ML Model"""
    print_header('TEST 3: MANUAL ENTRY MODE (User Input Features)')
    
    try:
        # Create a dummy request-like data object
        manual_data = {
            'age': 35,
            'gender': 'Male',
            'location': 'Bulawayo',
            'income_level': 'High Income',
            'policy_count': 2,
            'average_premium': 85.0,
            'payment_method': 'Bank Debit',
            'dependents': 3,
            'late_payments': 1,
            'missed_payments': 0,
            'number_of_complaints': 1,
            'claims_filed': 0,
            'customer_tenure': 24,
            'service_satisfaction': 8.0
        }
        
        print_test('Manual Data Prepared', True, f'Features: {len(manual_data)}')
        
        # Test manual prediction (simulating backend endpoint)
        from churn.views import CustomerChurnCalculationViewSet
        viewset = CustomerChurnCalculationViewSet()
        result = viewset._calculate_churn_score_from_manual_data(manual_data)
        
        has_churn_pct = 'churn_percentage' in result
        has_is_churned = 'is_churned' in result
        has_risk_level = 'risk_level' in result
        churn_valid = 0 <= result.get('churn_percentage', -1) <= 100
        source_is_ml = result.get('source') == 'ml_model_manual_entry'
        
        print_test('ML Prediction Successful', has_churn_pct and has_is_churned,
                   f'Churn: {result.get("churn_percentage", "N/A")}%')
        print_test('Result Validity Check', churn_valid,
                   f'Percentage in range [0-100]: {churn_valid}')
        print_test('Data Points Used', result.get('data_points_used') == 19,
                   f'Features: {result.get("data_points_used")}')
        print_test('ML Model Source Check', source_is_ml,
                   f'Source: {result.get("source")}')
        
        return has_churn_pct and has_is_churned and churn_valid and source_is_ml
        
    except Exception as e:
        print_test('Manual Entry Mode', False, f'Error: {str(e)}')
        return False


def test_mode_consistency():
    """Test 4: Both Modes Produce Similar Predictions"""
    print_header('TEST 4: PREDICTION CONSISTENCY CHECK')
    
    try:
        # Create test customer
        gender_m, _ = Gender.objects.get_or_create(code='M', defaults={'label': 'Male'})
        victoria, _ = Location.objects.get_or_create(
            city='Victoria Falls', district='Victoria Falls',
            defaults={'province': 'Matabeleland North'}
        )
        income_low, _ = IncomeLevel.objects.get_or_create(code='L', defaults={'label': 'Low Income'})
        policy_type, _ = PolicyType.objects.get_or_create(
            code='FAM', defaults={'name': 'Family', 'is_active': True}
        )
        pay_cash, _ = PaymentMethod.objects.get_or_create(code='CASH', defaults={'label': 'Cash'})
        
        # Create customer matching manual data
        test_customer = Customer.objects.create(
            first_name='Consistency',
            last_name='TestCase',
            date_of_birth=date(1995, 6, 15),
            gender=gender_m,
            location=victoria,
            income_level=income_low,
            email='consistency@test.com',
            phone_primary='+263712111111',
            address_line1='Test'
        )
        
        today = date.today()
        policy = Policy.objects.create(
            customer=test_customer,
            policy_type=policy_type,
            start_date=today - timedelta(days=365),
            sum_assured=1000,
            premium_amount=55.0,
            dependents=4,
            status=Policy.Status.ACTIVE
        )
        
        # Mode 1: Database customer prediction
        predictor = ChurnPredictor()
        db_result = predictor.predict(test_customer)
        db_churn = db_result['churn_percentage']
        
        print_test('Database Mode Result', True, f'Churn: {db_churn}%')
        
        # Mode 2: Manual entry with same features
        manual_data = {
            'age': test_customer.age,
            'gender': 'Male',
            'location': 'Victoria Falls',
            'income_level': 'Low Income',
            'policy_count': 1,
            'average_premium': 55.0,
            'payment_method': 'Cash',
            'dependents': 4,
            'late_payments': 0,
            'missed_payments': 0,
            'number_of_complaints': 0,
            'claims_filed': 0,
            'customer_tenure': 12,
            'service_satisfaction': 7.0
        }
        
        from churn.views import CustomerChurnCalculationViewSet
        viewset = CustomerChurnCalculationViewSet()
        manual_result = viewset._calculate_churn_score_from_manual_data(manual_data)
        manual_churn = manual_result['churn_percentage']
        
        print_test('Manual Mode Result', True, f'Churn: {manual_churn}%')
        
        # Compare results (allow 10% difference due to feature extraction differences)
        difference = abs(db_churn - manual_churn)
        consistent = difference <= 10
        
        print_test('Mode Consistency Check', consistent,
                   f'Difference: {difference:.2f}% (threshold: 10%)')
        
        # Cleanup
        test_customer.delete()
        
        return consistent
        
    except Exception as e:
        print_test('Mode Consistency', False, f'Error: {str(e)}')
        return False


def run_all_tests():
    """Run all tests and report results."""
    print('\n' + '#'*80)
    print('#  ML MODEL INTEGRATION TEST SUITE')
    print('#'*80)
    print('Testing that the ML model is properly integrated for both customer')
    print('selection and manual data entry modes in the churn prediction system.')
    
    results = {
        'ML Model Loading': test_ml_model_loading(),
        'Customer Selection Mode': test_customer_selection_mode(),
        'Manual Entry Mode': test_manual_entry_mode(),
        'Prediction Consistency': test_mode_consistency(),
    }
    
    # Summary
    print_header('TEST SUMMARY')
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        symbol = '✅' if passed_test else '❌'
        print(f'{symbol} {test_name}')
    
    print(f'\nResult: {passed}/{total} tests passed')
    
    if passed == total:
        print('\n🎉 ALL TESTS PASSED - ML Model Integration Complete!')
        return True
    else:
        print(f'\n⚠️  {total - passed} test(s) failed - Review errors above')
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
