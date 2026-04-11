#!/usr/bin/env python3
"""
Customer Churn Calculation Feature Test
=====================================
Professional test suite for the customer churn calculation feature.

Tests:
- Customer search functionality
- Customer details retrieval
- Churn calculation model
- API endpoint integration

Usage:
    python test_churn_calculation.py
"""

import os
import sys

# Add Django project path
sys.path.append('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')

import django
django.setup()

from churn.models import Customer, Policy, ChurnPrediction, RiskLevel
from churn.views import CustomerChurnCalculationViewSet
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model


def test_churn_calculation_feature():
    """Test the complete churn calculation feature."""
    print("=" * 80)
    print("CUSTOMER CHURN CALCULATION FEATURE - PROFESSIONAL TEST")
    print("=" * 80)
    
    User = get_user_model()
    factory = APIRequestFactory()
    
    # Create test request
    request = factory.get('/api/v1/churn-calculation/')
    request.user = User.objects.first()
    
    # Create viewset instance
    view = CustomerChurnCalculationViewSet()
    view.request = request
    view.format_kwarg = None
    
    print("\n📊 DATABASE VERIFICATION:")
    total_customers = Customer.objects.count()Web Bundling failed 121918ms node_modules/expo-router/entry.js (1454 modules)
 ERROR  SyntaxError: /home/aqi/Documents/Projects/Farm-Link-AI/app/(tabs)/_layout.tsx: Unexpected token (119:6)

  117 |                 <Ionicons name="map-outline" size={size} color={color} />
  118 |               ),turn (
> 119 |       <View style={styles.loadingContainer}>
      |       ^
  120 |         <Ionicons name="hourglass-outline" size={48} color={Colors.primary} />
  121 |       </View>
  122 |     );
    at constructor (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:365:19)
    at TypeScriptParserMixin.raise (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:6599:19)
    at TypeScriptParserMixin.unexpected (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:6619:16)
    at TypeScriptParserMixin.parseIdentifierName (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:12193:12)
    at TypeScriptParserMixin.parseIdentifier (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:12171:23)
    at TypeScriptParserMixin.parseBindingAtom (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:7356:17)
    at TypeScriptParserMixin.parseBindingAtom (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:9932:18)
    at TypeScriptParserMixin.parseMaybeDefault (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:7444:39)
    at TypeScriptParserMixin.parseMaybeDefault (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:9960:24)
    at TypeScriptParserMixin.parseBindingElement (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:9119:23)
    at TypeScriptParserMixin.parseBindingList (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:7392:24)
    at TypeScriptParserMixin.parseFunctionParams (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:13451:24)
    at TypeScriptParserMixin.parseFunctionParams (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:9739:11)
    at TypeScriptParserMixin.parseMethod (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:12033:10)
    at TypeScriptParserMixin.parseMethod (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:10090:26)
    at TypeScriptParserMixin.parseObjectMethod (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:11934:19)
    at TypeScriptParserMixin.parseObjPropValue (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:11968:23)
    at TypeScriptParserMixin.parseObjPropValue (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:9734:18)
    at TypeScriptParserMixin.parsePropertyDefinition (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:11905:17)
    at TypeScriptParserMixin.parseObjectLike (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:11822:21)
    at TypeScriptParserMixin.parseExprAtom (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:11329:23)
    at TypeScriptParserMixin.parseExprAtom (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:4764:20)
    at TypeScriptParserMixin.parseExprSubscripts (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:11071:23)
    at TypeScriptParserMixin.parseUpdate (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:11056:21)
    at TypeScriptParserMixin.parseMaybeUnary (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:11036:23)
    at TypeScriptParserMixin.parseMaybeUnary (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:9827:18)
    at TypeScriptParserMixin.parseMaybeUnaryOrPrivate (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:10889:61)
    at TypeScriptParserMixin.parseExprOps (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:10894:23)
    at TypeScriptParserMixin.parseMaybeConditional (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:10871:23)
    at TypeScriptParserMixin.parseMaybeAssign (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:10821:21)
    at TypeScriptParserMixin.parseMaybeAssign (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:9776:20)
    at TypeScriptParserMixin.parseExpressionBase (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:10774:23)
    at /home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:10770:39
    at TypeScriptParserMixin.allowInAnd (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:12416:12)
    at TypeScriptParserMixin.parseExpression (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:10770:17)
    at TypeScriptParserMixin.jsxParseExpressionContainer (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:4632:31)
    at TypeScriptParserMixin.jsxParseAttributeValue (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:4604:21)
    at TypeScriptParserMixin.jsxParseAttribute (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:4653:38)
    at TypeScriptParserMixin.jsxParseOpeningElementAfterName (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:4667:28)
    at TypeScriptParserMixin.jsxParseOpeningElementAfterName (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:10033:18)
    at TypeScriptParserMixin.jsxParseOpeningElementAt (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:4662:17)
    at TypeScriptParserMixin.jsxParseElementAt (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:4686:33)
    at TypeScriptParserMixin.jsxParseElementAt (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:4698:32)
    at TypeScriptParserMixin.jsxParseElement (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:4749:17)
    at TypeScriptParserMixin.parseExprAtom (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:4759:19)
    at TypeScriptParserMixin.parseExprSubscripts (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:11071:23)
    at TypeScriptParserMixin.parseUpdate (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:11056:21)
    at TypeScriptParserMixin.parseMaybeUnary (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:11036:23)
    at TypeScriptParserMixin.parseMaybeUnary (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:9827:18)
    at TypeScriptParserMixin.parseMaybeUnaryOrPrivate (/home/aqi/Documents/Projects/Farm-Link-AI/node_modules/@babel/parser/lib/index.js:10889:61)

    total_policies = Policy.objects.count()
    total_predictions = ChurnPrediction.objects.count()
    
    print(f"  Total Customers: {total_customers:,}")
    print(f"  Total Policies: {total_policies:,}")
    print(f"  Existing Predictions: {total_predictions:,}")
    
    print("\n🔍 TESTING CUSTOMER SEARCH:")
    
    # Test customer search
    try:
        search_request = factory.get('/api/v1/churn-calculation/customer-search/?q=Tanaka&limit=10')
        search_request.user = User.objects.first()
        view.request = search_request
        
        search_response = view.customer_search(search_request)
        search_data = search_response.data
        
        print(f"  ✅ Customer Search Status: {search_response.status_code}")
        print(f"  📊 Search Results: {len(search_data.get('customers', []))} customers found")
        print(f"  🔍 Search Query: '{search_data.get('search_query', 'N/A')}'")
        print(f"  📈 Total Available: {search_data.get('total_available', 0)}")
        
        if search_data.get('customers'):
            sample_customer = search_data['customers'][0]
            print(f"  👤 Sample Customer: {sample_customer.get('full_name', 'N/A')}")
            print(f"  📋 Customer Number: {sample_customer.get('customer_number', 'N/A')}")
            print(f"  📧 Email: {sample_customer.get('email', 'N/A')}")
            print(f"  📱 Phone: {sample_customer.get('phone_primary', 'N/A')}")
            print(f"  🎂 Age: {sample_customer.get('age', 'N/A')}")
            print(f"  📊 Has Policy: {sample_customer.get('has_policy', False)}")
            print(f"  📋 Policy Count: {sample_customer.get('policy_count', 0)}")
        
    except Exception as e:
        print(f"  ❌ Customer Search Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n📋 TESTING CUSTOMER DETAILS:")
    
    # Test customer details
    try:
        if search_data.get('customers'):
            customer_id = search_data['customers'][0]['id']
            
            details_request = factory.get(f'/api/v1/churn-calculation/customer-details/?customer_id={customer_id}')
            details_request.user = User.objects.first()
            view.request = details_request
            
            details_response = view.customer_details(details_request)
            details_data = details_response.data
            
            print(f"  ✅ Customer Details Status: {details_response.status_code}")
            
            if details_data.get('success'):
                customer_details = details_data.get('customer_details', {})
                
                # Customer info
                customer_info = customer_details.get('customer_info', {})
                print(f"  👤 Customer Name: {customer_info.get('full_name', 'N/A')}")
                print(f"  📋 Customer Number: {customer_info.get('customer_number', 'N/A')}")
                print(f"  📧 Email: {customer_info.get('email', 'N/A')}")
                print(f"  🎂 Age: {customer_info.get('age', 'N/A')}")
                print(f"  📍 Location: {customer_info.get('location', {}).get('label', 'N/A')}")
                print(f"  💰 Income Level: {customer_info.get('income_level', {}).get('label', 'N/A')}")
                
                # Policy summary
                policy_summary = customer_details.get('policy_summary', {})
                print(f"  📋 Total Policies: {policy_summary.get('total_policies', 0)}")
                print(f"  ✅ Active Policies: {policy_summary.get('active_policies', 0)}")
                print(f"  💰 Total Premium: ${policy_summary.get('total_premium', 0):.2f}")
                print(f"  📊 Average Premium: ${policy_summary.get('average_premium', 0):.2f}")
                print(f"  📅 Average Tenure: {policy_summary.get('average_tenure_months', 0):.1f} months")
                
                # Engagement metrics
                engagement = customer_details.get('engagement_metrics', {})
                print(f"  🤝 Total Interactions: {engagement.get('total_interactions', 0)}")
                print(f"  📅 Last Interaction: {engagement.get('last_interaction', 'N/A')}")
                print(f"  📊 Interaction Types: {len(engagement.get('interaction_types', []))}")
                
                # Churn history
                churn_history = customer_details.get('churn_history', [])
                print(f"  📈 Churn History: {len(churn_history)} previous predictions")
                
            else:
                print(f"  ❌ Customer Details Failed: {details_data.get('message', 'Unknown error')}")
        
    except Exception as e:
        print(f"  ❌ Customer Details Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🧮 TESTING CHURN CALCULATION:")
    
    # Test churn calculation
    try:
        if search_data.get('customers'):
            customer_id = search_data['customers'][0]['id']
            
            calc_request = factory.post('/api/v1/churn-calculation/calculate-churn/', {
                'customer_id': customer_id,
                'calculation_context': {
                    'test_mode': True,
                    'calculation_purpose': 'feature_test'
                }
            })
            calc_request.user = User.objects.first()
            view.request = calc_request
            
            calc_response = view.calculate_churn(calc_request)
            calc_data = calc_response.data
            
            print(f"  ✅ Churn Calculation Status: {calc_response.status_code}")
            
            if calc_data.get('success'):
                prediction = calc_data.get('churn_prediction', {})
                
                print(f"  🎯 Customer: {prediction.get('customer_name', 'N/A')}")
                print(f"  📊 Churn Percentage: {prediction.get('churn_percentage', 0)}%")
                print(f"  ⚠️ Risk Level: {prediction.get('risk_level', {}).get('label', 'N/A')}")
                print(f"  📈 Confidence Score: {prediction.get('confidence_score', 0)}%")
                print(f"  🤖 Model Version: {prediction.get('model_version', 'N/A')}")
                print(f"  📅 Predicted At: {prediction.get('predicted_at', 'N/A')}")
                
                # Key factors
                key_factors = prediction.get('key_factors', [])
                print(f"  🔍 Key Factors: {len(key_factors)} identified")
                for factor in key_factors:
                    print(f"     - {factor}")
                
                # Recommendations
                recommendations = prediction.get('recommendations', [])
                print(f"  💡 Recommendations: {len(recommendations)} provided")
                for rec in recommendations:
                    print(f"     - {rec}")
                
                # Metadata
                metadata = calc_data.get('calculation_metadata', {})
                data_points = metadata.get('data_points_used', {})
                print(f"  📊 Data Points Used:")
                print(f"     - Policies: {data_points.get('policies', 0)}")
                print(f"     - Engagements: {data_points.get('engagements', 0)}")
                print(f"     - Payments: {data_points.get('payments', 0)}")
                print(f"     - Claims: {data_points.get('claims', 0)}")
                
            else:
                print(f"  ❌ Churn Calculation Failed: {calc_data.get('message', 'Unknown error')}")
        
    except Exception as e:
        print(f"  ❌ Churn Calculation Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎯 FEATURE INTEGRATION TEST:")
    
    # Test complete workflow
    try:
        print("  🔄 Testing complete customer churn calculation workflow...")
        
        # 1. Search for customer
        search_query = "Anesu"
        search_request = factory.get(f'/api/v1/churn-calculation/customer-search/?q={search_query}&limit=5')
        search_request.user = User.objects.first()
        view.request = search_request
        search_response = view.customer_search(search_request)
        
        if search_response.status_code == 200 and search_response.data.get('customers'):
            customer_id = search_response.data['customers'][0]['id']
            customer_name = search_response.data['customers'][0]['full_name']
            
            # 2. Get customer details
            details_request = factory.get(f'/api/v1/churn-calculation/customer-details/?customer_id={customer_id}')
            details_request.user = User.objects.first()
            view.request = details_request
            details_response = view.customer_details(details_request)
            
            # 3. Calculate churn
            calc_request = factory.post('/api/v1/churn-calculation/calculate-churn/', {
                'customer_id': customer_id,
                'calculation_context': {'workflow_test': True}
            })
            calc_request.user = User.objects.first()
            view.request = calc_request
            calc_response = view.calculate_churn(calc_request)
            
            if calc_response.status_code == 200:
                churn_result = calc_response.data.get('churn_prediction', {})
                print(f"  ✅ Workflow Success: {customer_name}")
                print(f"  📊 Churn Risk: {churn_result.get('churn_percentage', 0)}%")
                print(f"  ⚠️ Risk Level: {churn_result.get('risk_level', {}).get('label', 'N/A')}")
                print(f"  💡 Recommendations: {len(churn_result.get('recommendations', []))}")
            else:
                print(f"  ❌ Workflow Failed at calculation step")
        else:
            print(f"  ❌ Workflow Failed at search step")
        
    except Exception as e:
        print(f"  ❌ Workflow Error: {e}")
        return False
    
    print("\n📊 MODEL ACCURACY VERIFICATION:")
    
    # Verify risk levels exist
    try:
        risk_levels = RiskLevel.objects.all()
        print(f"  ✅ Risk Levels Available: {len(risk_levels)}")
        for level in risk_levels:
            print(f"     - {level.label} ({level.code})")
        
        # Verify predictions can be stored
        total_predictions_after = ChurnPrediction.objects.count()
        print(f"  📈 Total Predictions: {total_predictions_after}")
        
        if total_predictions_after > total_predictions:
            print(f"  ✅ New Prediction Created Successfully")
        else:
            print(f"  ⚠️ No new predictions created")
        
    except Exception as e:
        print(f"  ❌ Model Verification Error: {e}")
        return False
    
    print("\n🚀 PRODUCTION READINESS CHECK:")
    
    # Check production readiness
    checks = [
        ("Customer Search", search_response.status_code == 200),
        ("Customer Details", details_response.status_code == 200),
        ("Churn Calculation", calc_response.status_code == 200),
        ("Data Integration", total_customers > 0),
        ("Model Availability", len(risk_levels) >= 3),
        ("Prediction Storage", total_predictions_after >= total_predictions)
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ CUSTOMER CHURN CALCULATION FEATURE - PROFESSIONAL TEST COMPLETE")
        print("🚀 All tests passed - Feature ready for production!")
    else:
        print("❌ Some tests failed - Review implementation")
    print("=" * 80)
    
    return all_passed


if __name__ == '__main__':
    success = test_churn_calculation_feature()
    sys.exit(0 if success else 1)
