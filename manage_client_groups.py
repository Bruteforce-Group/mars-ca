#!/usr/bin/env python3
"""
Manage UniFi Client Groups and Device Assignments
"""

import os
import json
import requests
import time
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class ClientGroupManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
            'Content-Type': 'application/json'
        })
        
        # Define our desired client groups and their devices
        self.desired_groups = {
            'Servers': {
                'description': 'Corporate servers and network services',
                'devices': ['truenas', 'ringring']  # Fing agent
            },
            'Mac': {
                'description': 'Mac workstations',
                'devices': ['Boz-MBP-M3-Max']
            },
            'Cameras': {
                'description': 'UniFi cameras and network infrastructure',
                'devices': ['upstairs---study', 'lounge-room', 'backup', 'g5-pro', 'driveway']
            },
            'IoT - Apple': {
                'description': 'Apple IoT devices',
                'devices': ['ControlAppleTV2']
            }
        }

    def get_current_groups(self):
        """Get current client groups"""
        try:
            response = self.session.get('https://mars.int.bozza.au/proxy/network/api/s/default/rest/usergroup')
            if response.status_code == 200:
                return response.json().get('data', [])
        except Exception as e:
            print(f"Error getting groups: {str(e)}")
        return []

    def get_clients(self):
        """Get all clients from controller"""
        try:
            response = self.session.get('https://mars.int.bozza.au/proxy/network/api/s/default/stat/sta')
            if response.status_code == 200:
                return response.json().get('data', [])
        except Exception as e:
            print(f"Error getting clients: {str(e)}")
        return []

    def delete_group(self, group_id):
        """Delete a client group"""
        try:
            # Try alternative endpoints
            endpoints = [
                'rest/usergroup',    # Standard endpoint
                'rest/group',        # Alternative endpoint
                'set/setting/usergroup'  # Legacy endpoint
            ]
            
            for endpoint in endpoints:
                response = self.session.delete(
                    f'https://mars.int.bozza.au/proxy/network/api/s/default/{endpoint}/{group_id}'
                )
                if response.status_code == 200:
                    return True
            
            # None worked
            return False
        except Exception as e:
            print(f"Error deleting group: {str(e)}")
            return False

    def create_group(self, name, description=""):
        """Create a new client group"""
        try:
            # Try both possible payload formats
            payloads = [
                {
                    "name": name,
                    "group_type": "user-group",
                    "group_members": [],
                    "group_description": description
                },
                {
                    "name": name,
                    "type": "user-group",
                    "members": [],
                    "description": description,
                    "site_id": "default"
                }
            ]
            
            # Try different endpoints with both payload formats
            endpoints = [
                'rest/usergroup',
                'rest/group',
                'set/setting/usergroup'
            ]
            
            for endpoint in endpoints:
                for payload in payloads:
                    response = self.session.post(
                        f'https://mars.int.bozza.au/proxy/network/api/s/default/{endpoint}',
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'data' in result and result['data']:
                            return result['data'][0].get('_id')
            
            return None
        except Exception as e:
            print(f"Error creating group: {str(e)}")
        return None

    def update_group_members(self, group_id, members):
        """Update group members"""
        try:
            # Try both payload formats
            payloads = [
                {"group_members": members},
                {"members": members},
                {"usergroup_id": group_id, "members": members}
            ]
            
            # Try different endpoints
            endpoints = [
                f'rest/usergroup/{group_id}',
                f'rest/group/{group_id}',
                f'set/setting/usergroup/{group_id}',
                'cmd/sitemgr',  # Alternative command endpoint
                'cmd/stamgr'    # Station manager endpoint
            ]
            
            for endpoint in endpoints:
                for payload in payloads:
                    response = self.session.put(
                        f'https://mars.int.bozza.au/proxy/network/api/s/default/{endpoint}',
                        json=payload
                    )
                    if response.status_code == 200:
                        return True
            
            return False
        except Exception as e:
            print(f"Error updating group members: {str(e)}")
            return False

    def cleanup_old_groups(self):
        """Remove existing client groups"""
        print("🧹 Cleaning up existing client groups...")
        
        current_groups = self.get_current_groups()
        success_count = 0
        
        for group in current_groups:
            name = group.get('name', '')
            group_id = group.get('_id')
            
            # Skip special system groups
            if name.startswith('_') or name == 'Default':
                continue
                
            print(f"   Removing group: {name}")
            if self.delete_group(group_id):
                success_count += 1
                print(f"   ✅ Removed: {name}")
            else:
                print(f"   ❌ Failed to remove: {name}")
        
        print(f"🧹 Cleaned up {success_count} groups")
        return success_count > 0

    def setup_new_groups(self):
        """Create and configure new client groups"""
        print("\n🏗️ Setting up new client groups...")
        
        # Get current clients for MAC lookup
        clients = self.get_clients()
        client_lookup = {}
        for client in clients:
            hostname = client.get('hostname', client.get('name', ''))
            mac = client.get('mac')
            if hostname and mac:
                client_lookup[hostname.lower()] = {
                    'mac': mac,
                    'ip': client.get('ip', 'No IP')
                }
        
        success_count = 0
        
        for group_name, group_info in self.desired_groups.items():
            print(f"\n📍 Creating group: {group_name}")
            
            # Create the group
            group_id = self.create_group(group_name, group_info['description'])
            if not group_id:
                print(f"   ❌ Failed to create group")
                continue
            
            # Find MACs for devices in this group
            group_macs = []
            for device_name in group_info['devices']:
                device_info = client_lookup.get(device_name.lower())
                if device_info:
                    group_macs.append(device_info['mac'])
                    print(f"   ✅ Found {device_name}: {device_info['mac']} ({device_info['ip']})")
                else:
                    print(f"   ⚠️ Device not found: {device_name}")
            
            # Update group members
            if group_macs:
                if self.update_group_members(group_id, group_macs):
                    print(f"   ✅ Added {len(group_macs)} devices to group")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to add devices to group")
            
        print(f"\n📊 Successfully configured {success_count}/{len(self.desired_groups)} groups")
        return success_count > 0

    def verify_setup(self):
        """Verify the groups and assignments"""
        print("\n🔍 Verifying setup...")
        
        current_groups = self.get_current_groups()
        clients = self.get_clients()
        
        # Build lookup of MAC to client info
        mac_to_client = {}
        for client in clients:
            mac = client.get('mac')
            if mac:
                mac_to_client[mac] = {
                    'hostname': client.get('hostname', client.get('name', 'Unknown')),
                    'ip': client.get('ip', 'No IP')
                }
        
        # Check each group
        for group in current_groups:
            name = group.get('name')
            if name in self.desired_groups:
                print(f"\n📋 Group: {name}")
                members = group.get('group_members', [])
                print(f"   Members ({len(members)}):")
                for mac in members:
                    client = mac_to_client.get(mac, {})
                    print(f"   • {client.get('hostname', 'Unknown')} ({client.get('ip', 'No IP')})")

def main():
    """Main function"""
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    manager = ClientGroupManager()
    
    print("🎯 UniFi Client Group Setup")
    print("=" * 50)
    
    # Show what we're going to do
    print("This will:")
    print("1. Remove existing client groups")
    print("2. Create new groups with proper device assignments")
    print("3. Verify the setup")
    print("\nNew groups to create:")
    for name, info in manager.desired_groups.items():
        print(f"• {name} ({len(info['devices'])} devices)")
    
    confirm = input("\n🔴 Proceed with client group setup? (y/N): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("❌ Operation cancelled")
        return False
    
    # Do the work
    manager.cleanup_old_groups()
    manager.setup_new_groups()
    manager.verify_setup()
    
    print("\n🎉 Client Group Setup Complete!")
    print("Now you can use these groups in Object Policies")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)