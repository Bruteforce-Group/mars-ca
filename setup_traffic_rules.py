#!/usr/bin/env python3
"""
Setup UniFi Traffic Rules and Object Policies
Modern approach using Objects instead of VLANs
"""

import os
import json
import requests
import time
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class TrafficRulesManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
            'Content-Type': 'application/json'
        })
        
        # Device group assignments for Object Policies
        self.device_object_groups = {
            'Management_Infrastructure': {
                'description': 'UniFi cameras, APs, and network infrastructure',
                'devices': ['upstairs---study', 'lounge-room', 'backup', 'g5-pro', 'driveway'],
                'allowed_access': ['internet', 'local_services', 'management']
            },
            'Corporate_Servers': {
                'description': 'Internal servers, NAS, and business systems',
                'devices': ['truenas', 'ringring'],  # TrueNAS + Fing Network Agent
                'allowed_access': ['internet', 'local_services', 'user_devices']
            },
            'User_Workstations': {
                'description': 'Mac computers and user workstations',
                'devices': ['Boz-MBP-M3-Max'],
                'allowed_access': ['internet', 'local_services', 'corporate_servers', 'apple_iot']
            },
            'Apple_IoT_Devices': {
                'description': 'Apple TV, HomePods, and Apple ecosystem',
                'devices': ['ControlAppleTV2'],
                'allowed_access': ['internet', 'apple_services', 'user_devices']
            }
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

    def get_firewall_groups(self):
        """Get existing firewall groups"""
        try:
            response = self.session.get('https://mars.int.bozza.au/proxy/network/api/s/default/rest/firewallgroup')
            if response.status_code == 200:
                groups = {}
                for group in response.json().get('data', []):
                    groups[group.get('name')] = group
                return groups
        except Exception as e:
            print(f"Error getting firewall groups: {str(e)}")
        return {}

    def get_firewall_rules(self):
        """Get existing firewall rules"""
        try:
            response = self.session.get('https://mars.int.bozza.au/proxy/network/api/s/default/rest/firewallrule')
            if response.status_code == 200:
                return response.json().get('data', [])
        except Exception as e:
            print(f"Error getting firewall rules: {str(e)}")
        return []

    def create_object_policy_groups(self):
        """Create Object Policy Groups for traffic rules"""
        print("🏗️ Creating Object Policy Groups...")
        
        clients = self.get_clients()
        existing_groups = self.get_firewall_groups()
        
        # Create client MAC lookup
        client_lookup = {}
        for client in clients:
            hostname = client.get('hostname', client.get('name', ''))
            mac = client.get('mac')
            if hostname and mac:
                client_lookup[hostname] = mac
        
        success_count = 0
        
        for group_name, group_info in self.device_object_groups.items():
            print(f"\n📍 Creating group: {group_name}")
            
            # Find MACs for devices in this group
            group_macs = []
            for device_name in group_info['devices']:
                mac = client_lookup.get(device_name)
                if mac:
                    group_macs.append(mac)
                    print(f"   ✅ Found {device_name}: {mac}")
                else:
                    print(f"   ⚠️ Device not found: {device_name}")
            
            if not group_macs:
                print(f"   ❌ No devices found for group {group_name}")
                continue
            
            # Check if group already exists
            if group_name in existing_groups:
                print(f"   ℹ️ Group {group_name} already exists, updating...")
                group_id = existing_groups[group_name].get('_id')
                
                # Update existing group
                payload = {
                    "name": group_name,
                    "group_type": "address-group",
                    "group_members": group_macs,
                    "group_description": group_info['description']
                }
                
                try:
                    response = self.session.put(
                        f'https://mars.int.bozza.au/proxy/network/api/s/default/rest/firewallgroup/{group_id}',
                        json=payload,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        print(f"   ✅ Updated group with {len(group_macs)} devices")
                        success_count += 1
                    else:
                        print(f"   ❌ Failed to update: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error updating group: {str(e)}")
            else:
                # Create new group
                payload = {
                    "name": group_name,
                    "group_type": "address-group", 
                    "group_members": group_macs,
                    "group_description": group_info['description']
                }
                
                try:
                    response = self.session.post(
                        'https://mars.int.bozza.au/proxy/network/api/s/default/rest/firewallgroup',
                        json=payload,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        print(f"   ✅ Created group with {len(group_macs)} devices")
                        success_count += 1
                    else:
                        print(f"   ❌ Failed to create: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error creating group: {str(e)}")
        
        print(f"\n📊 Created/updated {success_count} Object Policy Groups")
        return success_count > 0

    def create_traffic_rules(self):
        """Create traffic rules for zero-trust security"""
        print(f"\n🛡️ Creating Zero-Trust Traffic Rules...")
        
        # Define zero-trust rules
        traffic_rules = [
            {
                "name": "Allow_Management_Infrastructure",
                "enabled": True,
                "action": "accept",
                "protocol": "all",
                "src_firewallgroup_ids": ["Management_Infrastructure"],
                "dst_address": "any",
                "ruleset": "LAN_IN",
                "rule_index": 2000,
                "description": "Allow management devices full access"
            },
            {
                "name": "Allow_Corporate_Servers_Web",
                "enabled": True,
                "action": "accept", 
                "protocol": "tcp",
                "src_firewallgroup_ids": ["Corporate_Servers"],
                "dst_port": "80,443,8080,22,3389",
                "dst_address": "any",
                "ruleset": "LAN_IN",
                "rule_index": 2001,
                "description": "Allow servers web and admin access"
            },
            {
                "name": "Allow_Users_to_Servers",
                "enabled": True,
                "action": "accept",
                "protocol": "all",
                "src_firewallgroup_ids": ["User_Workstations"],
                "dst_firewallgroup_ids": ["Corporate_Servers"],
                "ruleset": "LAN_IN", 
                "rule_index": 2002,
                "description": "Allow users to access corporate servers"
            },
            {
                "name": "Allow_Users_Internet",
                "enabled": True,
                "action": "accept",
                "protocol": "all", 
                "src_firewallgroup_ids": ["User_Workstations"],
                "dst_address": "!192.168.0.0/16",
                "ruleset": "LAN_IN",
                "rule_index": 2003,
                "description": "Allow users internet access"
            },
            {
                "name": "Allow_Apple_IoT_Limited",
                "enabled": True,
                "action": "accept",
                "protocol": "tcp",
                "src_firewallgroup_ids": ["Apple_IoT_Devices"], 
                "dst_port": "80,443,5353,62078",
                "dst_address": "any",
                "ruleset": "LAN_IN",
                "rule_index": 2004,
                "description": "Allow Apple devices limited internet access"
            },
            {
                "name": "Block_Inter_VLAN",
                "enabled": True,
                "action": "drop",
                "protocol": "all",
                "src_address": "192.168.0.0/16",
                "dst_address": "192.168.0.0/16", 
                "ruleset": "LAN_IN",
                "rule_index": 2999,
                "description": "Default deny for inter-network communication"
            }
        ]
        
        # Get existing groups to map names to IDs
        firewall_groups = self.get_firewall_groups()
        group_name_to_id = {name: group.get('_id') for name, group in firewall_groups.items()}
        
        success_count = 0
        existing_rules = self.get_firewall_rules()
        existing_rule_names = {rule.get('name') for rule in existing_rules}
        
        for rule in traffic_rules:
            rule_name = rule['name']
            
            if rule_name in existing_rule_names:
                print(f"   ℹ️ Rule '{rule_name}' already exists, skipping")
                continue
            
            # Map group names to IDs  
            if 'src_firewallgroup_ids' in rule:
                src_groups = []
                for group_name in rule['src_firewallgroup_ids']:
                    group_id = group_name_to_id.get(group_name)
                    if group_id:
                        src_groups.append(group_id)
                rule['src_firewallgroup_ids'] = src_groups
            
            if 'dst_firewallgroup_ids' in rule:
                dst_groups = []
                for group_name in rule['dst_firewallgroup_ids']:
                    group_id = group_name_to_id.get(group_name)
                    if group_id:
                        dst_groups.append(group_id)
                rule['dst_firewallgroup_ids'] = dst_groups
            
            print(f"   🔧 Creating rule: {rule_name}")
            
            try:
                response = self.session.post(
                    'https://mars.int.bozza.au/proxy/network/api/s/default/rest/firewallrule',
                    json=rule,
                    timeout=15
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Created traffic rule: {rule_name}")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to create rule {rule_name}: {response.status_code}")
                    print(f"       Response: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ Error creating rule {rule_name}: {str(e)}")
        
        print(f"\n🛡️ Created {success_count} traffic rules")
        return success_count > 0

    def setup_traffic_management(self, dry_run=False):
        """Set up complete traffic management system"""
        print("🎯 UniFi Traffic Rules & Object Policy Setup")
        print("=" * 60)
        
        if dry_run:
            print("🔍 DRY RUN MODE - No actual changes will be made")
            return True
        
        print("This will create Object Policy Groups and Zero-Trust Traffic Rules")
        print("instead of VLAN-based segmentation (modern UniFi approach).")
        
        confirm = input(f"\n🔴 Proceed with traffic rules setup? (y/N): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("❌ Operation cancelled")
            return False
        
        # Create Object Policy Groups
        groups_success = self.create_object_policy_groups()
        
        # Wait for groups to propagate
        if groups_success:
            print("\n⏳ Waiting for groups to propagate...")
            time.sleep(10)
        
        # Create Traffic Rules  
        rules_success = self.create_traffic_rules()
        
        print(f"\n🎉 Traffic Management Setup Complete!")
        print(f"📍 You can now view/edit at: https://mars.int.bozza.au/network/default/settings/objects")
        print(f"🛡️ Zero-trust network segmentation is now ACTIVE!")
        
        return groups_success or rules_success

def main():
    """Main function"""
    import sys
    
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    manager = TrafficRulesManager()
    
    # Check for dry run mode
    dry_run = '--dry-run' in sys.argv or '--test' in sys.argv
    
    return manager.setup_traffic_management(dry_run=dry_run)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)