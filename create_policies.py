#!/usr/bin/env python3
"""
Create UniFi Object Policies for each group
"""

import os
import json
import time
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Each policy has a name, content rules, route and QoS settings
POLICY_DEFAULTS = {
    'enabled': True,
    'app_enabled': True,
    'app_action': 'ALLOW',
    'app_schedule': 'ALWAYS',
    'app_type': 'ALL',
    'app_rules': [
        {
            'type': 'ANY',
        }
    ],
    'route_type': 'ALL',
    'route_interface': 'Telstra 1000/400 FTTP v1',
    'route_killSwitch': True,
    'traffic_enabled': True,
    'traffic_type': 'ALL',
    'traffic_mode': 'LIMIT',
    'traffic_schedule': 'ALWAYS',
}

# Policy configurations
POLICY_CONFIGS = {
    'Servers': {
        # Full access
        'enabled': True,
        'app_enabled': True,
        'app_action': 'ALLOW',
        'app_schedule': 'ALWAYS',
        'app_type': 'ALL',
        'app_rules': [
            {'type': 'ANY'}
        ],
        'traffic_enabled': True,
        'traffic_type': 'ALL',
        'traffic_mode': 'LIMIT',
        'traffic_schedule': 'ALWAYS',
        'traffic_up': 100,
        'traffic_down': 200,
        'route_type': 'ALL',
        'route_interface': 'Telstra 1000/400 FTTP v1',
        'route_killSwitch': True,
    },
    'Mac': {
        # Full access
        'enabled': True,
        'app_enabled': True,
        'app_action': 'ALLOW',
        'app_schedule': 'ALWAYS',
        'app_type': 'ALL',
        'app_rules': [
            {'type': 'ANY'}
        ],
        'traffic_enabled': True,
        'traffic_type': 'ALL',
        'traffic_mode': 'LIMIT',
        'traffic_schedule': 'ALWAYS',
        'traffic_up': 50,
        'traffic_down': 100,
        'route_type': 'ALL',
        'route_interface': 'Telstra 1000/400 FTTP v1',
        'route_killSwitch': True,
    },
    'Cameras': {
        # Limited to DNS, NTP, and UniFi
        'enabled': True,
        'app_enabled': True,
        'app_action': 'ALLOW',
        'app_schedule': 'ALWAYS',
        'app_type': 'EXACT',
        'app_rules': [
            {'name': 'NTP', 'type': 'EXACT'},
            {'name': 'DNS', 'type': 'EXACT'},
            {'name': 'ui.com', 'type': 'DOMAIN'},
            {'name': 'UniFi', 'type': 'GROUP'}
        ],
        'traffic_enabled': True,
        'traffic_type': 'ALL',
        'traffic_mode': 'LIMIT',
        'traffic_schedule': 'ALWAYS',
        'traffic_up': 10,
        'traffic_down': 10,
        'route_type': 'ALL',
        'route_interface': 'Telstra 1000/400 FTTP v1',
        'route_killSwitch': False,
    },
    'IoT - Apple': {
        # Limited to Apple services
        'enabled': True,
        'app_enabled': True,
        'app_action': 'ALLOW',
        'app_schedule': 'ALWAYS',
        'app_type': 'EXACT',
        'app_rules': [
            {'name': 'Apple', 'type': 'GROUP'},
            {'name': 'AirPlay', 'type': 'EXACT'},
            {'name': 'HomeKit', 'type': 'EXACT'},
            {'name': 'apple.com', 'type': 'DOMAIN'},
            {'name': 'icloud.com', 'type': 'DOMAIN'}
        ],
        'traffic_enabled': True,
        'traffic_type': 'ALL',
        'traffic_mode': 'LIMIT',
        'traffic_schedule': 'ALWAYS',
        'traffic_up': 25,
        'traffic_down': 25,
        'route_type': 'ALL',
        'route_interface': 'Telstra 1000/400 FTTP v1',
        'route_killSwitch': False,
    }
}

def create_policies():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
        'Content-Type': 'application/json'
    })
    
    # Get all groups
    response = session.get('https://192.168.22.194/proxy/network/api/s/default/rest/usergroup')
    if response.status_code != 200:
        print("❌ Could not get groups")
        return False
        
    groups = response.json().get('data', [])
    print(f"🎯 Groups Found: {len(groups)}")
    
    # Filter groups to only the ones we want to use
    active_groups = {}
    for group in groups:
        name = group.get('name')
        group_id = group.get('_id')
        
        if name in POLICY_CONFIGS and not name.endswith('_DELETE'):
            active_groups[name] = group_id
            
    print("\n📋 Active Groups:")
    for name, group_id in active_groups.items():
        print(f"   • {name}: {group_id}")
        
    # First get existing policies
    print("\n🔍 Checking for existing policies...")
    response = session.get('https://192.168.22.194/proxy/network/api/s/default/rest/object-policy')
    if response.status_code != 200:
        print("❌ Could not get policies")
        print(f"Response: {response.text[:200]}")
    else:
        policies = response.json().get('data', [])
        print(f"Found {len(policies)} existing policies")
        
        # Delete any existing policies for our groups
        if policies:
            print("\n🗑️ Cleaning up existing policies...")
            for policy in policies:
                policy_id = policy.get('_id')
                policy_name = policy.get('name')
                
                try:
                    # Delete the policy
                    response = session.delete(
                        f'https://192.168.22.194/proxy/network/api/s/default/rest/object-policy/{policy_id}'
                    )
                    if response.status_code == 200:
                        print(f"   ✅ Deleted: {policy_name}")
                    else:
                        print(f"   ❌ Failed to delete: {policy_name}")
                        print(f"   Response: {response.text[:200]}")
                except Exception as e:
                    print(f"   ❌ Error deleting: {policy_name} ({str(e)})")
                    
            # Wait a moment for changes to propagate
            print("\n⏳ Waiting for changes to propagate...")
            time.sleep(5)
    
    # Create new policies
    print("\n🏗️  Creating policies...")
    for group_name, group_id in active_groups.items():
        config = POLICY_CONFIGS.get(group_name)
        if not config:
            print(f"   ❓ No config for {group_name}")
            continue
            
        try:
            basic_payload = {
                'name': group_name,
                'groupId': group_id,
                'description': f'Managed policy for {group_name} group',
                'enabled': True,
                'settings': {
                    'secure': {
                        'enabled': True,
                        'action': config.get('app_action', 'ALLOW')
                    },
                    'route': {
                        'enabled': True,
                        'interface': 'Telstra 1000/400 FTTP v1',
                        'killSwitch': config.get('route_killSwitch', True)
                    },
                    'qos': {
                        'enabled': True,
                        'mode': 'LIMIT',
                        'download': config.get('traffic_down', 200),
                        'upload': config.get('traffic_up', 100)
                    }
                }
            }
            
            print(f"\n📤 Policy payload for {group_name}:")
            print(json.dumps(basic_payload, indent=2))
            
            response = session.post(
                'https://192.168.22.194/proxy/network/api/s/default/rest/object-policy',
                json=basic_payload
            )
            
            if response.status_code == 200:
                policy_id = response.json().get('data', [{}])[0].get('_id')
                print(f"   ✅ Created: {group_name} ({policy_id})")
            else:
                print(f"   ❌ Failed to create: {group_name}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error creating: {group_name} ({str(e)})")
            
    return True

def main():
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    return create_policies()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)