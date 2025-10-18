#!/usr/bin/env python3
"""
Assign devices directly to client groups via client API
"""

import os
import json
import requests
import time
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class DeviceAssigner:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
            'Content-Type': 'application/json'
        })
        
        # Device to group mapping
        self.assignments = {
            'Boz-MBP-M3-Max': 'Mac',
            'truenas': 'Servers',
            'ringring': 'Servers',
            'ControlAppleTV2': 'IoT - Apple',
            'upstairs---study': 'Cameras',
            'lounge-room': 'Cameras',
            'backup': 'Cameras',
            'g5-pro': 'Cameras',
            'driveway': 'Cameras'
        }

    def get_groups(self):
        """Get existing client groups"""
        try:
            response = self.session.get('https://mars.int.bozza.au/proxy/network/api/s/default/rest/usergroup')
            if response.status_code == 200:
                groups = {}
                for group in response.json().get('data', []):
                    groups[group.get('name')] = group.get('_id')
                return groups
        except Exception as e:
            print(f"Error getting groups: {str(e)}")
        return {}

    def get_clients(self):
        """Get all clients from controller"""
        try:
            response = self.session.get('https://mars.int.bozza.au/proxy/network/api/s/default/stat/sta')
            if response.status_code == 200:
                return response.json().get('data', [])
        except Exception as e:
            print(f"Error getting clients: {str(e)}")
        return []

    def assign_device(self, client, group_id):
        """Assign a device to a group using multiple API methods"""
        mac = client.get('mac')
        user_id = client.get('_id')
        hostname = client.get('hostname', client.get('name', 'Unknown'))
        
        # Try different API approaches
        methods = [
            # Method 1: Update client directly
            {
                'method': 'PUT',
                'endpoint': f'rest/user/{user_id}',
                'payload': {'usergroup_id': group_id}
            },
            # Method 2: Use stamgr command
            {
                'method': 'POST',
                'endpoint': 'cmd/stamgr',
                'payload': {
                    'cmd': 'update-sta',
                    'mac': mac,
                    'usergroup_id': group_id
                }
            },
            # Method 3: Alternative user update
            {
                'method': 'PUT',
                'endpoint': f'rest/user/{mac}',
                'payload': {'group': group_id}
            },
            # Method 4: Direct client update
            {
                'method': 'PUT',
                'endpoint': f'stat/sta/{mac}',
                'payload': {'usergroup_id': group_id}
            },
            # Method 5: Alternative group assignment
            {
                'method': 'POST',
                'endpoint': 'upd/user',
                'payload': {
                    'mac': mac,
                    'usergroup_id': group_id
                }
            }
        ]
        
        for method in methods:
            try:
                url = f'https://mars.int.bozza.au/proxy/network/api/s/default/{method["endpoint"]}'
                
                if method['method'] == 'PUT':
                    response = self.session.put(url, json=method['payload'])
                else:
                    response = self.session.post(url, json=method['payload'])
                
                if response.status_code == 200:
                    return True, f"Success using {method['endpoint']}"
                
            except Exception as e:
                continue
        
        return False, "All methods failed"

    def assign_all_devices(self, dry_run=False):
        """Assign all devices to their groups"""
        print("🎯 Assigning Devices to Groups")
        print("=" * 50)
        
        if dry_run:
            print("🔍 DRY RUN MODE - No actual changes will be made")
            print()
        
        # Get groups and their IDs
        groups = self.get_groups()
        if not groups:
            print("❌ No groups found!")
            return False
            
        print("📋 Found groups:")
        for name, group_id in groups.items():
            print(f"   • {name} ({group_id})")
        
        # Get all clients
        clients = self.get_clients()
        if not clients:
            print("❌ No clients found!")
            return False
        
        # Process assignments
        success_count = 0
        for client in clients:
            hostname = client.get('hostname', client.get('name', 'Unknown'))
            mac = client.get('mac')
            current_ip = client.get('ip', 'No IP')
            
            # Skip if no assignment needed
            if hostname not in self.assignments:
                continue
            
            target_group = self.assignments[hostname]
            group_id = groups.get(target_group)
            
            if not group_id:
                print(f"❌ Group not found: {target_group}")
                continue
            
            print(f"\n📱 Processing: {hostname}")
            print(f"   MAC: {mac}")
            print(f"   IP: {current_ip}")
            print(f"   Target Group: {target_group}")
            
            if dry_run:
                print(f"   ℹ️ Would assign to group {target_group}")
                success_count += 1
                continue
            
            # Attempt assignment
            success, message = self.assign_device(client, group_id)
            
            if success:
                print(f"   ✅ {message}")
                success_count += 1
                
                # Small delay between assignments
                time.sleep(2)
            else:
                print(f"   ❌ Failed: {message}")
        
        print(f"\n📊 Assignment Results:")
        print(f"   ✅ Successfully assigned: {success_count}/{len(self.assignments)} devices")
        
        if not dry_run and success_count > 0:
            print(f"\n⏳ Waiting for changes to propagate...")
            time.sleep(10)
            
            print(f"\n🔄 Verifying assignments...")
            self.verify_assignments()
        
        return success_count > 0

    def verify_assignments(self):
        """Verify device group assignments"""
        clients = self.get_clients()
        groups = self.get_groups()
        
        # Create reverse lookup for group IDs to names
        group_id_to_name = {id: name for name, id in groups.items()}
        
        print("\n📋 Current Device Assignments:")
        for client in clients:
            hostname = client.get('hostname', client.get('name', 'Unknown'))
            if hostname in self.assignments:
                expected_group = self.assignments[hostname]
                current_group_id = client.get('usergroup_id', '')
                current_group = group_id_to_name.get(current_group_id, 'None')
                
                if current_group == expected_group:
                    print(f"   ✅ {hostname:<20} → {current_group}")
                else:
                    print(f"   ❌ {hostname:<20} → Expected: {expected_group}, Got: {current_group}")

def main():
    """Main function"""
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    assigner = DeviceAssigner()
    
    # Check for dry run mode
    import sys
    dry_run = '--dry-run' in sys.argv or '--test' in sys.argv
    
    return assigner.assign_all_devices(dry_run=dry_run)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)