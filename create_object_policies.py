#!/usr/bin/env python3
"""
Create Object-Oriented Network Policies in UniFi OS
"""

import os
import json
import requests
import time
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class ObjectPolicyManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
            'Content-Type': 'application/json'
        })
        
        # Define our policies
        self.policies = [
            # Management Infrastructure Policy
            {
                'name': 'Management_Full_Access',
                'description': 'Full access for UniFi devices',
                'type': 'secure',
                'group_name': 'Cameras',
                'config': {
                    'internet': {
                        'enabled': True,
                        'access_type': 'allow_all'
                    },
                    'local': {
                        'enabled': True,
                        'access_type': 'allow_all'
                    }
                }
            },
            # Servers Policy
            {
                'name': 'Servers_Limited',
                'description': 'Limited access for servers',
                'type': 'secure',
                'group_name': 'Servers',
                'config': {
                    'internet': {
                        'enabled': True,
                        'access_type': 'allow_all'
                    },
                    'local': {
                        'enabled': True,
                        'access_type': 'limited',
                        'allowed_groups': ['Mac']
                    }
                }
            },
            # User Workstations Policy
            {
                'name': 'User_Access',
                'description': 'Standard access for workstations',
                'type': 'secure',
                'group_name': 'Mac',
                'config': {
                    'internet': {
                        'enabled': True,
                        'access_type': 'allow_all'
                    },
                    'local': {
                        'enabled': True,
                        'access_type': 'limited',
                        'allowed_groups': ['Servers', 'IoT - Apple']
                    }
                }
            },
            # Apple IoT Policy
            {
                'name': 'IoT_Apple_Limited',
                'description': 'Limited access for Apple IoT',
                'type': 'secure',
                'group_name': 'IoT - Apple',
                'config': {
                    'internet': {
                        'enabled': True,
                        'access_type': 'limited',
                        'allowed_services': ['apple_services']
                    },
                    'local': {
                        'enabled': True,
                        'access_type': 'limited',
                        'allowed_groups': ['Mac']
                    }
                }
            },
            # QoS Policies
            {
                'name': 'Management_Priority',
                'description': 'Priority for management traffic',
                'type': 'qos',
                'group_name': 'Cameras',
                'config': {
                    'behavior': 'prioritize',
                    'interface': 'Telstra 1000/400 FTTP v1'
                }
            },
            {
                'name': 'Server_Bandwidth',
                'description': 'Bandwidth limits for servers',
                'type': 'qos',
                'group_name': 'Servers',
                'config': {
                    'behavior': 'limit',
                    'interface': 'Telstra 1000/400 FTTP v1',
                    'download_limit': 500,  # Mbps
                    'upload_limit': 500     # Mbps
                }
            },
            {
                'name': 'IoT_Bandwidth',
                'description': 'Bandwidth limits for IoT',
                'type': 'qos',
                'group_name': 'IoT - Apple',
                'config': {
                    'behavior': 'limit',
                    'interface': 'Telstra 1000/400 FTTP v1',
                    'download_limit': 100,  # Mbps
                    'upload_limit': 50      # Mbps
                }
            },
            # Route Policies (WAN Selection)
            {
                'name': 'Management_Route',
                'description': 'Route management via main WAN',
                'type': 'route',
                'group_name': 'Cameras',
                'config': {
                    'interface': 'Telstra 1000/400 FTTP v1',
                    'type': 'all_traffic'
                }
            }
        ]

    def get_groups(self):
        """Get client groups"""
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

    def get_existing_policies(self):
        """Get existing object policies"""
        try:
            response = self.session.get('https://mars.int.bozza.au/proxy/network/api/s/default/rest/object-policy')
            if response.status_code == 200:
                return response.json().get('data', [])
        except Exception as e:
            print(f"Error getting policies: {str(e)}")
        return []

    def create_policy(self, policy, group_id):
        """Create an object policy"""
        try:
            # Convert our policy definition to UniFi OS 9.5.12 format
            api_payload = {
                'name': policy['name'],
                'enabled': True,
                'site_id': 'default',
                'description': policy['description'],
                'object_type': policy['type'],
                'match_type': 'group',
                'match_group_id': group_id,
                'schedule': {
                    'type': 'always'
                }
            }
            
            # Add type-specific configuration
            if policy['type'] == 'secure':
                api_payload.update({
                    'action': 'allow',
                    'internet': {
                        'enabled': True,
                        'type': policy['config']['internet']['access_type']
                    },
                    'local': {
                        'enabled': True,
                        'type': policy['config']['local']['access_type'],
                        'targets': policy['config']['local'].get('allowed_groups', [])
                    }
                })
            elif policy['type'] == 'qos':
                api_payload.update({
                    'action': policy['config']['behavior'],
                    'interface': policy['config']['interface'],
                    'download_rate': policy['config'].get('download_limit', 0),
                    'upload_rate': policy['config'].get('upload_limit', 0)
                })
            elif policy['type'] == 'route':
                api_payload.update({
                    'action': 'route',
                    'interface': policy['config']['interface'],
                    'kill_switch': True
                })
            
            response = self.session.post(
                'https://mars.int.bozza.au/proxy/network/api/s/default/rest/object-policy',
                json=api_payload
            )
            
            if response.status_code == 200:
                return True, "Policy created successfully"
            else:
                return False, f"API returned {response.status_code}: {response.text[:100]}"
                
        except Exception as e:
            return False, f"Error: {str(e)}"

    def setup_policies(self, dry_run=False):
        """Set up all object policies"""
        print("🎯 Setting Up Object-Oriented Network Policies")
        print("=" * 60)
        
        if dry_run:
            print("🔍 DRY RUN MODE - No actual changes will be made")
            print()
        
        # Get groups
        groups = self.get_groups()
        if not groups:
            print("❌ No groups found!")
            return False
            
        print("📋 Found groups:")
        for name, group_id in groups.items():
            print(f"   • {name}")
        
        # Show existing policies
        existing = self.get_existing_policies()
        if existing:
            print(f"\n📋 Found {len(existing)} existing policies:")
            for policy in existing:
                print(f"   • {policy.get('name')}")
        
        print("\n🔧 Policies to create:")
        for policy in self.policies:
            print(f"   • {policy['name']} ({policy['type']}) → {policy['group_name']}")
        
        if dry_run:
            return True
            
        # Confirm before proceeding
        confirm = input("\n🔴 Proceed with policy creation? (y/N): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("❌ Operation cancelled")
            return False
        
        # Create policies
        success_count = 0
        
        for policy in self.policies:
            print(f"\n📝 Creating policy: {policy['name']}")
            print(f"   Type: {policy['type']}")
            print(f"   Group: {policy['group_name']}")
            
            group_id = groups.get(policy['group_name'])
            if not group_id:
                print(f"   ❌ Group not found: {policy['group_name']}")
                continue
            
            success, message = self.create_policy(policy, group_id)
            
            if success:
                print(f"   ✅ {message}")
                success_count += 1
            else:
                print(f"   ❌ Failed: {message}")
            
            # Small delay between creations
            time.sleep(2)
        
        print(f"\n📊 Policy Creation Results:")
        print(f"   ✅ Successfully created: {success_count}/{len(self.policies)} policies")
        
        return success_count > 0

def main():
    """Main function"""
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    manager = ObjectPolicyManager()
    
    # Check for dry run mode
    import sys
    dry_run = '--dry-run' in sys.argv or '--test' in sys.argv
    
    return manager.setup_policies(dry_run=dry_run)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)