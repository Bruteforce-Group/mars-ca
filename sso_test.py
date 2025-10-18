#!/usr/bin/env python3
import os
import requests
import json
import time
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
    
    # Test SSO authentication first
    print('Attempting SSO authentication...')
    try:
        # Get SSO login page
        response = session.get(f'https://{controller}/manage/account/login', timeout=5)
        print(f'SSO page status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ SSO login page accessible')
            
            # Try SSO login
            login_data = {
                'username': username,
                'password': password,
                'rememberMe': True,
                'redirect': '/manage'
            }
            
            response = session.post(
                f'https://{controller}/api/auth/login',
                json=login_data,
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )
            print(f'SSO login status: {response.status_code}')
            
            if response.status_code == 200:
                print('✅ SSO login successful!')
                # Get any tokens or cookies
                print('Cookies:', session.cookies.get_dict())
                return True
            else:
                print(f'SSO response: {response.text[:200]}')
    except Exception as e:
        print(f'SSO error: {str(e)}')
    
    # If SSO fails, try legacy authentication
    print('\nTrying legacy authentication methods...')
    
    # Try different usernames
    usernames = ['root', 'admin', username]
    for test_username in usernames:
        print(f'\nTesting with username: {test_username}')
        login_data = {
            'username': test_username,
            'password': password,
            'strict': True
        }
        
        try:
            response = session.post(
                f'https://{controller}/api/login',
                json=login_data,
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )
            print(f'Auth status: {response.status_code}')
            
            if response.status_code == 200:
                print('✅ Authentication successful!')
                return True
            else:
                print(f'Response: {response.text[:100]}')
        except Exception as e:
            print(f'Error: {str(e)}')
    
    print('\n❌ All authentication attempts failed')
    print('\nPossible solutions:')
    print('1. Check if account is locked in UniFi settings')
    print('2. Verify correct username (might not be "root")')
    print('3. Try accessing web interface manually to confirm credentials')
    print('4. Check if SSO is required for this controller')
    return False

if __name__ == '__main__':
    test_unifi_controller()