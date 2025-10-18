#!/usr/bin/env python3
"""
List all available UniFi devices
"""

import os
import json
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def list_devices():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
        'Content-Type': 'application/json'
    })

    # Get all devices
    response = session.get('https://192.168.22.194/proxy/network/api/s/default/list/user')
    if response.status_code != 200:
        print("❌ Could not get device list")
        return False
        
    devices = response.json().get('data', [])
    
    print(f"📱 Devices Found: {len(devices)}")
    print("\n📋 Device Details:")
    print("=" * 80)
    
    for device in devices:
        # Extract fields we care about
        name = device.get('name', device.get('hostname', 'Unknown'))
        mac = device.get('mac')
        ip = device.get('ip') or device.get('fixed_ip')
        network = device.get('network', 'Unknown')
        oui = device.get('oui', 'Unknown')
        device_id = device.get('_id')
        
        print(f"Name: {name}")
        print(f"MAC: {mac}")
        print(f"IP: {ip}")
        print(f"Network: {network}")
        print(f"OUI: {oui}")
        print(f"ID: {device_id}")
        print("-" * 80)

    # Get all groups
    response = session.get('https://192.168.22.194/proxy/network/api/s/default/rest/usergroup')
    if response.status_code != 200:
        print("❌ Could not get groups")
        return False
        
    groups = response.json().get('data', [])
    print("\n🎯 Groups:")
    print("=" * 80)
    
    for group in groups:
        name = group.get('name')
        group_id = group.get('_id')
        description = group.get('group_description', 'No description')
        if name.startswith('Default') or name.endswith('DELETE'):
            continue
        print(f"Name: {name}")
        print(f"ID: {group_id}")
        print(f"Description: {description}")
        print("-" * 80)
    
    return True

def main():
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    return list_devices()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)