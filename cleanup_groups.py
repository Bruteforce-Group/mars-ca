#!/usr/bin/env python3
"""
Clean up duplicate groups and recreate them cleanly
"""

import os
import json
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def cleanup_groups():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
        'Content-Type': 'application/json'
    })

    print("🧹 Cleaning up groups...")

    # First list all groups
    response = session.get('https://192.168.22.194/proxy/network/api/s/default/rest/usergroup')
    if response.status_code != 200:
        print("❌ Could not get groups")
        return False
        
    groups = response.json().get('data', [])
    print("\n📋 Current Groups:")
    for group in groups:
        name = group.get('name')
        group_id = group.get('_id')
        print(f"   • {name}: {group_id}")

    # Find all non-default groups by name
    groups_by_name = {}
    for group in groups:
        name = group.get('name')
        group_id = group.get('_id')
        
        if name == 'Default':
            continue
            
        if name not in groups_by_name:
            groups_by_name[name] = []
        groups_by_name[name].append(group_id)
    
    # Delete all non-default groups
    print("\n🗑️ Deleting groups...")
    for name, group_ids in groups_by_name.items():
        print(f"   🎯 {name}: {len(group_ids)} instances")
        for group_id in group_ids:
            try:
                # First try a direct delete
                response = session.delete(
                    f'https://192.168.22.194/proxy/network/api/s/default/rest/usergroup/{group_id}'
                )
                if response.status_code == 200:
                    print(f"      ✅ Deleted {group_id} directly")
                    continue
                    
                # If that fails, try to remove through put
                print(f"      ⚠️ Direct delete failed for {group_id}, trying PUT")
                response = session.put(
                    f'https://192.168.22.194/proxy/network/api/s/default/rest/usergroup/{group_id}',
                    json={
                        '_id': group_id,
                        'name': f"{name}_DELETE_{group_id}",
                        'group_type': 'user-group',
                        'group_description': 'Marked for deletion'
                    }
                )
                if response.status_code == 200:
                    print(f"      ✅ Marked {group_id} for deletion")
                    
                    # Try delete again
                    response = session.delete(
                        f'https://192.168.22.194/proxy/network/api/s/default/rest/usergroup/{group_id}'
                    )
                    if response.status_code == 200:
                        print(f"      ✅ Deleted {group_id} after marking")
                    else:
                        print(f"      ❌ Failed final delete for {group_id}: {response.status_code}")
                else:
                    print(f"      ❌ Failed to mark {group_id}: {response.status_code}")
            except Exception as e:
                print(f"      ❌ Error processing {group_id}: {str(e)}")
    
    # Wait a moment
    print("\n⏳ Waiting for changes to propagate...")
    time.sleep(5)
    
    # Create clean groups
    print("\n🏗️ Creating clean groups...")
    groups_to_create = [
        {
            'name': 'Servers',
            'description': 'Corporate servers and network services',
            'members': ['truenas', 'ringring']
        },
        {
            'name': 'Mac',
            'description': 'Mac workstations',
            'members': ['Boz-MBP-M3-Max']
        },
        {
            'name': 'Cameras',
            'description': 'UniFi cameras and network infrastructure',
            'members': ['upstairs---study', 'lounge-room', 'backup', 'g5-pro', 'driveway']
        },
        {
            'name': 'IoT - Apple',
            'description': 'Apple IoT devices',
            'members': ['ControlAppleTV2']
        }
    ]
    
    for group in groups_to_create:
        try:
            payload = {
                'name': group['name'],
                'group_type': 'user-group',
                'group_description': group['description']
            }
            
            # List groups first to check for existing
            response = session.get('https://192.168.22.194/proxy/network/api/s/default/rest/usergroup')
            if response.status_code != 200:
                print(f"   ❌ Could not check for existing {group['name']}")
                continue
                
            existing_groups = response.json().get('data', [])
            matching_groups = [g for g in existing_groups if g.get('name') == group['name']]
            
            if matching_groups:
                print(f"   ⚠️ Group {group['name']} already exists: {[g.get('_id') for g in matching_groups]}")
                continue
            
            # Create the new group
            response = session.post(
                'https://192.168.22.194/proxy/network/api/s/default/rest/usergroup',
                json=payload
            )
            
            if response.status_code == 200:
                new_group_id = response.json().get('data', [{}])[0].get('_id')
                print(f"   ✅ Created group: {group['name']} ({new_group_id})")
            else:
                print(f"   ❌ Failed to create {group['name']}: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error creating {group['name']}: {str(e)}")
    
    # Verify final state
    print("\n🔍 Verifying final state...")
    response = session.get('https://192.168.22.194/proxy/network/api/s/default/rest/usergroup')
    if response.status_code == 200:
        groups = response.json().get('data', [])
        print("\n📋 Final Groups:")
        for group in groups:
            name = group.get('name')
            group_id = group.get('_id')
            print(f"   • {name}: {group_id}")
    
    return True

def main():
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    return cleanup_groups()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)