#!/usr/bin/env python3
"""
Populate Device Groups Script
Actually assigns devices to the proper groups in UniFi interface
"""

import os
import json
import requests
import time
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class DeviceGroupPopulator:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
            'Content-Type': 'application/json'
        })
        
        # Device group assignments based on your interface
        self.device_group_assignments = {
            'Boz-MBP-M3-Max': 'Mac',
            'truenas': 'Servers', 
            'ControlAppleTV2': 'IoT - Apple',
            'ringring': 'Servers',  # Fing Network Agent -> Servers
            'upstairs---study': 'Cameras',  # UniFi cameras
            'lounge-room': 'Cameras',
            'backup': 'Cameras', 
            'g5-pro': 'Cameras',
            'driveway': 'Cameras'
        }
        
        # Network assignments (for VLAN placement)
        self.network_assignments = {
            'Boz-MBP-M3-Max': 'User_Devices',
            'truenas': 'Corporate_Servers',
            'ControlAppleTV2': 'Apple_IoT', 
            'ringring': 'Corporate_Servers',
            'upstairs---study': 'MGMT_Infrastructure',
            'lounge-room': 'MGMT_Infrastructure',
            'backup': 'MGMT_Infrastructure',
            'g5-pro': 'MGMT_Infrastructure', 
            'driveway': 'MGMT_Infrastructure'
        }

    def get_clients(self):
        """Get all clients from controller"""
        try:
            response = self.session.get('https://mars.int.bozza.au/proxy/network/api/s/default/stat/sta')
            if response.status_code == 200:
                return response.json().get('data', [])
        except Exception as e:
            print(f"Error getting clients: {str(e)}")
        return []

    def get_networks(self):
        """Get all networks and create ID mapping"""
        try:
            response = self.session.get('https://mars.int.bozza.au/proxy/network/api/s/default/rest/networkconf')
            if response.status_code == 200:
                networks = {}
                for net in response.json().get('data', []):
                    networks[net.get('name')] = net.get('_id')
                return networks
        except Exception as e:
            print(f"Error getting networks: {str(e)}")
        return {}

    def get_user_groups(self):
        """Get existing user groups"""
        try:
            response = self.session.get('https://mars.int.bozza.au/proxy/network/api/s/default/rest/usergroup')
            if response.status_code == 200:
                groups = {}
                for group in response.json().get('data', []):
                    groups[group.get('name')] = group.get('_id')
                return groups
        except Exception as e:
            print(f"Error getting user groups: {str(e)}")
        return {}

    def create_missing_groups(self):
        """Create any missing device groups"""
        print("🔍 Checking for missing device groups...")
        
        existing_groups = self.get_user_groups()
        required_groups = set(self.device_group_assignments.values())
        
        missing_groups = required_groups - set(existing_groups.keys())
        
        if not missing_groups:
            print("   ✅ All required groups exist")
            return True
            
        print(f"   📝 Creating {len(missing_groups)} missing groups...")
        
        for group_name in missing_groups:
            try:
                payload = {
                    "name": group_name,
                    "qos_rate_max_down": -1,
                    "qos_rate_max_up": -1
                }
                
                response = self.session.post(
                    'https://mars.int.bozza.au/proxy/network/api/s/default/rest/usergroup',
                    json=payload,
                    timeout=15
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Created group: {group_name}")
                else:
                    print(f"   ❌ Failed to create {group_name}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error creating {group_name}: {str(e)}")
        
        return True

    def assign_device_to_group(self, user_id, group_id, device_name, group_name):
        """Assign device to a user group"""
        try:
            # Update user with group assignment
            payload = {
                "usergroup_id": group_id
            }
            
            response = self.session.put(
                f'https://mars.int.bozza.au/proxy/network/api/s/default/rest/user/{user_id}',
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, f"Assigned to {group_name}"
            else:
                return False, f"API returned {response.status_code}: {response.text[:100]}"
                
        except Exception as e:
            return False, f"Exception: {str(e)}"

    def assign_device_to_network(self, user_id, network_id, device_name, network_name):
        """Assign device to a network (VLAN)"""
        try:
            payload = {
                "network": network_id
            }
            
            response = self.session.put(
                f'https://mars.int.bozza.au/proxy/network/api/s/default/rest/user/{user_id}',
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, f"Moved to {network_name}"
            else:
                return False, f"Network assignment failed: {response.status_code}"
                
        except Exception as e:
            return False, f"Network exception: {str(e)}"

    def populate_groups_and_networks(self, dry_run=False):
        """Populate device groups and assign networks"""
        print("🎯 Device Group & Network Assignment")
        print("=" * 50)
        
        if dry_run:
            print("🔍 DRY RUN MODE - No actual changes will be made")
            print()
        
        # Get current state
        clients = self.get_clients()
        networks = self.get_networks()
        user_groups = self.get_user_groups()
        
        if not dry_run:
            self.create_missing_groups()
            user_groups = self.get_user_groups()  # Refresh after creation
        
        print("\n📊 Available Networks:")
        for name, net_id in networks.items():
            if name in self.network_assignments.values():
                print(f"   📍 {name}")
        
        print("\n📊 Available Groups:")
        for name, group_id in user_groups.items():
            if name in self.device_group_assignments.values():
                print(f"   👥 {name}")
        
        print(f"\n📱 Device Assignments:")
        
        # Find devices to assign
        assignments_to_make = []
        for client in clients:
            hostname = client.get('hostname', client.get('name', 'Unknown'))
            user_id = client.get('user_id')
            current_network = client.get('network')
            current_group = client.get('usergroup_id', '')
            current_ip = client.get('ip', 'Unknown')
            
            if hostname in self.device_group_assignments:
                target_group_name = self.device_group_assignments[hostname]
                target_network_name = self.network_assignments[hostname]
                
                target_group_id = user_groups.get(target_group_name)
                target_network_id = networks.get(target_network_name)
                
                # Check what needs to be done
                group_needed = current_group != target_group_id
                network_needed = current_network != target_network_name
                
                if group_needed or network_needed:
                    assignments_to_make.append({
                        'hostname': hostname,
                        'user_id': user_id,
                        'current_ip': current_ip,
                        'target_group_name': target_group_name,
                        'target_group_id': target_group_id,
                        'target_network_name': target_network_name,
                        'target_network_id': target_network_id,
                        'group_needed': group_needed,
                        'network_needed': network_needed
                    })
        
        # Show assignment plan
        for assignment in assignments_to_make:
            hostname = assignment['hostname']
            group_name = assignment['target_group_name']
            network_name = assignment['target_network_name']
            current_ip = assignment['current_ip']
            
            actions = []
            if assignment['group_needed']:
                actions.append(f"Group: {group_name}")
            if assignment['network_needed']:
                actions.append(f"Network: {network_name}")
            
            actions_str = " + ".join(actions)
            print(f"   📍 {hostname:<20} → {actions_str} [{current_ip}]")
        
        if not assignments_to_make:
            print("   ✅ All devices already correctly assigned!")
            return True
            
        if dry_run:
            print(f"\n🔍 Dry run complete - would make {len(assignments_to_make)} assignments")
            return True
        
        # Confirm before proceeding  
        print(f"\n⚠️ This will assign {len(assignments_to_make)} devices to groups and networks")
        confirm = input(f"\n🔴 Proceed? (y/N): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("❌ Operation cancelled")
            return False
        
        # Make assignments
        success_count = 0
        
        for i, assignment in enumerate(assignments_to_make, 1):
            hostname = assignment['hostname']
            user_id = assignment['user_id']
            
            print(f"\n📱 [{i}/{len(assignments_to_make)}] Configuring {hostname}...")
            
            device_success = True
            
            # Assign to group first
            if assignment['group_needed']:
                group_name = assignment['target_group_name']
                group_id = assignment['target_group_id']
                
                if group_id:
                    print(f"   👥 Assigning to group: {group_name}")
                    success, message = self.assign_device_to_group(user_id, group_id, hostname, group_name)
                    if success:
                        print(f"   ✅ {message}")
                    else:
                        print(f"   ❌ Group assignment failed: {message}")
                        device_success = False
                else:
                    print(f"   ❌ Group '{group_name}' not found")
                    device_success = False
            
            # Then assign to network
            if assignment['network_needed'] and device_success:
                network_name = assignment['target_network_name'] 
                network_id = assignment['target_network_id']
                
                if network_id:
                    print(f"   🌐 Moving to network: {network_name}")
                    success, message = self.assign_device_to_network(user_id, network_id, hostname, network_name)
                    if success:
                        print(f"   ✅ {message}")
                        print(f"   ⏳ Waiting for reconnection...")
                        time.sleep(30)
                    else:
                        print(f"   ❌ Network assignment failed: {message}")
                        device_success = False
                else:
                    print(f"   ❌ Network '{network_name}' not found")
                    device_success = False
            
            if device_success:
                success_count += 1
                print(f"   🎉 {hostname} successfully configured")
            else:
                print(f"   💥 {hostname} configuration failed")
        
        print(f"\n📊 Assignment Results:")
        print(f"   ✅ Successfully configured: {success_count}/{len(assignments_to_make)} devices")
        print(f"   📈 Success rate: {(success_count/len(assignments_to_make))*100:.1f}%")
        
        if success_count > 0:
            print(f"\n🔍 Checking final status in 15 seconds...")
            time.sleep(15)
            os.system("python3 monitor_assignment_progress.py")
        
        return success_count > 0

def main():
    """Main function"""
    import sys
    
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    populator = DeviceGroupPopulator()
    
    # Check for dry run mode
    dry_run = '--dry-run' in sys.argv or '--test' in sys.argv
    
    return populator.populate_groups_and_networks(dry_run=dry_run)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)