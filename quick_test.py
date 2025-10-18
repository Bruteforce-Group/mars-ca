#!/usr/bin/env python3
import os
import requests
import json
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def test_unifi_controller():
    print('🔍 Testing UniFi Controller Connection')
    print('======================================')
    
    # Configuration
    controller = '192.168.22.194'
    username = 'root'
    password = os.getenv('UNIFI_PASSWORD_MARS')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    print(f'Controller IP: {controller}')
    print(f'Username: {username}')
    print(f'Password: {"[set]" if password else "[not set]"}')
    print(f'API Key: {api_key[:8]}... {"[set]" if api_key else "[not set]"}')
    print()
    
    session = requests.Session()
    session.verify = False
    
    # Test basic connectivity
    try:
        print('Testing basic connectivity...')
        response = session.get(f'https://{controller}/', timeout=5)
        print(f'Basic connection: {response.status_code}')
        if response.status_code == 200:
            print('✅ Controller web interface accessible')
    except Exception as e:
        print(f'❌ Connection error: {str(e)}')
        return
    
    # Test API key authentication
    print('\nTesting API key authentication...')
    try:
        headers = {'X-API-Key': api_key}
        response = session.get(f'https://{controller}/api/self', headers=headers, timeout=5)
        print(f'API auth status: {response.status_code}')
        if response.status_code == 200:
            print('✅ API key authentication successful!')
            data = response.json()
            print(f'Controller info: {json.dumps(data, indent=2)}')
            return True
    except Exception as e:
        print(f'API auth error: {str(e)}')
    
    # Test password authentication
    print('\nTrying password authentication...')
    login_data = {
        'username': username,
        'password': password,
        'remember': True
    }
    
    auth_endpoints = [
        '/api/auth/login',
        '/api/login',
        '/proxy/network/api/login'
    ]
    
    for endpoint in auth_endpoints:
        try:
            url = f'https://{controller}{endpoint}'
            print(f'\nTrying: {url}')
            response = session.post(url, json=login_data, timeout=5)
            print(f'Status: {response.status_code}')
            
            if response.status_code == 200:
                print('✅ Password authentication successful!')
                if 'x-csrf-token' in response.headers:
                    print('Got CSRF token')
                return True
            elif response.status_code == 401:
                print('Authentication failed - wrong credentials')
            elif response.status_code == 404:
                print('Endpoint not found - trying next')
            else:
                print(f'Unexpected response: {response.text[:100]}')
        except Exception as e:
            print(f'Error: {str(e)}')

    return False

if __name__ == '__main__':
    test_unifi_controller()