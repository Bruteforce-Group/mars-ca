#!/usr/bin/env python3
"""
Get Current UCG-Fiber Configuration
Retrieves existing networks, firewall rules, and device information
"""

import os
import json
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
from pprint import pprint

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def get_current_config():
    """Retrieve current UniFi configuration"""
    
    host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', 'mars.int.bozza.au')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    if not api_key:
        print("❌ API key not found in environment")
        return False
    
    print(f"🔍 Gathering Current Configuration from {host}")
    print("=" * 60)
    
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    })
    
    base_url = f"https://{host}"
    config_data = {}
    
    # List of endpoints to query
    endpoints = {
        'system_info': '/proxy/network/api/s/default/stat/sysinfo',
        'networks': '/proxy/network/api/s/default/rest/networkconf', 
        'firewall_groups': '/proxy/network/api/s/default/rest/firewallgroup',
        'firewall_rules': '/proxy/network/api/s/default/rest/firewallrule',
        'devices': '/proxy/network/api/s/default/stat/device',
        'clients': '/proxy/network/api/s/default/stat/sta',
        'sites': '/proxy/network/api/s/default/stat/sites',
        'port_profiles': '/proxy/network/api/s/default/rest/portconf',
        'wlan_groups': '/proxy/network/api/s/default/rest/wlangroup',
        'wlans': '/proxy/network/api/s/default/rest/wlanconf',
    }
    
    print("📊 Retrieving Configuration Data:")
    
    for name, endpoint in endpoints.items():
        try:
            print(f"  📋 Getting {name}...")
            response = session.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                config_data[name] = data.get('data', [])
                count = len(config_data[name]) if isinstance(config_data[name], list) else 1
                print(f"    ✅ Success - {count} items")
            else:
                print(f"    ❌ Failed - {response.status_code}")
                config_data[name] = None
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            config_data[name] = None
    
    # Save configuration to file
    timestamp = int(time.time())
    config_file = f"current_config_{timestamp}.json"
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2, default=str)
        print(f"\n💾 Configuration saved to: {config_file}")
    except Exception as e:
        print(f"\n❌ Failed to save config: {str(e)}")
    
    # Display summary
    print(f"\n📈 Configuration Summary:")
    print("=" * 40)
    
    if config_data.get('system_info'):
        sysinfo = config_data['system_info'][0] if config_data['system_info'] else {}
        print(f"🖥️  Controller: {sysinfo.get('hostname', 'Unknown')}")
        print(f"📡 Model: {sysinfo.get('udm_version', sysinfo.get('version', 'Unknown'))}")
        print(f"🔧 Version: {sysinfo.get('version', 'Unknown')}")
    
    if config_data.get('networks'):
        networks = config_data['networks']
        print(f"\n🌐 Networks ({len(networks)} configured):")
        for net in networks:
            vlan = net.get('vlan', 'N/A')
            name = net.get('name', 'Unnamed')
            purpose = net.get('purpose', 'user-defined')
            print(f"   VLAN {vlan}: {name} ({purpose})")
    
    if config_data.get('firewall_groups'):
        fw_groups = config_data['firewall_groups']
        print(f"\n🔥 Firewall Groups ({len(fw_groups)} configured):")
        for group in fw_groups:
            name = group.get('name', 'Unnamed')
            group_type = group.get('group_type', 'unknown')
            print(f"   {name} ({group_type})")
    
    if config_data.get('firewall_rules'):
        fw_rules = config_data['firewall_rules']
        print(f"\n🛡️  Firewall Rules ({len(fw_rules)} configured):")
        for rule in fw_rules:
            name = rule.get('name', 'Unnamed')
            action = rule.get('action', 'unknown')
            enabled = rule.get('enabled', False)
            status = "✅" if enabled else "❌"
            print(f"   {status} {name} ({action})")
    
    if config_data.get('devices'):
        devices = config_data['devices']
        print(f"\n📱 Network Devices ({len(devices)} connected):")
        device_types = {}
        for device in devices:
            dev_type = device.get('type', 'unknown')
            device_types[dev_type] = device_types.get(dev_type, 0) + 1
        
        for dev_type, count in device_types.items():
            print(f"   {dev_type}: {count}")
    
    if config_data.get('clients'):
        clients = config_data['clients']
        print(f"\n👥 Client Devices ({len(clients)} connected):")
        client_types = {}
        for client in clients:
            os_name = client.get('os_name', client.get('oui', 'unknown'))
            client_types[os_name] = client_types.get(os_name, 0) + 1
        
        for client_type, count in sorted(client_types.items()):
            print(f"   {client_type}: {count}")
    
    print(f"\n✅ Configuration retrieval complete!")
    return config_data

if __name__ == "__main__":
    config = get_current_config()
    if config:
        print(f"\n🚀 Ready to analyze differences and plan deployment!")
    else:
        print(f"\n❌ Failed to retrieve configuration")