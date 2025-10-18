#!/usr/bin/env python3
"""
Monitor Device Assignment Progress
Real-time tracking of device group assignments and VLAN movements
"""

import os
import json
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class AssignmentMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
            'Content-Type': 'application/json'
        })
        
        # Expected assignments
        self.target_assignments = {
            'Boz-MBP-M3-Max': {'group': 'User_Workstations', 'vlan': 'User_Devices', 'ip_range': '192.168.20.x'},
            'truenas': {'group': 'Corporate_Servers', 'vlan': 'Corporate_Servers', 'ip_range': '192.168.10.x'},
            'ControlAppleTV2': {'group': 'Apple_Ecosystem', 'vlan': 'Apple_IoT', 'ip_range': '192.168.30.x'},
            'ringring': {'group': 'Security_Systems', 'vlan': 'Security_Cameras', 'ip_range': '192.168.50.x'},
            'upstairs---study': {'group': 'Management_Infrastructure', 'vlan': 'MGMT_Infrastructure', 'ip_range': '192.168.5.x'},
            'lounge-room': {'group': 'Management_Infrastructure', 'vlan': 'MGMT_Infrastructure', 'ip_range': '192.168.5.x'},
            'backup': {'group': 'Management_Infrastructure', 'vlan': 'MGMT_Infrastructure', 'ip_range': '192.168.5.x'},
            'g5-pro': {'group': 'Management_Infrastructure', 'vlan': 'MGMT_Infrastructure', 'ip_range': '192.168.5.x'},
            'driveway': {'group': 'Management_Infrastructure', 'vlan': 'MGMT_Infrastructure', 'ip_range': '192.168.5.x'}
        }

    def get_clients(self):
        """Get all clients from UniFi controller"""
        try:
            response = self.session.get('https://mars.int.bozza.au/proxy/network/api/s/default/stat/sta')
            if response.status_code == 200:
                return response.json().get('data', [])
        except Exception as e:
            print(f"Error getting clients: {str(e)}")
        return []

    def get_networks(self):
        """Get all networks from UniFi controller"""
        try:
            response = self.session.get('https://mars.int.bozza.au/proxy/network/api/s/default/rest/networkconf')
            if response.status_code == 200:
                networks = {}
                for net in response.json().get('data', []):
                    networks[net.get('_id')] = net.get('name', 'Unknown')
                return networks
        except Exception as e:
            print(f"Error getting networks: {str(e)}")
        return {}

    def check_ip_range(self, ip, expected_range):
        """Check if IP is in expected range"""
        if not ip:
            return False
        
        # Extract expected subnet from range (e.g., '192.168.20.x' -> '192.168.20.')
        expected_prefix = expected_range.replace('.x', '.')
        return ip.startswith(expected_prefix)

    def monitor_progress(self, continuous=False):
        """Monitor assignment progress"""
        print("🔍 Monitoring Device Assignment Progress")
        print("=" * 60)
        
        while True:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n📊 Status Check at {timestamp}")
            print("-" * 40)
            
            clients = self.get_clients()
            networks = self.get_networks()
            
            # Track progress
            total_devices = len(self.target_assignments)
            correctly_assigned = 0
            group_assigned = 0
            vlan_assigned = 0
            
            for client in clients:
                hostname = client.get('hostname', client.get('name', 'Unknown'))
                ip = client.get('ip')
                network_id = client.get('network')
                network_name = networks.get(network_id, 'Unknown')
                
                if hostname in self.target_assignments:
                    target = self.target_assignments[hostname]
                    
                    # Check VLAN assignment
                    vlan_correct = network_name == target['vlan']
                    if vlan_correct:
                        vlan_assigned += 1
                    
                    # Check IP range
                    ip_correct = self.check_ip_range(ip, target['ip_range'])
                    
                    # Status indicators
                    vlan_status = "✅" if vlan_correct else "❌"
                    ip_status = "✅" if ip_correct else "❌" if ip else "⏳"
                    
                    # Overall status
                    if vlan_correct and ip_correct:
                        correctly_assigned += 1
                        status = "🟢 COMPLETE"
                    elif vlan_correct:
                        status = "🟡 DHCP PENDING"
                    else:
                        status = "🔴 NEEDS ASSIGNMENT"
                    
                    print(f"📱 {hostname:<20} {status}")
                    print(f"   Network: {vlan_status} {network_name:<20} (Target: {target['vlan']})")
                    ip_display = ip if ip else "None"
                    print(f"   IP:      {ip_status} {ip_display:<15} (Expected: {target['ip_range']})")
                    print()
            
            # Summary
            print("📊 Progress Summary:")
            print(f"   🎯 Total Devices: {total_devices}")
            print(f"   🔄 VLAN Assigned: {vlan_assigned}/{total_devices}")
            print(f"   ✅ Fully Complete: {correctly_assigned}/{total_devices}")
            print(f"   📈 Progress: {(correctly_assigned/total_devices)*100:.1f}%")
            
            if correctly_assigned == total_devices:
                print("\n🎉 ALL DEVICES SUCCESSFULLY ASSIGNED!")
                print("🔒 Zero-trust network segmentation is now ACTIVE")
                break
            
            if not continuous:
                break
                
            print(f"\n⏳ Next check in 30 seconds... (Ctrl+C to stop)")
            try:
                time.sleep(30)
            except KeyboardInterrupt:
                print("\n\n👋 Monitoring stopped by user")
                break

def main():
    """Main function"""
    import sys
    
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    monitor = AssignmentMonitor()
    
    # Check for continuous mode
    continuous = '--monitor' in sys.argv or '--continuous' in sys.argv
    
    if continuous:
        print("🔄 Starting continuous monitoring (Ctrl+C to stop)")
        print("⏰ Updates every 30 seconds")
        print()
    
    monitor.monitor_progress(continuous=continuous)
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)