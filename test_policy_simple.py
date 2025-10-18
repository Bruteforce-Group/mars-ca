#!/usr/bin/env python3
"""
Test policy creation with simpler format
"""

import os
import json
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def create_simple_policy():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
        'Content-Type': 'application/json'
    })

    print("🔍 Creating simple test policy...")
    
    # First get the Mac group ID
    response = session.get('https://192.168.22.194/proxy/network/api/s/default/rest/usergroup')
    mac_group_id = None
    if response.status_code == 200:
        groups = response.json().get('data', [])
        print("\n📋 Available Groups:")
        for group in groups:
            name = group.get('name')
            group_id = group.get('_id')
            print(f"   • {name}: {group_id}")
            if name == 'Mac':
                mac_group_id = group_id
    
    if not mac_group_id:
        print("❌ Could not find Mac group ID")
        return
        
    # Try different simple formats
    test_policies = [
        # Test 1: Route only
        {
            "name": "Test_Route",
            "enabled": True,
            "device_groups": [mac_group_id],
            "route": {
                "enabled": True,
                "interface": "Telstra 1000/400 FTTP v1",
                "kill_switch": True
            }
        },
        # Test 2: QoS only
        {
            "name": "Test_QoS",
            "enabled": True,
            "device_groups": [mac_group_id],
            "qos": {
                "enabled": True,
                "rate_download": 25,
                "rate_upload": 10
            }
        },
        # Test 3: Secure only with just internet
        {
            "name": "Test_Secure",
            "enabled": True,
            "device_groups": [mac_group_id],
            "secure": {
                "internet_access": True,
                "internet_type": "allowlist"
            }
        },
        # Test 4: Different device format
        {
            "name": "Test_Different",
            "enabled": True,
            "match_type": "devices",
            "match_groups": [mac_group_id],
            "action": "route",
            "interface": "Telstra 1000/400 FTTP v1"
        },
        # Test 5: Most basic
        {
            "name": "Test_Basic",
            "groups": [mac_group_id],
            "action": "allow"
        }
    ]
    
    # Try different API endpoints too
    endpoints = [
        'rest/object-policy',
        'rest/policy',
        'api/s/default/cmd/stamgr'
    ]
    
    for i, policy in enumerate(test_policies, 1):
        print(f"\n📝 Testing format {i}:")
        print(json.dumps(policy, indent=2))
        
        for endpoint in endpoints:
            print(f"\n   🔌 Trying endpoint: {endpoint}")
            try:
                response = session.post(
                    f'https://192.168.22.194/proxy/network/api/s/default/{endpoint}',
                    json=policy
                )
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
                if response.status_code == 200:
                    print("   ✅ Success!")
                    print("\nFound working format!")
                    print(f"Endpoint: {endpoint}")
                    print("Policy format:")
                    print(json.dumps(policy, indent=2))
                    return True
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
            
        print("\nTrying next format...")

    print("\n❌ No working format found")
    return False

def main():
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    return create_simple_policy()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)