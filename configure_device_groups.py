#!/usr/bin/env python3
"""
Configure UniFi Device Groups
Clean up old groups and configure proper enterprise device groups
"""

import os
import json
import requests
import time
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def setup_unifi_session():
    """Set up UniFi API session"""
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
        'Content-Type': 'application/json'
    })
    return session

def get_current_groups(session):
    """Get current device groups"""
    try:
        response = session.get('https://mars.int.bozza.au/proxy/network/api/s/default/rest/firewallgroup')
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except Exception as e:
        print(f"Error getting groups: {str(e)}")
        return []

def delete_old_groups(session):
    """Delete old device groups that might conflict"""
    print("🧹 Cleaning up old device groups...")
    
    # Groups to potentially remove (common default/test groups)
    groups_to_remove = ['Cameras', 'Daniel', 'IoT', 'IoT - Apple', 'IoT - Tuya', 'iPhones', 'Mac']
    
    current_groups = get_current_groups(session)
    deleted_count = 0
    
    for group in current_groups:
        group_name = group.get('name', '')
        group_id = group.get('_id')
        
        if group_name in groups_to_remove:
            try:
                response = session.delete(
                    f"https://mars.int.bozza.au/proxy/network/api/s/default/rest/firewallgroup/{group_id}"
                )
                if response.status_code == 200:
                    print(f"   ✅ Deleted old group: {group_name}")
                    deleted_count += 1
                else:
                    print(f"   ⚠️ Could not delete {group_name}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting {group_name}: {str(e)}")
    
    print(f"📊 Cleaned up {deleted_count} old groups")
    return deleted_count > 0

def create_enterprise_groups(session):
    """Create proper enterprise device groups"""
    print("\n🏗️ Creating enterprise device groups...")
    
    # Define our enterprise device groups
    device_groups = [
        {
            "name": "Management_Infrastructure",
            "group_type": "address-group",
            "group_members": [],
            "group_description": "UCG-Fiber, switches, access points, and network infrastructure"
        },
        {
            "name": "Corporate_Servers", 
            "group_type": "address-group",
            "group_members": [],
            "group_description": "Internal servers, NAS, and business-critical systems"
        },
        {
            "name": "User_Workstations",
            "group_type": "address-group", 
            "group_members": [],
            "group_description": "Mac computers, Windows PCs, and user workstations"
        },
        {
            "name": "Mobile_Devices",
            "group_type": "address-group",
            "group_members": [],
            "group_description": "iPhones, iPads, Android phones and tablets"
        },
        {
            "name": "Apple_Ecosystem",
            "group_type": "address-group",
            "group_members": [],
            "group_description": "Apple TV, HomePods, Apple Watch, and Apple IoT devices"
        },
        {
            "name": "Smart_Home_IoT",
            "group_type": "address-group",
            "group_members": [],
            "group_description": "Tuya devices, smart plugs, sensors, and general IoT"
        },
        {
            "name": "Security_Systems",
            "group_type": "address-group", 
            "group_members": [],
            "group_description": "IP cameras, NVR systems, and security equipment"
        },
        {
            "name": "Automotive_Systems",
            "group_type": "address-group",
            "group_members": [],
            "group_description": "Tesla vehicles, car chargers, and automotive devices"
        },
        {
            "name": "Print_Services",
            "group_type": "address-group",
            "group_members": [],
            "group_description": "Printers, scanners, and print servers"
        },
        {
            "name": "Guest_Devices",
            "group_type": "address-group",
            "group_members": [],
            "group_description": "Visitor devices and temporary network access"
        },
        {
            "name": "Quarantine_Zone",
            "group_type": "address-group",
            "group_members": [],
            "group_description": "Suspicious, compromised, or unknown devices"
        }
    ]
    
    success_count = 0
    for group in device_groups:
        try:
            response = session.post(
                'https://mars.int.bozza.au/proxy/network/api/s/default/rest/firewallgroup',
                json=group,
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"   ✅ Created: {group['name']}")
                success_count += 1
            else:
                # Check if it already exists
                if "already exists" in response.text.lower():
                    print(f"   ℹ️ Already exists: {group['name']}")
                    success_count += 1
                else:
                    print(f"   ⚠️ Failed: {group['name']} ({response.status_code})")
        except Exception as e:
            print(f"   ❌ Error: {group['name']} - {str(e)}")
    
    print(f"\n📊 Created {success_count}/{len(device_groups)} enterprise device groups")
    return success_count

