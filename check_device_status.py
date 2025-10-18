#!/usr/bin/env python3
"""
Device Status Checker
Monitor device VLAN assignments and connectivity during manual moves
"""

import os
import requests
import time
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def get_device_status():
    """Get current device status and VLAN assignments"""
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
        'Content-Type': 'application/json'
    })
    
    try:
        response = session.get('https://mars.int.bozza.au/proxy/network/api/s/default/stat/sta')
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            print(f"❌ API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return []

def display_device_status():
    """Display formatted device status"""
    print("\n🔍 Current Device Status")
    print("=" * 80)
    
    clients = get_device_status()
    if not clients:
        print("❌ No devices found or connection failed")
        return
    
    # Device classification for display
    device_targets = {
        'upstairs---study': 'MGMT_Infrastructure (VLAN 5)',
        'lounge-room': 'MGMT_Infrastructure (VLAN 5)', 
        'backup': 'MGMT_Infrastructure (VLAN 5)',
        'g5-pro': 'MGMT_Infrastructure (VLAN 5)',
        'driveway': 'MGMT_Infrastructure (VLAN 5)',
        'Boz-MBP-M3-Max': 'User_Devices (VLAN 20)',
        'truenas': 'Corporate_Servers (VLAN 10)',
        'ControlAppleTV2': 'Apple_IoT (VLAN 30)',
        'ringring': 'Security_Cameras (VLAN 50)'
    }
    
    print(f"{'Device Name':<20} {'Current IP':<15} {'Network':<20} {'Target Network':<25}")
    print("-" * 80)
    
    for client in clients:
        hostname = client.get('hostname', 'Unknown')
        ip = client.get('ip', 'Unknown')
        network = client.get('network', 'Default')
        
        # Determine if device is in correct network
        target = device_targets.get(hostname, 'User_Devices (VLAN 20)')
        
        # Status indicator
        if network == 'Default':
            status = "⏳"  # Waiting to move
        elif target.split(' ')[0] in network:
            status = "✅"  # Correctly assigned
        else:
            status = "⚠️"   # Possibly incorrect
        
        print(f"{status} {hostname:<18} {ip:<15} {network:<20} {target}")
    
    # Summary
    default_count = sum(1 for c in clients if c.get('network', 'Default') == 'Default')
    moved_count = len(clients) - default_count
    
    print("\n📊 Summary:")
    print(f"   📱 Total devices: {len(clients)}")
    print(f"   ⏳ On Default network: {default_count}")
    print(f"   ✅ Moved to VLANs: {moved_count}")
    
    if default_count == 0:
        print("\n🎉 All devices have been moved to VLANs!")
        print("🔍 Verify each device is working correctly")
    elif moved_count > 0:
        print(f"\n🚀 Progress: {moved_count}/{len(clients)} devices moved")
        print("⏳ Continue moving remaining devices")
    else:
        print("\n📋 Ready to start moving devices to VLANs")
        print("💡 Start with non-critical devices first")

def monitor_mode():
    """Continuous monitoring mode"""
    print("🔄 Starting device monitoring mode...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Clear screen (works on most terminals)
            print("\033[2J\033[H", end="")
            
            print(f"🕐 Last updated: {time.strftime('%H:%M:%S')}")
            display_device_status()
            
            print("\n⏳ Refreshing in 10 seconds... (Ctrl+C to stop)")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")

def main():
    """Main function"""
    print("🎯 UniFi Device Status Checker")
    print("=" * 40)
    
    # Check if we have credentials
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found in environment")
        print("🔧 Run: source activate.sh")
        return
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        monitor_mode()
    else:
        display_device_status()
        print("\n💡 Usage:")
        print("   python3 check_device_status.py           # One-time check")
        print("   python3 check_device_status.py --monitor # Continuous monitoring")

if __name__ == "__main__":
    main()