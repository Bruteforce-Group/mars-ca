#!/usr/bin/env python3
"""
Enhanced UniFi Authentication Diagnostic Script
Tests various authentication methods and provides detailed diagnostics
"""

import os
import requests
import json
import time
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def test_unifi_os_authentication():
    """Test UniFi OS authentication with enhanced diagnostics"""
    
    host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', 'mars.int.bozza.au')
    username = os.getenv('UNIFI_USERNAME_MARS', 'root')
    password = os.getenv('UNIFI_PASSWORD_MARS')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    print(f"🔍 Enhanced UniFi OS Authentication Test")
    print(f"📡 Controller: {host}")
    print(f"👤 Username: {username}")
    print(f"🔑 API Key: {'✓ Set' if api_key else '✗ Not set'}")
    print(f"🔒 Password: {'✓ Set' if password else '✗ Not set'}")
    print("=" * 80)
    
    session = requests.Session()
    session.verify = False
    
    # Test different UniFi OS endpoints
    base_url = f"https://{host}"
    
    # 1. Test UniFi OS endpoints
    print(f"\n🌐 Testing UniFi OS Endpoints:")
    
    endpoints_to_test = [
        "/api/auth",
        "/api/bootstrap", 
        "/api/users/self",
        "/proxy/network/api/auth",
        "/proxy/network/api/self",
        "/proxy/network/api/bootstrap",
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = session.get(f"{base_url}{endpoint}", timeout=5)
            print(f"  {endpoint}: {response.status_code}")
            if response.status_code != 404:
                try:
                    data = response.json()
                    if 'error' in data:
                        print(f"    Error: {data['error'].get('message', 'Unknown')}")
                    elif 'data' in data:
                        print(f"    ✓ Data available")
                except:
                    print(f"    Non-JSON response")
        except Exception as e:
            print(f"  {endpoint}: ✗ Failed - {str(e)}")
    
    # 2. Test API Key Authentication on various endpoints
    if api_key:
        print(f"\n🔑 Testing API Key Authentication:")
        headers = {'X-API-Key': api_key, 'Content-Type': 'application/json'}
        
        api_endpoints = [
            "/api/auth",
            "/api/users/self",
            "/api/bootstrap",
            "/proxy/network/api/self",
            "/proxy/network/api/auth",
            "/proxy/network/api/bootstrap",
        ]
        
        for endpoint in api_endpoints:
            try:
                response = session.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                print(f"  {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"    ✅ SUCCESS! API Key works with {endpoint}")
                    try:
                        data = response.json()
                        if 'data' in data:
                            print(f"    📊 Response contains data")
                        return True
                    except:
                        pass
                elif response.status_code in [401, 403]:
                    try:
                        error_data = response.json()
                        print(f"    ❌ {error_data}")
                    except:
                        print(f"    ❌ Authentication failed")
            except Exception as e:
                print(f"  {endpoint}: ✗ Failed - {str(e)}")
    
    # 3. Test UniFi OS Login
    if username and password:
        print(f"\n🔐 Testing UniFi OS Login:")
        
        login_endpoints = [
            "/api/auth/login",
            "/api/login", 
            "/proxy/network/api/auth/login",
            "/proxy/network/api/login",
        ]
        
        for login_endpoint in login_endpoints:
            try:
                # Try UniFi OS login format
                login_data = {
                    "username": username,
                    "password": password,
                    "rememberMe": True
                }
                
                response = session.post(f"{base_url}{login_endpoint}", json=login_data, timeout=10)
                print(f"  {login_endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"    ✅ LOGIN SUCCESS with {login_endpoint}!")
                    
                    # Test authenticated request
                    try:
                        test_response = session.get(f"{base_url}/api/users/self", timeout=5)
                        print(f"    🔍 Auth test: {test_response.status_code}")
                        if test_response.status_code == 200:
                            return True
                    except Exception as e:
                        print(f"    ⚠️ Auth test failed: {str(e)}")
                        
                else:
                    try:
                        error_data = response.json()
                        if 'message' in error_data:
                            print(f"    ❌ {error_data['message']}")
                        elif 'error' in error_data:
                            print(f"    ❌ {error_data['error']}")
                        else:
                            print(f"    ❌ {error_data}")
                    except:
                        print(f"    ❌ Login failed - Status {response.status_code}")
                        
            except Exception as e:
                print(f"  {login_endpoint}: ✗ Failed - {str(e)}")
    
    # 4. Check for account lockout information
    print(f"\n🔒 Account Status Diagnostics:")
    try:
        # Try to get any public information about account status
        response = session.get(f"{base_url}/api/auth", timeout=5)
        if response.status_code == 403:
            try:
                error_data = response.json()
                if 'AUTHENTICATION_FAILED_ACCOUNT_LOCKED' in str(error_data):
                    print("  ⚠️ ACCOUNT IS LOCKED")
                    print("  📝 To resolve:")
                    print("    1. Wait 30 minutes for automatic unlock")
                    print("    2. Access web interface directly and unlock manually")
                    print("    3. Reset password if needed")
                    print("    4. Generate new API key after unlock")
            except:
                pass
    except Exception as e:
        print(f"  Status check failed: {str(e)}")
    
    print(f"\n❌ All authentication methods failed")
    print(f"\n📋 RECOMMENDATIONS:")
    print(f"1. 🌐 Access https://{host} directly in browser")
    print(f"2. 🔓 Check if account is locked and unlock it")
    print(f"3. 🔑 Generate new API key in Settings > Admins")
    print(f"4. 🔄 Verify username and password are correct")
    print(f"5. ⏳ Wait for account lockout to expire (usually 30 min)")
    
    return False

if __name__ == "__main__":
    success = test_unifi_os_authentication()
    exit(0 if success else 1)