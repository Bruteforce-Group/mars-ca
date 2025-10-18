#!/usr/bin/env python3
import os
import requests
import json
import time
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def test_unifi_api():
    print('🔍 Testing UniFi Network Application')
    print('===================================')
    
    # Configuration
    controller = '192.168.22.194'
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    username = os.getenv('UNIFI_USERNAME_MARS', 'root')
    password = os.getenv('UNIFI_PASSWORD_MARS')
    
    # Initial setup
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    print(f'Controller: {controller}')
    print(f'API Key: {api_key[:8]}***')
    print(f'Username: {username}')
    print()
    
    def try_request(method, url, **kwargs):
        full_url = f'https://{controller}{url}'
        print(f'{method} {full_url}')
        try:
            response = session.request(method, full_url, timeout=5, **kwargs)
            print(f'Status: {response.status_code}')
            print('Headers:', dict(response.headers))
            print('Cookies:', session.cookies.get_dict())
            
            try:
                data = response.json()
                print(f'Response: {json.dumps(data, indent=2)[:500]}')
            except:
                print(f'Response (text): {response.text[:200]}')
            return response
        except Exception as e:
            print(f'Error: {str(e)}')
            return None
    
    # Step 1: Get initial page and check type
    print('\n1️⃣  Detecting controller type...')
    response = try_request('GET', '/manage/site-map')
    
    is_modern = False
    is_classic = False
    
    if response:
        if response.status_code == 200:
            print('✅ Detected modern UniFi OS')
            is_modern = True
        elif response.status_code == 404:
            print('Detected classic controller')
            is_classic = True
    
    # Step 2: Try modern authentication
    if is_modern:
        print('\n2️⃣  Testing modern authentication...')
        # First get CSRF token
        response = try_request('GET', '/api/users/self')
        if response and 'x-csrf-token' in response.headers:
            csrf_token = response.headers['x-csrf-token']
            session.headers['X-CSRF-Token'] = csrf_token
            print(f'Got CSRF token: {csrf_token}')
        
        login_data = {
            'username': username,
            'password': password,
            'rememberMe': True,
            'token': csrf_token if 'csrf_token' in locals() else ''
        }
        
        response = try_request('POST', '/api/auth/login', json=login_data)
        if response and response.status_code == 200:
            print('✅ Modern authentication successful!')
            
            # Try to get network data
            print('\nTesting network access...')
            response = try_request('GET', '/proxy/network/api/v2/sites/default/settings')
            if response and response.status_code == 200:
                print('✅ Can access network settings!')
                return True
    
    # Step 3: Try legacy API paths
    print('\n3️⃣  Testing legacy API paths...')
    legacy_paths = [
        '/api/s/default/stat/device',
        '/v1/api/site/default/devices',
        '/v2/api/site/default/devices',
        '/proxy/network/api/s/default/stat/device'
    ]
    
    for path in legacy_paths:
        print(f'\nTrying path: {path}')
        response = try_request('GET', path)
        if response and response.status_code == 200:
            print(f'✅ Found working API path: {path}')
            return True
    
    # Step 4: Try direct network access
    print('\n4️⃣  Testing direct network access...')
    network_paths = [
        '/proxy/network/api/v2/networks',
        '/v2/api/site/default/networks',
        '/proxy/network/v2/api/site/default/networks'
    ]
    
    for path in network_paths:
        print(f'\nTrying path: {path}')
        response = try_request('GET', path)
        if response and response.status_code == 200:
            print(f'✅ Found working network API: {path}')
            return True
    
    print('\n❌ Could not establish API access')
    print('\nTroubleshooting Information:')
    print('1. This appears to be a modern UniFi OS device')
    print('2. API endpoints suggest UDM/UDM Pro configuration')
    print('3. Authentication is failing - verify credentials')
    print('4. Try accessing web interface at:')
    print(f'   https://{controller}/manage/network/default/settings/networks')
    return False

if __name__ == '__main__':
    test_unifi_api()