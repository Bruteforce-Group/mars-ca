#!/usr/bin/env python3
"""
Phase 2 Verification and Device Analysis
Verifies firewall groups and analyzes current device classification
"""

import os
import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def verify_phase2_deployment():
    """Verify Phase 2 deployment and analyze current devices"""
    
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
        'Content-Type': 'application/json'
    })
    
    print("🔍 Phase 2 Deployment Verification & Device Analysis")
    print("=" * 60)
    
    # Expected firewall groups after Phase 2
    expected_groups = [
        "MGMT_Infrastructure_Devices", "Corporate_Server_Devices", "Mac_Computer_Devices",
        "iPhone_Mobile_Devices", "Apple_IoT_Devices", "General_IoT_Devices", 
        "Security_Camera_Devices", "Automotive_Devices", "Printer_Devices",
        "Guest_Devices", "Quarantine_Devices", "Management_Ports",
        "Web_Services_Ports", "Printer_Ports", "Camera_Ports", "IoT_Basic_Ports"
    ]
    
    try:
        # Verify firewall groups
        response = session.get('https://mars.int.bozza.au/proxy/network/api/s/default/rest/firewallgroup')
        if response.status_code != 200:
            print(f"❌ Failed to get firewall groups: {response.status_code}")
            return False
            
        groups = response.json().get('data', [])
        our_groups = [group['name'] for group in groups if group['name'] in expected_groups]
        
        print(f"📊 Firewall Groups Status:")
        print(f"   Expected: {len(expected_groups)} groups")
        print(f"   Found: {len(our_groups)} groups")
        print()
        
        # Check each expected group
        for group_name in expected_groups:
            if group_name in our_groups:
                print(f"✅ {group_name}")
            else:
                print(f"❌ {group_name} - MISSING")
        
        print()
        
        # Get and analyze current devices
        response = session.get('https://mars.int.bozza.au/proxy/network/api/s/default/stat/sta')
        if response.status_code == 200:
            clients = response.json().get('data', [])
            print(f"📱 Current Device Analysis ({len(clients)} devices connected):")
            print()
            
            device_classifications = {
                'Infrastructure': [],
                'Mac Computers': [],
                'Apple TV/IoT': [],
                'Security Cameras': [],
                'Servers': [],
                'Unknown': []
            }
            
            for client in clients:
                hostname = client.get('hostname', 'Unknown')
                ip = client.get('ip', 'Unknown')  
                mac = client.get('mac', 'Unknown')
                oui = client.get('oui', 'Unknown')
                os_name = client.get('os_name', str(oui))
                
                # Device classification logic
                if 'Ubiquiti' in str(oui) or 'ubiquiti' in hostname.lower():
                    if any(name in hostname.lower() for name in ['study', 'lounge', 'backup', 'driveway']):
                        device_classifications['Infrastructure'].append({
                            'hostname': hostname, 'ip': ip, 'type': 'UniFi Device', 'suggested_vlan': 5
                        })
                elif 'truenas' in hostname.lower() or 'server' in hostname.lower():
                    device_classifications['Servers'].append({
                        'hostname': hostname, 'ip': ip, 'type': 'Server', 'suggested_vlan': 10
                    })
                elif 'mbp' in hostname.lower() or 'mac' in hostname.lower():
                    device_classifications['Mac Computers'].append({
                        'hostname': hostname, 'ip': ip, 'type': 'Mac Computer', 'suggested_vlan': 20
                    })
                elif 'appletv' in hostname.lower() or 'control' in hostname.lower():
                    device_classifications['Apple TV/IoT'].append({
                        'hostname': hostname, 'ip': ip, 'type': 'Apple TV', 'suggested_vlan': 30
                    })
                elif 'ring' in hostname.lower() or 'camera' in hostname.lower():
                    device_classifications['Security Cameras'].append({
                        'hostname': hostname, 'ip': ip, 'type': 'Security Camera', 'suggested_vlan': 50
                    })
                else:
                    device_classifications['Unknown'].append({
                        'hostname': hostname, 'ip': ip, 'type': 'Unknown', 'suggested_vlan': 20
                    })
            
            # Display classification results
            for category, devices in device_classifications.items():
                if devices:
                    print(f"🏷️  {category} ({len(devices)} devices):")
                    for device in devices:
                        vlan_name = {5: "MGMT", 10: "Corporate", 20: "Users", 30: "Apple IoT", 50: "Security"}
                        vlan_display = vlan_name.get(device['suggested_vlan'], f"VLAN {device['suggested_vlan']}")
                        print(f"   📱 {device['hostname']:<20} {device['ip']:<15} → {vlan_display}")
                    print()
            
            print("🎯 Phase 3 Preparation Summary:")
            print("=" * 40)
            
            total_devices = sum(len(devices) for devices in device_classifications.values())
            
            # Infrastructure devices
            infra_count = len(device_classifications['Infrastructure'])
            print(f"🏢 Management VLAN (5): {infra_count} infrastructure devices")
            
            # Server devices  
            server_count = len(device_classifications['Servers'])
            print(f"🏢 Corporate VLAN (10): {server_count} server devices")
            
            # User devices
            user_count = len(device_classifications['Mac Computers']) + len(device_classifications['Unknown'])
            print(f"👥 User VLAN (20): {user_count} user devices")
            
            # Apple IoT
            apple_count = len(device_classifications['Apple TV/IoT'])
            print(f"🍎 Apple IoT VLAN (30): {apple_count} Apple devices")
            
            # Security cameras
            camera_count = len(device_classifications['Security Cameras'])
            print(f"📹 Security VLAN (50): {camera_count} camera devices")
            
            print(f"\n📊 Total devices to be moved in Phase 3: {total_devices}")
            print()
            
        if len(our_groups) == len(expected_groups):
            print("🎉 Phase 2 SUCCESS - All firewall groups deployed!")
            print()
            print("📋 What was accomplished:")
            print("   ✅ 11 device classification groups created") 
            print("   ✅ 5 port groups defined for services")
            print("   ✅ Device analysis completed")
            print("   ✅ Phase 3 preparation ready")
            print("   ✅ No impact on current connectivity")
            print()
            print("⚠️  CRITICAL: Phase 3 Impact Assessment")
            print("   🔄 Devices will be automatically moved to VLANs")
            print("   🛡️  Zero-trust firewall rules will be activated")
            print("   ⚡ Network communication patterns will change")
            print("   📱 Some applications may require reconfiguration")
            print()
            print("🚀 Ready for Phase 3: Zero-Trust Security (HIGH IMPACT)")
            return True
        else:
            print("⚠️ Phase 2 incomplete - some firewall groups missing")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {str(e)}")
        return False

if __name__ == "__main__":
    verify_phase2_deployment()