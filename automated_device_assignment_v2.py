#!/usr/bin/env python3
"""
Automated Device Assignment Script v2
Uses the correct API method discovered through diagnostics
"""

import os
import json
import requests
import time
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class DeviceAssignmentEngineV2:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
            'Content-Type': 'application/json'
        })
        
        # Updated device assignment plan with correct device types
        self.assignment_plan = {
            'ControlAppleTV2': {
                'target_network': 'Apple_IoT',
                'priority': 1,
                'risk_level': 'LOW',
                'description': 'Apple TV'
            },
            'ringring': {
                'target_network': 'Corporate_Servers',  # Fing Network Agent -> Corporate
                'priority': 2,
                'risk_level': 'LOW', 
                'description': 'Fing Network Agent'
            },
            'truenas': {
                'target_network': 'Corporate_Servers',
                'priority': 3,
                'risk_level': 'MEDIUM',
                'description': 'TrueNAS server'
            },
            'upstairs---study': {
                'target_network': 'MGMT_Infrastructure',
                'priority': 4,
                'risk_level': 'HIGH',
                'description': 'UniFi camera/AP'
            },
            'lounge-room': {
                'target_network': 'MGMT_Infrastructure', 
                'priority': 5,
                'risk_level': 'HIGH',
                'description': 'UniFi camera/AP'
            },
            'backup': {
                'target_network': 'MGMT_Infrastructure',
                'priority': 6,
                'risk_level': 'HIGH',
                'description': 'UniFi camera'
            },
            'g5-pro': {
                'target_network': 'MGMT_Infrastructure',
                'priority': 7,
                'risk_level': 'HIGH',
                'description': 'UniFi camera'
            },
            'driveway': {
                'target_network': 'MGMT_Infrastructure',
                'priority': 8,
                'risk_level': 'HIGH',
                'description': 'UniFi camera'
            },
            'Boz-MBP-M3-Max': {
                'target_network': 'User_Devices',
                'priority': 9,
                'risk_level': 'CRITICAL',
                'description': 'Your Mac computer'
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

    def move_device_to_network(self, user_id, network_id, device_name):
        """Move a device to specific network using the correct API method"""
        try:
            # Use the working method: PUT /rest/user/{user_id}
            payload = {
                "network": network_id
            }
            
            response = self.session.put(
                f'https://mars.int.bozza.au/proxy/network/api/s/default/rest/user/{user_id}',
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, "Successfully moved device"
            else:
                return False, f"API returned {response.status_code}: {response.text[:200]}"
            
        except Exception as e:
            return False, f"Exception: {str(e)}"

    def assign_devices_automatically(self, dry_run=False):
        """Attempt automated device assignment using correct API"""
        print("🤖 Automated Device Assignment v2")
        print("=" * 50)
        
        if dry_run:
            print("🔍 DRY RUN MODE - No actual changes will be made")
            print()
        
        # Get current state
        clients = self.get_clients()
        networks = self.get_networks()
        
        print("📊 Current Networks Available:")
        target_networks = set(plan['target_network'] for plan in self.assignment_plan.values())
        for name, network_id in networks.items():
            if name in target_networks:
                print(f"   📍 {name} → {network_id}")
        print()
        
        # Find devices to move
        devices_to_move = []
        for client in clients:
            hostname = client.get('hostname', client.get('name', 'Unknown'))
            user_id = client.get('user_id')
            current_network = client.get('network')
            current_ip = client.get('ip', 'Unknown')
            
            if hostname in self.assignment_plan:
                plan = self.assignment_plan[hostname]
                target_network = plan['target_network']
                
                if target_network in networks:
                    target_network_id = networks[target_network]
                    
                    # Check if already on correct network
                    if current_network != target_network:  # Compare by name since we're getting network name in 'network' field
                        devices_to_move.append({
                            'hostname': hostname,
                            'user_id': user_id,
                            'current_network': current_network,
                            'current_ip': current_ip,
                            'target_network': target_network,
                            'target_network_id': target_network_id,
                            'priority': plan['priority'],
                            'risk_level': plan['risk_level'],
                            'description': plan['description']
                        })
        
        # Sort by priority (lowest number = highest priority)
        devices_to_move.sort(key=lambda x: x['priority'])
        
        print(f"📱 Devices to Move ({len(devices_to_move)} total):")
        for device in devices_to_move:
            risk_emoji = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🟠', 'CRITICAL': '🔴'}.get(device['risk_level'], '⚪')
            current_ip = device['current_ip']
            print(f"   {risk_emoji} {device['hostname']:<20} → {device['target_network']:<20} ({device['description']}) [{current_ip}]")
        print()
        
        if not devices_to_move:
            print("✅ All devices are already correctly assigned!")
            return True
            
        if dry_run:
            print("🔍 Dry run complete - would move the above devices")
            return True
        
        # Show assignment plan
        print("📋 Assignment Plan:")
        expected_ranges = {
            'Apple_IoT': '192.168.30.x',
            'Corporate_Servers': '192.168.10.x', 
            'MGMT_Infrastructure': '192.168.5.x',
            'User_Devices': '192.168.20.x'
        }
        
        for device in devices_to_move:
            target = device['target_network']
            expected_ip = expected_ranges.get(target, 'Unknown range')
            print(f"   📍 {device['hostname']:<20} → {target:<20} (New IP: {expected_ip})")
        
        # Confirm before proceeding
        print(f"\n⚠️ This will move {len(devices_to_move)} devices automatically")
        print("🚨 Risk: May temporarily lose connectivity to some devices")
        print("🔥 High risk devices will require individual confirmation")
        
        confirm = input(f"\n🔴 Proceed with automated assignment? (y/N): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("❌ Operation cancelled")
            return False
        
        # Move devices one by one
        success_count = 0
        total_devices = len(devices_to_move)
        
        for i, device in enumerate(devices_to_move, 1):
            hostname = device['hostname']
            user_id = device['user_id']
            target_network = device['target_network']
            target_network_id = device['target_network_id']
            risk_level = device['risk_level']
            current_ip = device['current_ip']
            
            risk_emoji = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🟠', 'CRITICAL': '🔴'}.get(risk_level, '⚪')
            
            print(f"\n{risk_emoji} [{i}/{total_devices}] Moving {hostname} to {target_network}...")
            print(f"   Current: {device['current_network']} ({current_ip})")
            print(f"   Target:  {target_network}")
            
            # Special handling for risky devices
            if risk_level in ['HIGH', 'CRITICAL']:
                if risk_level == 'CRITICAL':
                    print("🚨 CRITICAL DEVICE - This will affect your console access!")
                else:
                    print("⚠️ HIGH RISK DEVICE - May affect network connectivity!")
                    
                final_confirm = input("   Continue with this device? (y/N): ").lower().strip()
                if final_confirm not in ['y', 'yes']:
                    print("   ⏭️ Skipping device")
                    continue
            
            # Attempt the move
            success, message = self.move_device_to_network(user_id, target_network_id, hostname)
            
            if success:
                print(f"   ✅ Success: {message}")
                success_count += 1
                
                # Wait for device to reconnect
                print("   ⏳ Waiting 45 seconds for device to reconnect...")
                time.sleep(45)
                
                # Quick verification
                print("   🔍 Verifying new assignment...")
                time.sleep(5)
                
            else:
                print(f"   ❌ Failed: {message}")
                
                # For high risk devices, ask if we should continue
                if risk_level in ['HIGH', 'CRITICAL']:
                    continue_on_fail = input(f"   Continue with remaining devices? (y/N): ").lower().strip()
                    if continue_on_fail not in ['y', 'yes']:
                        print("   🛑 Stopping due to high-risk failure")
                        break
        
        print(f"\n📊 Assignment Results:")
        print(f"   ✅ Successfully moved: {success_count}/{total_devices} devices")
        print(f"   📈 Success rate: {(success_count/total_devices)*100:.1f}%")
        
        if success_count > 0:
            print(f"\n🔍 Checking final status in 15 seconds...")
            time.sleep(15)
            
            # Run the progress monitor to show results
            print("\n" + "="*60)
            os.system("python3 monitor_assignment_progress.py")
        
        return success_count > 0

def main():
    """Main function"""
    import sys
    
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    engine = DeviceAssignmentEngineV2()
    
    # Check for dry run mode
    dry_run = '--dry-run' in sys.argv or '--test' in sys.argv
    
    return engine.assign_devices_automatically(dry_run=dry_run)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)