def show_current_groups(session):
    """Display current device groups"""
    print("\n📋 Current Device Groups:")
    current_groups = get_current_groups(session)
    
    if not current_groups:
        print("   No groups found")
        return
    
    # Group by type
    address_groups = [g for g in current_groups if g.get('group_type') == 'address-group']
    port_groups = [g for g in current_groups if g.get('group_type') == 'port-group']
    
    if address_groups:
        print("   📱 Address Groups:")
        for group in address_groups:
            name = group.get('name', 'Unknown')
            desc = group.get('group_description', 'No description')
            member_count = len(group.get('group_members', []))
            print(f"      • {name} ({member_count} members) - {desc[:50]}...")
    
    if port_groups:
        print("   🔌 Port Groups:")  
        for group in port_groups:
            name = group.get('name', 'Unknown')
            desc = group.get('group_description', 'No description')
            member_count = len(group.get('group_members', []))
            print(f"      • {name} ({member_count} ports) - {desc[:50]}...")

def assign_devices_to_groups(session):
    """Provide instructions for assigning devices to groups"""
    print("\n📋 Device Assignment Instructions:")
    print("=" * 50)
    print("Now that device groups are created, you can assign devices in the UniFi interface:")
    print()
    print("🖥️ **In UniFi Console → Network → Clients:**")
    print("1. Click on each device")
    print("2. Look for 'Groups' or 'Device Groups' section")  
    print("3. Add device to appropriate group:")
    print()
    print("📱 **Device Assignment Plan:**")
    assignments = [
        ("Boz-MBP-M3-Max", "User_Workstations", "Your Mac computer"),
        ("truenas", "Corporate_Servers", "TrueNAS storage server"),
        ("ControlAppleTV2", "Apple_Ecosystem", "Apple TV"),
        ("ringring", "Security_Systems", "Ring security camera"),
        ("upstairs---study", "Management_Infrastructure", "UniFi AP"),
        ("lounge-room", "Management_Infrastructure", "UniFi AP"),
        ("backup", "Management_Infrastructure", "UniFi device"),
        ("g5-pro", "Management_Infrastructure", "UniFi camera"),
        ("driveway", "Management_Infrastructure", "UniFi device")
    ]
    
    for device, group, description in assignments:
        print(f"   📍 {device:<20} → {group:<25} ({description})")

def main():
    """Main function"""
    print("🎯 UniFi Device Groups Configuration")
    print("=" * 50)
    print("This will clean up old groups and create proper enterprise device groups")
    print()
    
    # Check credentials
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    session = setup_unifi_session()
    
    # Show current state
    print("📊 Current Device Groups Status:")
    show_current_groups(session)
    
    # Confirm cleanup
    print(f"\n⚠️ This will:")
    print(f"   🧹 Remove old/conflicting device groups")
    print(f"   🏗️ Create new enterprise device groups") 
    print(f"   📋 Provide assignment instructions")
    
    confirm = input(f"\n🔴 Proceed? (y/N): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("❌ Operation cancelled")
        return False
    
    # Clean up old groups
    cleanup_success = delete_old_groups(session)
    
    # Wait a moment for changes to propagate
    if cleanup_success:
        print("⏳ Waiting for changes to propagate...")
        time.sleep(5)
    
    # Create new enterprise groups
    create_count = create_enterprise_groups(session)
    
    # Show final state
    print(f"\n📊 Final Device Groups Status:")
    show_current_groups(session)
    
    # Provide assignment instructions
    assign_devices_to_groups(session)
    
    print(f"\n🎉 Device Groups Configuration Complete!")
    print(f"📋 Next steps:")
    print(f"   1. In UniFi Console → Network → Clients")
    print(f"   2. Assign each device to appropriate group")
    print(f"   3. Move devices to VLANs using the group assignments")
    print(f"   4. Test connectivity after each change")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)