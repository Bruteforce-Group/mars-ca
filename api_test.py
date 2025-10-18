#!/usr/bin/env python3
import os
import requests
import json
import time
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def test_unifi_api():
    print('🔍 Testing UniFi API Access')
    print('===========================')
    
    # Configuration
    controller = '192.168.22.194'
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    username = os.getenv('UNIFI_USERNAME_MARS')
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
            
            try:
                data = response.json()
                print(f'Response: {json.dumps(data, indent=2)[:500]}')
            except:
                print(f'Response (text): {response.text[:200]}')
                
            print(f'Headers: {dict(response.headers)}')
            return response
        except Exception as e:
            print(f'Error: {str(e)}')
            return None
    
    # Step 1: Test basic connectivity
    print('\n1️⃣  Testing basic connectivity...')
    response = try_request('GET', '/')
    if not response or response.status_code not in [200, 302]:
        print('❌ Cannot reach controller')
        return False
    
    # Step 2: Try API key auth first
    print('\n2️⃣  Testing API key authentication...')
    session.headers.update({
        'X-API-Key': api_key,
        'Authorization': f'Bearer {api_key}'
    })
    
    response = try_request('GET', '/api/s/default/stat/device')
    if response and response.status_code == 200:
        print('✅ API key authentication successful!')
        return True
    
    # Step 3: Try modern auth flow
    print('\n3️⃣  Testing modern authentication flow...')
    session.headers.pop('X-API-Key', None)
    session.headers.pop('Authorization', None)
    
    login_data = {
        'username': username,
        'password': password,
        'rememberMe': True,
        'type': 'local'
    }
    
    response = try_request('POST', '/api/auth/login', json=login_data)
    if response and response.status_code == 200:
        print('✅ Modern authentication successful!')
        
        if 'x-csrf-token' in response.headers:
            session.headers['X-CSRF-Token'] = response.headers['x-csrf-token']
            print('Got CSRF token')
        
        # Try to get network data
        print('\nTesting API access...')
        response = try_request('GET', '/api/s/default/rest/networkconf')
        if response and response.status_code == 200:
            print('✅ Can access network configuration!')
            return True
    
    # Step 4: Try legacy auth if modern fails
    print('\n4️⃣  Testing legacy authentication...')
    login_data = {
        'username': username,
        'password': password,
        'remember': True,
        'strict': True
    }
    
    response = try_request('POST', '/api/login', json=login_data)
    if response and response.status_code == 200:
        print('✅ Legacy authentication successful!')
        return True
    
    print('\n❌ All authentication methods failed')
    print('\nTroubleshooting steps:')
    print('1. Check if username/password are correct')
    print('2. Check if API key has proper permissions')
    print('3. Try accessing the web interface manually')
    print('4. Check controller logs for auth failures')
    return False

if __name__ == '__main__':
    test_unifi_api()