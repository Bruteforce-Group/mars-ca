#!/usr/bin/env python3
"""
Create test policy matching UI format exactly
"""

import os
import json
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def create_test_policy():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
        'Content-Type': 'application/json'
    })

    print("🔍 Creating test policy to match UI...")
    
    # First get the Mac group ID
    response = session.get('https://192.168.22.194/proxy/network/api/s/default/rest/usergroup')
    mac_group_id = None
    if response.status_code == 200:
        for group in response.json().get('data', []):
            if group.get('name') == 'Mac':
                mac_group_id = group.get('_id')
                break
    
    if not mac_group_id:
        print("❌ Could not find Mac group ID")
        return
        
    print(f"📋 Found Mac group ID: {mac_group_id}")
    
    # Create policy matching UI exactly
    policy = {
        "name": "TEST2",  # Using TEST2 since TEST already exists
        "enabled": True,
        "secure": {
            "internet": {
                "enabled": True,
                "type": "allowlist",
                "everything": True
            },
            "schedule": {
                "type": "always"
            },
            "local": {
                "enabled": True,
                "type": "allowlist",
                "everything": True
            }
        },
        "route": {
            "enabled": True,
            "type": "all_traffic",
            "interface": "Telstra 1000/400 FTTP v1",
            "kill_switch": True
        },
        "qos": {
            "enabled": True,
            "type": "all_traffic",
            "mode": "limit",
            "download_limit": 25,
            "upload_limit": 10,
            "burst": "off",
            "schedule": {
                "type": "always"
            }
        },
        "match": {
            "type": "devices",
            "groups": [mac_group_id]
        }
    }
    
    print("\n📝 Using policy format:")
    print(json.dumps(policy, indent=2))
    
    try:
        response = session.post(
            'https://192.168.22.194/proxy/network/api/s/default/rest/object-policy',
            json=policy
        )
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✅ Policy created successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return False

def main():
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    return create_test_policy()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)