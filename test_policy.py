#!/usr/bin/env python3
"""
Test creation of a single basic policy to understand required format
"""

import os
import json
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def test_policy():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
        'Content-Type': 'application/json'
    })

    print("🔍 Testing basic policy creation")
    
    # Get the Mac group ID first
    response = session.get('https://mars.int.bozza.au/proxy/network/api/s/default/rest/usergroup')
    groups = {}
    if response.status_code == 200:
        for group in response.json().get('data', []):
            groups[group.get('name')] = group.get('_id')
    
    mac_group_id = groups.get('Mac')
    if not mac_group_id:
        print("❌ Could not find Mac group ID")
        return
        
    print(f"📋 Found Mac group ID: {mac_group_id}")
    
    # Try different policy formats
    test_policies = [
        # Test 1: Basic secure policy
        {
            "name": "Test_Basic_Policy",
            "enabled": True,
            "type": "secure",
            "source_type": "group",
            "source_group_id": mac_group_id,
            "internet": {
                "enabled": True,
                "type": "allow"
            }
        },
        # Test 2: Different format
        {
            "name": "Test_Basic_Policy_2",
            "enabled": True,
            "policy_type": "secure",
            "source": {
                "type": "group",
                "id": mac_group_id
            },
            "actions": {
                "internet": "allow"
            }
        },
        # Test 3: Minimal format
        {
            "name": "Test_Basic_Policy_3",
            "source": mac_group_id,
            "type": "secure",
            "action": "allow"
        },
        # Test 4: Very basic
        {
            "name": "Test_Basic_Policy_4",
            "group": mac_group_id,
            "access": "allow"
        }
    ]
    
    for i, policy in enumerate(test_policies, 1):
        print(f"\n📝 Testing format {i}:")
        print(json.dumps(policy, indent=2))
        
        try:
            response = session.post(
                'https://mars.int.bozza.au/proxy/network/api/s/default/rest/object-policy',
                json=policy
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("✅ Success!")
                print("Found working format!")
                return
                
        except Exception as e:
            print(f"Error: {str(e)}")
            
        print("Moving to next format...")

def main():
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    test_policy()
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)