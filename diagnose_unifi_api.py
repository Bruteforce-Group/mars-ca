#!/usr/bin/env python3
"""
UniFi API Diagnostic Script
Explores API endpoints to understand device management structure
"""

import os
import json
import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def setup_session():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'X-API-Key': os.getenv('UNIFI_API_KEY_MARS'),
        'Content-Type': 'application/json'
    })
    return session

def explore_api_endpoints(session):
    """Test various API endpoints to find the right one for device management"""
    
    base_url = 'https://mars.int.bozza.au/proxy/network/api/s/default'
    
    endpoints_to_test = [
        '/stat/sta',           # Client statistics
        '/rest/user',          # User management
        '/stat/device',        # Device statistics  
        '/rest/device',        # Device management
        '/list/user',          # List users
        '/cmd/stamgr',         # Station manager commands
        '/rest/networkconf',   # Network configuration
        '/stat/alluser',       # All users
    ]
    
    print("🔍 Testing API Endpoints:")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('data', []))
                print(f"✅ {endpoint:<20} → {response.status_code} ({count} items)")
            else:
                print(f"❌ {endpoint:<20} → {response.status_code}")
                
        except Exception as e:
            print(f"💥 {endpoint:<20} → Error: {str(e)[:50]}...")

def analyze_client_data(session):
    """Analyze client data structure to understand device management"""
    
    print(f"\n📱 Analyzing Client Data Structure:")
    print("=" * 50)
    
    try:
        response = session.get('https://mars.int.bozza.au/proxy/network/api/s/default/stat/sta')
        if response.status_code != 200:
            print(f"❌ Failed to get client data: {response.status_code}")
            return
            
        clients = response.json().get('data', [])
        print(f"📊 Found {len(clients)} clients")
        
        # Analyze key fields for each client
        for client in clients[:3]:  # Just first 3 for analysis
            hostname = client.get('hostname', client.get('name', 'Unknown'))
            print(f"\n🔍 Client: {hostname}")
            
            # Key fields for device management
            important_fields = [
                '_id', 'mac', 'hostname', 'name', 'network', 'network_id',
                'user_id', 'usergroup_id', 'is_wired', 'oui', 'device_id'
            ]
            
            for field in important_fields:
                if field in client:
                    value = client[field]
                    print(f"   {field:<15} → {value}")
        
        # Show all unique field names across clients
        all_fields = set()
        for client in clients:
            all_fields.update(client.keys())
        
        print(f"\n📋 All available fields ({len(all_fields)} total):")
        sorted_fields = sorted(all_fields)
        for i in range(0, len(sorted_fields), 4):
            fields_chunk = sorted_fields[i:i+4]
            print(f"   {' | '.join(f'{field:<18}' for field in fields_chunk)}")
            
    except Exception as e:
        print(f"💥 Error analyzing clients: {str(e)}")

def test_device_assignment_methods(session):
    """Test different methods for device assignment"""
    
    print(f"\n🧪 Testing Device Assignment Methods:")
    print("=" * 50)
    
    # Get a sample client for testing
    try:
        response = session.get('https://mars.int.bozza.au/proxy/network/api/s/default/stat/sta')
        clients = response.json().get('data', [])
        
        if not clients:
            print("❌ No clients found for testing")
            return
            
        # Find the Apple TV for testing (low risk)
        test_client = None
        for client in clients:
            hostname = client.get('hostname', client.get('name', ''))
            if 'ControlAppleTV2' in hostname:
                test_client = client
                break
        
        if not test_client:
            test_client = clients[0]  # Use first client
            
        client_mac = test_client.get('mac')
        client_id = test_client.get('_id')
        user_id = test_client.get('user_id')
        hostname = test_client.get('hostname', test_client.get('name', 'Unknown'))
        
        print(f"🎯 Test client: {hostname}")
        print(f"   MAC: {client_mac}")
        print(f"   ID: {client_id}")
        print(f"   User ID: {user_id}")
        
        # Get target network ID
        net_response = session.get('https://mars.int.bozza.au/proxy/network/api/s/default/rest/networkconf')
        networks = {}
        for net in net_response.json().get('data', []):
            networks[net.get('name')] = net.get('_id')
        
        target_network_id = networks.get('Apple_IoT')
        print(f"   Target Network ID: {target_network_id}")
        
        # Test Method 1: REST API with MAC
        print(f"\n🧪 Method 1: PUT /rest/user/{client_mac}")
        payload1 = {"network": target_network_id}
        try:
            response = session.put(
                f'https://mars.int.bozza.au/proxy/network/api/s/default/rest/user/{client_mac}',
                json=payload1,
                timeout=10
            )
            print(f"   Result: {response.status_code}")
            if response.status_code != 200:
                print(f"   Response: {response.text[:100]}...")
        except Exception as e:
            print(f"   Error: {str(e)[:50]}...")
        
        # Test Method 2: REST API with User ID
        if user_id:
            print(f"\n🧪 Method 2: PUT /rest/user/{user_id}")
            try:
                response = session.put(
                    f'https://mars.int.bozza.au/proxy/network/api/s/default/rest/user/{user_id}',
                    json=payload1,
                    timeout=10
                )
                print(f"   Result: {response.status_code}")
                if response.status_code != 200:
                    print(f"   Response: {response.text[:100]}...")
            except Exception as e:
                print(f"   Error: {str(e)[:50]}...")
        
        # Test Method 3: Command API
        print(f"\n🧪 Method 3: POST /cmd/stamgr")
        payload3 = {
            "cmd": "set-sta-network",
            "mac": client_mac,
            "network_id": target_network_id
        }
        try:
            response = session.post(
                'https://mars.int.bozza.au/proxy/network/api/s/default/cmd/stamgr',
                json=payload3,
                timeout=10
            )
            print(f"   Result: {response.status_code}")
            result = response.json() if response.status_code == 200 else None
            if result:
                print(f"   Meta RC: {result.get('meta', {}).get('rc')}")
            if response.status_code != 200:
                print(f"   Response: {response.text[:100]}...")
        except Exception as e:
            print(f"   Error: {str(e)[:50]}...")
            
    except Exception as e:
        print(f"💥 Error in testing: {str(e)}")

def main():
    """Main diagnostic function"""
    
    print("🔬 UniFi API Diagnostic Tool")
    print("=" * 60)
    
    if not os.getenv('UNIFI_API_KEY_MARS'):
        print("❌ UNIFI_API_KEY_MARS not found")
        print("🔧 Run: source activate.sh")
        return False
    
    session = setup_session()
    
    # Test basic connectivity
    try:
        response = session.get('https://mars.int.bozza.au/proxy/network/api/s/default/stat/sta')
        if response.status_code == 200:
            print("✅ API Connection successful")
        else:
            print(f"❌ API Connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"💥 Connection error: {str(e)}")
        return False
    
    # Run diagnostics
    explore_api_endpoints(session)
    analyze_client_data(session)
    test_device_assignment_methods(session)
    
    print(f"\n🎯 Diagnostic Complete!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)