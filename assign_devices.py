#!/usr/bin/env python3
"""
Assign devices to the correct groups
"""

import os
import json
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Map device patterns to groups
DEVICE_PATTERNS = {
    'Servers': [
        # Named devices
        'truenas',
        'ringring',
    ],
    'Mac': [
        # Workstations
        'Boz-MBP-M3-Max',
        'Boz-Mac-M3',
        'BOZ - Macbook Pro M3 Max',
        'BOZ - Mac Studio M3 Ultra',
        'BOZ - MacBook Pro M3',
    ],
    'Cameras': [
        # UniFi cameras
        'upstairs---study',
        'lounge-room',
        'backup',
        'g5-pro',
        'driveway',
    ],
    'IoT - Apple': [
        # Apple TVs
        'BOZ - Apple TV Love Dungeon',
        'BOZ - Apple TV Lounge Room',
        'BOZ - Apple TV Control Room',
        'BOZ - Control Room Apple TV',
        'BOZ - Apple TV 4K via ETH',
        # HomeKit devices
        'ControlAppleTV2',
        'ControlRoom496',
        'Lounge-Room-432',
    ]
}

def assign_devices():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
        'Content-Type': 'application/json'
    })

    # First get device list
    response = session.get('https://192.168.22.194/proxy/network/api/s/default/list/user')
    if response.status_code != 200:
        print("❌ Could not get device list")
        return False
        
    devices = response.json().get('data', [])
    print(f"📱 Devices Found: {len(devices)}")
    
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
        
        if name in DEVICE_PATTERNS and not name.endswith('_DELETE'):
            active_groups[name] = group_id
            
    print("\n📋 Active Groups:")
    for name, group_id in active_groups.items():
        print(f"   • {name}: {group_id}")
    
    # Map devices to groups
    device_assignments = {}
    unassigned_devices = []
    for device in devices:
        device_name = device.get('name', device.get('hostname', '')).lower()
        device_id = device.get('_id')
        
        # Skip if no name or id
        if not device_name or not device_id:
            continue
        
        assigned = False
        for group_name, patterns in DEVICE_PATTERNS.items():
            if group_name not in active_groups:
                continue
                
            for pattern in patterns:
                if pattern.lower() in device_name:
                    group_id = active_groups[group_name]
                    if group_id not in device_assignments:
                        device_assignments[group_id] = []
                    device_assignments[group_id].append({
                        'id': device_id,
                        'name': device_name
                    })
                    assigned = True
                    break
                    
            if assigned:
                break
                
        if not assigned:
            unassigned_devices.append({
                'id': device_id,
                'name': device_name
            })
    
    # Show assignments
    print("\n📝 Device Assignments:")
    for group_name, group_id in active_groups.items():
        assigned = device_assignments.get(group_id, [])
        print(f"\n{group_name} ({group_id}): {len(assigned)} devices")
        for device in assigned:
            print(f"   • {device['name']} ({device['id']})")
    
    print("\n❓ Unassigned: {len(unassigned_devices)} devices")
    print("\nℹ️  These are usually guest devices, phones, tablets, etc.")
    
    # Update groups with device assignments
    print("\n🔄 Updating groups...")
    for group_name, group_id in active_groups.items():
        assigned = device_assignments.get(group_id, [])
        if not assigned:
            print(f"   • {group_name}: No devices to assign")
            continue
            
        try:
            device_ids = [d['id'] for d in assigned]
            device_names = [d['name'] for d in assigned]
            
            payload = {
                '_id': group_id,
                'name': group_name,
                'group_type': 'user-group',
                'group_description': f'Managed by assign_devices.py',
                'deviceIds': device_ids
            }
            
            response = session.put(
                f'https://192.168.22.194/proxy/network/api/s/default/rest/usergroup/{group_id}',
                json=payload
            )
            if response.status_code == 200:
                print(f"   ✅ {group_name}: {len(device_ids)} devices")
            else:
                print(f"   ❌ {group_name}: Failed to update ({response.status_code})")
                print(f"      Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ {group_name}: Error updating ({str(e)})")
    
    return True

def main():
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    return assign_devices()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)