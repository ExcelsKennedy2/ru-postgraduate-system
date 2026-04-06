#!/usr/bin/env python
import requests
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'syncpath.settings')

import django
django.setup()

from users.models import User

def test_supervisor_login():
    """Test supervisor login flow"""
    print("Testing supervisor login...")

    # Get supervisor credentials
    supervisor = User.objects.filter(role='supervisor').first()
    if not supervisor:
        print("❌ No supervisor user found")
        return False

    print(f"Supervisor credentials: unique_id={supervisor.unique_id}, username={supervisor.username}")

    # Create a session to maintain cookies
    session = requests.Session()

    # First, try to access supervisor dashboard without login (should redirect to login)
    print("\n1. Testing access to supervisor dashboard without login...")
    response = session.get('http://127.0.0.1:8000/supervisor/dashboard/', allow_redirects=False)
    print(f"Status: {response.status_code}")
    if response.status_code == 302:  # Redirect
        redirect_url = response.headers.get('Location', '')
        print(f"Redirected to: {redirect_url}")
        if 'login' in redirect_url and 'next=' in redirect_url:
            print("✅ Correctly redirected to login with next parameter")
        else:
            print("❌ Not redirected to login with next parameter")
            return False
    else:
        print("❌ Expected redirect, got different response")
        return False

    # Now try to login
    print("\n2. Testing login...")
    login_data = {
        'unique_id': supervisor.unique_id,
        'password': 'password123',  # Assuming default password
        'next': '/supervisor/dashboard/'
    }

    response = session.post('http://127.0.0.1:8000/users/login/', data=login_data, allow_redirects=False)
    print(f"Login response status: {response.status_code}")

    if response.status_code == 302:  # Redirect after successful login
        redirect_url = response.headers.get('Location', '')
        print(f"Redirected to: {redirect_url}")
        if '/supervisor/dashboard/' in redirect_url:
            print("✅ Successfully redirected to supervisor dashboard!")
            return True
        else:
            print(f"❌ Redirected to wrong URL: {redirect_url}")
            return False
    else:
        print(f"❌ Login failed with status {response.status_code}")
        # Check if there was an error message
        if 'Invalid' in response.text:
            print("❌ Invalid credentials - check password")
        return False

if __name__ == '__main__':
    success = test_supervisor_login()
    if success:
        print("\n🎉 Supervisor login test PASSED!")
    else:
        print("\n💥 Supervisor login test FAILED!")
        sys.exit(1)