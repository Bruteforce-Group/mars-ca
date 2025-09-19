#!/usr/bin/env python3
"""
UniFi Authentication Test Script
Tests different authentication methods and endpoints to diagnose credential issues
"""

import os
import requests
import json
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def test_unifi_authentication():
    """Test various UniFi authentication methods and endpoints"""
    
    # Load credentials from environment
    host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', 'mars.int.bozza.au')
    username = os.getenv('UNIFI_USERNAME_MARS', 'root')
    password = os.getenv('UNIFI_PASSWORD_MARS')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    print(f"Testing UniFi Controller: {host}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password) if password else 'Not set'}")
    print(f"API Key: {'*' * len(api_key) if api_key else 'Not set'}")
    print("=" * 60)
    
    # Test different ports and endpoints
    test_configs = [
        {
            'port': 443,
            'name': 'UDM/UDM Pro (443)',
            'endpoints': {
                'login': '/api/auth/login',
                'test': '/api/self',
                'status': '/api/status'
            }
        },
        {
            'port': 8443,
            'name': 'Classic Controller (8443)',
            'endpoints': {
                'login': '/api/login',
                'test': '/api/self',
                'status': '/status'
            }
        },
        {
            'port': 443,
            'name': 'Alternative (443)',
            'endpoints': {
                'login': '/api/login',
                'test': '/api/self',
                'status': '/api/status'
            }
        }
    ]
    
    session = requests.Session()
    session.verify = False
    
    for config in test_configs:
        port = config['port']
        name = config['name']
        endpoints = config['endpoints']
        base_url = f"https://{host}:{port}"
        
        print(f"\nTesting {name}:")
        print(f"Base URL: {base_url}")
        
        # Test basic connectivity
        try:
            response = session.get(base_url, timeout=5)
            print(f"  ✓ Basic connectivity: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Basic connectivity failed: {str(e)}")
            continue
        
        # Test status endpoint
        try:
            response = session.get(f"{base_url}{endpoints['status']}", timeout=5)
            print(f"  ✓ Status endpoint: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'version' in str(data):
                        print(f"    Controller info available")
                except:
                    pass
        except Exception as e:
            print(f"  ✗ Status endpoint failed: {str(e)}")
        
        # Test API key authentication
        if api_key:
            try:
                headers = {
                    'X-API-Key': api_key,
                    'Content-Type': 'application/json'
                }
                response = session.get(f"{base_url}{endpoints['test']}", headers=headers, timeout=5)
                print(f"  API Key Auth: {response.status_code}")
                if response.status_code == 200:
                    print(f"    ✓ API key authentication successful!")
                    return True
                else:
                    try:
                        error_data = response.json()
                        print(f"    ✗ API key error: {error_data}")
                    except:
                        print(f"    ✗ API key error: {response.text}")
            except Exception as e:
                print(f"  ✗ API key authentication failed: {str(e)}")
        else:
            print(f"  ⊘ API key not provided")
        
        # Test username/password authentication
        if username and password:
            try:
                login_data = {
                    "username": username,
                    "password": password
                }
                
                # Add additional fields for UDM controllers
                if port == 443:
                    login_data.update({
                        "remember": True,
                        "strict": True
                    })
                
                response = session.post(
                    f"{base_url}{endpoints['login']}",
                    json=login_data,
                    timeout=10
                )
                
                print(f"  Username/Password Auth: {response.status_code}")
                if response.status_code == 200:
                    print(f"    ✓ Username/password authentication successful!")
                    
                    # Test authenticated request
                    try:
                        test_response = session.get(f"{base_url}{endpoints['test']}", timeout=5)
                        print(f"    ✓ Authenticated test request: {test_response.status_code}")
                        if test_response.status_code == 200:
                            return True
                    except Exception as e:
                        print(f"    ✗ Authenticated test failed: {str(e)}")
                else:
                    try:
                        error_data = response.json()
                        print(f"    ✗ Login error: {error_data}")
                    except:
                        print(f"    ✗ Login error: {response.text}")
            except Exception as e:
                print(f"  ✗ Username/password authentication failed: {str(e)}")
        else:
            print(f"  ⊘ Username/password not provided")
    
    print("\n" + "=" * 60)
    print("AUTHENTICATION DIAGNOSIS:")
    print("\nAll authentication attempts failed. Possible causes:")
    print("1. Invalid credentials - password may have changed")
    print("2. Invalid API key - key may be expired or revoked")
    print("3. Wrong username - may not be 'root'")
    print("4. Controller type mismatch - may be different UniFi system")
    print("5. Network access issues - firewall or routing problems")
    print("6. Controller not running or in maintenance mode")
    
    print("\nRECOMMENDED ACTIONS:")
    print("1. Log into UniFi controller web interface to verify credentials")
    print("2. Generate new API key if using API authentication")
    print("3. Check if controller hostname/IP is correct")
    print("4. Verify network connectivity to the controller")
    print("5. Check controller logs for authentication attempts")
    
    return False

if __name__ == "__main__":
    success = test_unifi_authentication()
    exit(0 if success else 1)