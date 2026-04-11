#!/usr/bin/env python3
"""
Policy Pagination Investigation
==============================
Investigate why policy holder page shows fewer than 1000 customers
when database has 5000 customers.

Usage:
    python investigate_policy_pagination.py
"""

import os
import sys

# Add Django project path
sys.path.append('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')

import django
django.setup()

from churn.models import Policy, Customer
from churn.serializers import PolicyListSerializer
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model


def investigate_policy_pagination():
    """Investigate pagination issues in policy endpoint."""
    print("=" * 80)
    print("POLICY PAGINATION INVESTIGATION")
    print("=" * 80)
    
    User = get_user_model()
    factory = APIRequestFactory()
    
    print("\n📊 DATABASE VERIFICATION:")
    total_customers = Customer.objects.count()
    total_policies = Policy.objects.count()
    unique_customers_with_policies = Policy.objects.values('customer').distinct().count()
    
    print(f"  Total Customers in Database: {total_customers:,}")
    print(f"  Total Policies in Database: {total_policies:,}")
    print(f"  Unique Customers with Policies: {unique_customers_with_policies:,}")
    
    # Check if all customers have policies
    customers_without_policies = Customer.objects.filter(policies__isnull=True).count()
    print(f"  Customers without Policies: {customers_without_policies}")
    
    print("\n🔍 PAGINATION SETTINGS:")
    from rest_framework.settings import api_settings
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    page_size = api_settings.PAGE_SIZE
    
    print(f"  Pagination Class: {pagination_class}")
    print(f"  Page Size: {page_size}")
    
    # Calculate expected pages
    expected_pages = (total_policies + page_size - 1) // page_size
    print(f"  Expected Pages: {expected_pages}")
    
    print("\n📄 TESTING POLICY ENDPOINT:")
    
    # Test page 1
    try:
        request = factory.get('/api/v1/policies/')
        request.user = User.objects.first()
        
        from churn.views import PolicyViewSet
        view = PolicyViewSet()
        view.request = request
        view.format_kwarg = None
        
        response = view.list(request)
        
        print(f"  ✅ Page 1 Status: {response.status_code}")
        
        if hasattr(response.data, 'get'):
            if 'results' in response.data:
                results_count = len(response.data['results'])
                total_count = response.data.get('count', 0)
                next_page = response.data.get('next', None)
                previous_page = response.data.get('previous', None)
                
                print(f"  📄 Page 1 Results: {results_count} policies")
                print(f"  📊 Total Count: {total_count}")
                print(f"  ➡️ Next Page: {'Available' if next_page else 'None'}")
                print(f"  ⬅️ Previous Page: {'Available' if previous_page else 'None'}")
                
                # Test multiple pages
                total_retrieved = results_count
                current_page = 1
                next_url = next_page
                
                while next_url and current_page < 5:  # Test first 5 pages
                    current_page += 1
                    # Extract page number from next_url
                    if 'page=' in next_url:
                        page_num = next_url.split('page=')[1].split('&')[0]
                        page_request = factory.get(f'/api/v1/policies/?page={page_num}')
                        page_request.user = User.objects.first()
                        view.request = page_request
                        page_response = view.list(page_request)
                        
                        page_results = len(page_response.data.get('results', []))
                        total_retrieved += page_results
                        next_url = page_response.data.get('next', None)
                        
                        print(f"  📄 Page {current_page}: {page_results} policies (Total: {total_retrieved})")
                    else:
                        break
                
                print(f"\n📈 PAGINATION ANALYSIS:")
                print(f"  Total Retrieved (first 5 pages): {total_retrieved}")
                print(f"  Expected Total: {total_count}")
                print(f"  Coverage: {(total_retrieved/total_count*100):.1f}%")
                
            else:
                print(f"  📄 Response Type: {type(response.data)}")
                print(f"  📊 Total Results: {len(response.data)}")
        else:
            print(f"  📄 Response Data: {response.data}")
            
    except Exception as e:
        print(f"  ❌ Error testing endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🔧 FRONTEND INTEGRATION CHECK:")
    
    # Check if frontend is requesting all pages
    print("  📱 Common Frontend Issues:")
    print("    - Only loading first page of results")
    print("    - Not implementing pagination controls")
    print("    - Not handling 'next' URL for additional pages")
    print("    - Assuming single page contains all data")
    
    print("\n💡 SOLUTIONS:")
    print("  1. Increase PAGE_SIZE in settings.py")
    print("  2. Implement proper pagination in frontend")
    print("  3. Add 'page_size' parameter to API requests")
    print("  4. Use infinite scroll or load more functionality")
    
    print("\n" + "=" * 80)
    print("✅ PAGINATION INVESTIGATION COMPLETE")
    print("=" * 80)
    
    return True


if __name__ == '__main__':
    success = investigate_policy_pagination()
    sys.exit(0 if success else 1)
