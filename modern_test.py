#!/usr/bin/env python3
import os
import requests
import json
import base64
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def test_unifi_controller():
    print('🔍 Testing UniFi Controller Connection')
    print('======================================')
    
    # Configuration
    controller = '192.168.22.194'
    username = os.getenv('UNIFI_USERNAME_MARS', 'root')  # Try environment username if set
    password = os.getenv('UNIFI_PASSWORD_MARS')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    print(f'Controller IP: {controller}')
    print(f'Username: {username}')
    print(f'Password: {"[set]" if password else "[not set]"}')
    print(f'API Key: {api_key[:8]}... {"[set]" if api_key else "[not set]"}')
    print()
    
    session = requests.Session()
    session.verify = False
    
    # Try to get the login page first to get any necessary cookies/tokens
    print('Fetching initial page...')
    try:
        response = session.get(f'https://{controller}/', timeout=5)
        print(f'Initial page status: {response.status_code}')
        if response.status_code == 200:
            print('✅ Controller reachable')
            print('Cookies:', session.cookies.get_dict())
        else:
            print('❌ Controller not reachable')
            return False
    except Exception as e:
        print(f'Error accessing controller: {str(e)}')
        return False
    
    # Try different auth methods
    auth_methods = [
        # Method 1: Basic API key
        {
            'url': '/api/self',
            'method': 'GET',
            'headers': {'Authorization': f'Bearer {api_key}'},
            'name': 'API Key (Bearer)'
        },
        # Method 2: Basic Auth
        {
            'url': '/api/self',
            'method': 'GET',
            'headers': {'Authorization': f'Basic {base64.b64encode(f"{username}:{password}".encode()).decode()}'},
            'name': 'Basic Auth'
        },
        # Method 3: Modern auth with token
        {
            'url': '/api/auth/login',
            'method': 'POST',
            'json': {'username': username, 'password': password},
            'name': 'Modern Login'
        },
        # Method 4: Legacy auth
        {
            'url': '/api/login',
            'method': 'POST',
            'json': {'username': username, 'password': password, 'remember': True},
            'name': 'Legacy Login'
        }
    ]
    
    print('\nTrying authentication methods...')
    for method in auth_methods:
        try:
            print(f'\nTesting {method["name"]}...')
            url = f'https://{controller}{method["url"]}'
            print(f'URL: {url}')
            
            kwargs = {
                'timeout': 5,
                'headers': {'Content-Type': 'application/json'}
            }
            
            if 'headers' in method:
                kwargs['headers'].update(method['headers'])
            if 'json' in method:
                kwargs['json'] = method['json']
            
            response = session.request(method['method'], url, **kwargs)
            print(f'Status: {response.status_code}')
            
            try:
                data = response.json()
                print(f'Response: {json.dumps(data, indent=2)}')
            except:
                print('Response not JSON')
                print(f'Content: {response.text[:200]}')
            
            if response.status_code == 200:
                print('✅ Authentication successful!')
                print('Headers:', dict(response.headers))
                print('Cookies:', session.cookies.get_dict())
                return True
                
        except Exception as e:
            print(f'Error: {str(e)}')
    
    print('\n❌ Authentication failed')
    print('\nDebug Information:')
    print('1. Check if controller is in setup mode')
    print('2. Try accessing web interface manually')
    print('3. Verify network policy allows API access')
    print('4. Check controller logs for auth failures')
    return False

if __name__ == '__main__':
    test_unifi_controller()