#!/usr/bin/env python3
"""
Production Readiness Assessment
===============================
Comprehensive scan of the Nyaradzo Assurance Management System
for deployment to PythonAnywhere (backend) and Vercel (frontend).

Assessment Areas:
- Environment variables configuration
- Database setup and migrations
- Security settings
- API endpoints readiness
- Frontend build configuration
- Deployment requirements

Usage:
    python production_readiness_assessment.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add Django project path
sys.path.append('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nyaradzo_backend.settings')

import django
django.setup()

def scan_project_structure():
    """Scan the complete project structure."""
    print("=" * 80)
    print("PROJECT STRUCTURE SCAN")
    print("=" * 80)
    
    project_root = Path('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction')
    
    print("\nPROJECT OVERVIEW:")
    print(f"  Project Root: {project_root}")
    print(f"  Backend Path: {project_root / 'Backend'}")
    print(f"  Frontend Path: {project_root / 'Frontend'}")
    
    print("\nBACKEND STRUCTURE:")
    backend_files = []
    for root, dirs, files in os.walk(project_root / 'Backend'):
        for file in files:
            if file.endswith(('.py', '.json', '.md', '.txt', '.env')):
                rel_path = os.path.relpath(os.path.join(root, file), project_root / 'Backend')
                backend_files.append(rel_path)
    
    print(f"  Total Backend Files: {len(backend_files)}")
    important_files = [f for f in backend_files if any(x in f for x in ['settings', 'urls', 'views', 'models', 'requirements', 'manage', 'wsgi', 'asgi'])]
    print("  Key Backend Files:")
    for file in sorted(important_files):
        print(f"    - {file}")
    
    print("\nFRONTEND STRUCTURE:")
    frontend_files = []
    for root, dirs, files in os.walk(project_root / 'Frontend'):
        for file in files:
            if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.json', '.md', '.env', '.html', '.css')):
                rel_path = os.path.relpath(os.path.join(root, file), project_root / 'Frontend')
                frontend_files.append(rel_path)
    
    print(f"  Total Frontend Files: {len(frontend_files)}")
    important_frontend = [f for f in frontend_files if any(x in f for x in ['package', 'vite', 'next', 'index', 'app', 'layout', 'config'])]
    print("  Key Frontend Files:")
    for file in sorted(important_frontend):
        print(f"    - {file}")
    
    return {
        'backend_files': backend_files,
        'frontend_files': frontend_files,
        'project_root': project_root
    }


def assess_environment_variables():
    """Assess environment variables configuration."""
    print("\n" + "=" * 80)
    print("ENVIRONMENT VARIABLES ASSESSMENT")
    print("=" * 80)
    
    project_root = Path('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction')
    
    # Check backend environment files
    backend_env_files = [
        project_root / 'Backend' / '.env',
        project_root / 'Backend' / '.env.example',
        project_root / 'Backend' / 'nyaradzo_backend' / '.env'
    ]
    
    print("\nBACKEND ENVIRONMENT FILES:")
    env_files_found = []
    for env_file in backend_env_files:
        if env_file.exists():
            env_files_found.append(env_file)
            print(f"  Found: {env_file}")
            
            # Read and analyze environment file
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                    print(f"    Variables: {len(lines)}")
                    
                    # Categorize variables
                    db_vars = [line for line in lines if any(x in line.upper() for x in ['DB_', 'DATABASE', 'POSTGRES', 'MYSQL'])]
                    secret_vars = [line for line in lines if any(x in line.upper() for x in ['SECRET', 'KEY', 'TOKEN', 'PASSWORD'])]
                    django_vars = [line for line in lines if any(x in line.upper() for x in ['DJANGO', 'DEBUG', 'ALLOWED_HOSTS'])]
                    
                    if db_vars:
                        print(f"    Database Variables: {len(db_vars)}")
                    if secret_vars:
                        print(f"    Security Variables: {len(secret_vars)}")
                    if django_vars:
                        print(f"    Django Variables: {len(django_vars)}")
            except Exception as e:
                print(f"    Error reading: {e}")
        else:
            print(f"  Missing: {env_file}")
    
    # Check frontend environment files
    frontend_env_files = [
        project_root / 'Frontend' / '.env',
        project_root / 'Frontend' / '.env.example',
        project_root / 'Frontend' / '.env.local'
    ]
    
    print("\nFRONTEND ENVIRONMENT FILES:")
    for env_file in frontend_env_files:
        if env_file.exists():
            print(f"  Found: {env_file}")
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                    print(f"    Variables: {len(lines)}")
                    
                    # Categorize frontend variables
                    api_vars = [line for line in lines if any(x in line.upper() for x in ['API', 'URL', 'BASE'])]
                    build_vars = [line for line in lines if any(x in line.upper() for x in ['NODE_ENV', 'BUILD', 'VERCEL'])]
                    
                    if api_vars:
                        print(f"    API Variables: {len(api_vars)}")
                    if build_vars:
                        print(f"    Build Variables: {len(build_vars)}")
            except Exception as e:
                print(f"    Error reading: {e}")
        else:
            print(f"  Missing: {env_file}")
    
    return {
        'backend_env_files': env_files_found,
        'frontend_env_files': [f for f in frontend_env_files if f.exists()]
    }


def assess_database_readiness():
    """Assess database configuration and migrations."""
    print("\n" + "=" * 80)
    print("DATABASE READINESS ASSESSMENT")
    print("=" * 80)
    
    try:
        from django.db import connection
        from django.core.management import call_command
        from django.apps import apps
        
        print("\nDATABASE CONNECTION:")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print("  Database Connection: SUCCESS")
        except Exception as e:
            print(f"  Database Connection: FAILED - {e}")
            return False
        
        print("\nMIGRATIONS STATUS:")
        try:
            # Get all migrations
            from django.core.management.commands.showmigrations import Command as ShowMigrationsCommand
            show_migrations = ShowMigrationsCommand()
            
            # Capture migration output
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                show_migrations.handle(None, [], verbosity=0)
            
            migration_output = f.getvalue()
            print("  Migration Status Retrieved")
            
            # Check for unapplied migrations
            if '[ ]' in migration_output:
                print("  Unapplied Migrations: DETECTED")
                print("  Recommendation: Run 'python manage.py migrate'")
            else:
                print("  Migration Status: ALL APPLIED")
                
        except Exception as e:
            print(f"  Migration Check: ERROR - {e}")
        
        print("\nDATABASE TABLES:")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"  Total Tables: {len(tables)}")
                
                # Important tables
                important_tables = ['auth_user', 'churn_customer', 'churn_policy', 'churn_payment', 'churn_claim']
                found_important = [t for t in important_tables if t in tables]
                print(f"  Important Tables: {len(found_important)}/{len(important_tables)}")
                
                for table in found_important:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"    {table}: {count:,} records")
                    
        except Exception as e:
            print(f"  Table Count: ERROR - {e}")
        
        return True
        
    except Exception as e:
        print(f"Database Assessment Error: {e}")
        return False


def assess_security_settings():
    """Assess security configuration."""
    print("\n" + "=" * 80)
    print("SECURITY SETTINGS ASSESSMENT")
    print("=" * 80)
    
    try:
        from django.conf import settings
        from django.core.management.utils import get_random_secret_key
        
        print("\nDJANGO SECURITY SETTINGS:")
        
        # Secret Key
        secret_key = getattr(settings, 'SECRET_KEY', None)
        if secret_key:
            if secret_key == 'your-secret-key-here' or len(secret_key) < 50:
                print("  SECRET_KEY: INSECURE - needs to be changed")
            else:
                print("  SECRET_KEY: SECURE")
        else:
            print("  SECRET_KEY: MISSING")
        
        # Debug Mode
        debug_mode = getattr(settings, 'DEBUG', True)
        print(f"  DEBUG: {'INSECURE' if debug_mode else 'SECURE'}")
        
        # Allowed Hosts
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        print(f"  ALLOWED_HOSTS: {len(allowed_hosts)} configured")
        if not allowed_hosts:
            print("    WARNING: No allowed hosts configured")
        
        # CORS Settings
        cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        print(f"  CORS_ORIGINS: {len(cors_origins)} configured")
        
        # Database Password
        db_password = getattr(settings, 'DATABASES', {}).get('default', {}).get('PASSWORD', '')
        if db_password and db_password != '':
            print("  DATABASE_PASSWORD: CONFIGURED")
        else:
            print("  DATABASE_PASSWORD: NOT CONFIGURED")
        
        # JWT Settings
        jwt_secret = getattr(settings, 'JWT_SECRET_KEY', None)
        if jwt_secret:
            print("  JWT_SECRET_KEY: CONFIGURED")
        else:
            print("  JWT_SECRET_KEY: NOT CONFIGURED")
        
        print("\nSECURITY RECOMMENDATIONS:")
        recommendations = []
        
        if debug_mode:
            recommendations.append("Set DEBUG=False in production")
        
        if not allowed_hosts:
            recommendations.append("Configure ALLOWED_HOSTS for production domain")
        
        if not cors_origins:
            recommendations.append("Configure CORS_ALLOWED_ORIGINS for frontend domain")
        
        if not jwt_secret:
            recommendations.append("Configure JWT_SECRET_KEY for authentication")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("  All security settings appear properly configured")
        
        return len(recommendations) == 0
        
    except Exception as e:
        print(f"Security Assessment Error: {e}")
        return False


def assess_api_endpoints():
    """Assess API endpoints readiness."""
    print("\n" + "=" * 80)
    print("API ENDPOINTS ASSESSMENT")
    print("=" * 80)
    
    try:
        from django.urls import get_resolver
        from rest_framework.test import APIRequestFactory
        from django.contrib.auth import get_user_model
        
        print("\nURL PATTERNS:")
        resolver = get_resolver()
        url_patterns = []
        
        def collect_urls(patterns, prefix=''):
            for pattern in patterns:
                if hasattr(pattern, 'url_patterns'):
                    collect_urls(pattern.url_patterns, prefix + str(pattern.pattern))
                else:
                    url_patterns.append(prefix + str(pattern.pattern))
        
        collect_urls(resolver.url_patterns)
        
        print(f"  Total URL Patterns: {len(url_patterns)}")
        
        # API endpoints
        api_endpoints = [url for url in url_patterns if 'api' in url.lower()]
        print(f"  API Endpoints: {len(api_endpoints)}")
        
        # Important endpoints
        important_endpoints = [
            'api/v1/users/',
            'api/v1/customers/',
            'api/v1/policies/',
            'api/v1/dashboard/',
            'api/v1/analytics/',
            'api/v1/churn-calculation/'
        ]
        
        found_endpoints = [ep for ep in important_endpoints if any(ep in url for url in api_endpoints)]
        print(f"  Important Endpoints: {len(found_endpoints)}/{len(important_endpoints)}")
        
        for endpoint in found_endpoints:
            print(f"    - {endpoint}")
        
        print("\nAUTHENTICATION TESTING:")
        try:
            User = get_user_model()
            user_count = User.objects.count()
            print(f"  Users in Database: {user_count}")
            
            if user_count > 0:
                print("  Authentication: READY")
            else:
                print("  Authentication: NO USERS - need to create admin user")
        except Exception as e:
            print(f"  Authentication Check: ERROR - {e}")
        
        return True
        
    except Exception as e:
        print(f"API Assessment Error: {e}")
        return False


def assess_frontend_readiness():
    """Assess frontend build configuration."""
    print("\n" + "=" * 80)
    print("FRONTEND READINESS ASSESSMENT")
    print("=" * 80)
    
    project_root = Path('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction')
    frontend_path = project_root / 'Frontend'
    
    print("\nFRONTEND CONFIGURATION:")
    
    # Package.json
    package_json = frontend_path / 'package.json'
    if package_json.exists():
        try:
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            print(f"  Project Name: {package_data.get('name', 'Unknown')}")
            print(f"  Version: {package_data.get('version', 'Unknown')}")
            print(f"  Build Script: {'present' if 'build' in package_data.get('scripts', {}) else 'missing'}")
            print(f"  Dependencies: {len(package_data.get('dependencies', {}))}")
            print(f"  Dev Dependencies: {len(package_data.get('devDependencies', {}))}")
            
            # Check for important dependencies
            deps = package_data.get('dependencies', {})
            important_deps = ['react', 'react-dom', 'axios', 'react-router-dom']
            found_deps = [dep for dep in important_deps if dep in deps]
            print(f"  Important Dependencies: {len(found_deps)}/{len(important_deps)}")
            
        except Exception as e:
            print(f"  Package.json Error: {e}")
    else:
        print("  Package.json: MISSING")
    
    # Vite config
    vite_config = frontend_path / 'vite.config.js'
    if vite_config.exists():
        print("  Vite Config: PRESENT")
    else:
        print("  Vite Config: MISSING")
    
    # Environment files
    env_files = ['.env', '.env.example', '.env.local']
    found_env = []
    for env_file in env_files:
        env_path = frontend_path / env_file
        if env_path.exists():
            found_env.append(env_file)
    
    print(f"  Environment Files: {len(found_env)} found")
    
    # Build directory
    build_dir = frontend_path / 'dist'
    if build_dir.exists():
        print("  Build Directory: EXISTS")
    else:
        print("  Build Directory: NOT BUILT")
    
    return True


def assess_deployment_requirements():
    """Assess deployment requirements for PythonAnywhere and Vercel."""
    print("\n" + "=" * 80)
    print("DEPLOYMENT REQUIREMENTS ASSESSMENT")
    print("=" * 80)
    
    print("\nPYTHONANYWHERE DEPLOYMENT (BACKEND):")
    
    print("  REQUIREMENTS:")
    print("    - Python version: 3.8+ recommended")
    print("    - Virtual environment setup")
    print("    - requirements.txt file")
    print("    - wsgi.py configuration")
    print("    - Static files configuration")
    print("    - Database configuration")
    
    # Check requirements.txt
    project_root = Path('/home/aqi/Documents/Projects/Insuarance_Churn_Prediction')
    requirements_file = project_root / 'Backend' / 'requirements.txt'
    
    if requirements_file.exists():
        print("    - requirements.txt: FOUND")
        try:
            with open(requirements_file, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(f"      Dependencies: {len(requirements)}")
        except Exception as e:
            print(f"      Error reading: {e}")
    else:
        print("    - requirements.txt: MISSING")
    
    # Check wsgi.py
    wsgi_file = project_root / 'Backend' / 'nyaradzo_backend' / 'wsgi.py'
    if wsgi_file.exists():
        print("    - wsgi.py: FOUND")
    else:
        print("    - wsgi.py: MISSING")
    
    print("\n  ENVIRONMENT VARIABLES NEEDED:")
    backend_env_vars = [
        "SECRET_KEY",
        "DEBUG=False",
        "ALLOWED_HOSTS=your-domain.pythonanywhere.com",
        "DATABASE_URL=postgresql://username:password@host/dbname",
        "JWT_SECRET_KEY",
        "CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app"
    ]
    
    for var in backend_env_vars:
        print(f"    - {var}")
    
    print("\nVERCEL DEPLOYMENT (FRONTEND):")
    
    print("  REQUIREMENTS:")
    print("    - package.json with build script")
    print("    - vercel.json configuration (optional)")
    print("    - Environment variables for API URL")
    print("    - Build optimization")
    
    # Check vercel.json
    vercel_config = project_root / 'Frontend' / 'vercel.json'
    if vercel_config.exists():
        print("    - vercel.json: FOUND")
    else:
        print("    - vercel.json: NOT REQUIRED (auto-detection)")
    
    print("\n  ENVIRONMENT VARIABLES NEEDED:")
    frontend_env_vars = [
        "VITE_API_URL=https://your-domain.pythonanywhere.com/api",
        "NODE_ENV=production"
    ]
    
    for var in frontend_env_vars:
        print(f"    - {var}")
    
    return True


def generate_deployment_checklist():
    """Generate comprehensive deployment checklist."""
    print("\n" + "=" * 80)
    print("DEPLOYMENT CHECKLIST")
    print("=" * 80)
    
    checklist = {
        "backend": [
            "Create PythonAnywhere account",
            "Set up virtual environment",
            "Upload backend code",
            "Install requirements.txt dependencies",
            "Configure database (PostgreSQL recommended)",
            "Set environment variables",
            "Run database migrations",
            "Create superuser account",
            "Configure static files",
            "Configure WSGI application",
            "Test API endpoints"
        ],
        "frontend": [
            "Create Vercel account",
            "Connect Git repository",
            "Configure build settings",
            "Set environment variables",
            "Deploy to Vercel",
            "Test frontend functionality",
            "Verify API connectivity",
            "Test authentication flow"
        ],
        "post_deployment": [
            "Test complete user flow",
            "Verify all API endpoints",
            "Check database connectivity",
            "Test authentication",
            "Monitor error logs",
            "Set up monitoring/alerts",
            "Configure backup strategy"
        ]
    }
    
    for category, items in checklist.items():
        print(f"\n{category.upper()}:")
        for i, item in enumerate(items, 1):
            print(f"  [ ] {i}. {item}")
    
    return checklist


def main():
    """Main assessment function."""
    print("NYARADZO ASSURANCE MANAGEMENT SYSTEM")
    print("PRODUCTION READINESS ASSESSMENT")
    print("=" * 80)
    
    # Run all assessments
    structure = scan_project_structure()
    env_vars = assess_environment_variables()
    database = assess_database_readiness()
    security = assess_security_settings()
    api = assess_api_endpoints()
    frontend = assess_frontend_readiness()
    deployment = assess_deployment_requirements()
    checklist = generate_deployment_checklist()
    
    # Overall assessment
    print("\n" + "=" * 80)
    print("OVERALL PRODUCTION READINESS")
    print("=" * 80)
    
    assessments = [
        ("Project Structure", True),
        ("Environment Variables", len(env_vars['backend_env_files']) > 0),
        ("Database", database),
        ("Security", security),
        ("API Endpoints", api),
        ("Frontend", frontend),
        ("Deployment Requirements", True)
    ]
    
    ready_count = 0
    for name, status in assessments:
        status_icon = "GREEN" if status else "YELLOW"
        print(f"  {name}: {status_icon}")
        if status:
            ready_count += 1
    
    print(f"\nREADINESS SCORE: {ready_count}/{len(assessments)}")
    
    if ready_count >= 6:
        print("\nSTATUS: READY FOR DEPLOYMENT")
        print("The project appears to be well-prepared for production deployment.")
        print("Follow the checklist above for smooth deployment to PythonAnywhere and Vercel.")
    else:
        print("\nSTATUS: NEEDS ATTENTION")
        print("Some areas require attention before production deployment.")
        print("Review the YELLOW items above and address the issues.")
    
    print("\n" + "=" * 80)
    print("ASSESSMENT COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
