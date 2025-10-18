#!/usr/bin/env python3
"""
Phase 2 Deployment: Device Classification
Creates firewall groups and device classification rules without affecting traffic
"""

import os
import json
import requests
import time
import logging
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase2_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UniFiDeviceClassifier:
    """Deploy Phase 2 device classification"""
    
    def __init__(self):
        self.host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', 'mars.int.bozza.au')
        self.api_key = os.getenv('UNIFI_API_KEY_MARS')
        self.base_url = f"https://{self.host}"
        
        if not self.api_key:
            raise ValueError("API key not found in environment")
        
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        })
        
        self.site = "default"
        
    def test_connection(self):
        """Test API connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/proxy/network/api/s/{self.site}/stat/sysinfo")
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    sysinfo = data['data'][0]
                    logger.info(f"✅ Connected to {sysinfo.get('hostname', 'UniFi Controller')}")
                    return True
            logger.error(f"❌ Connection failed: {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"❌ Connection error: {str(e)}")
            return False
    
    def get_existing_firewall_groups(self):
        """Get current firewall groups"""
        try:
            response = self.session.get(f"{self.base_url}/proxy/network/api/s/{self.site}/rest/firewallgroup")
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting firewall groups: {str(e)}")
            return []
    
    def create_firewall_group(self, group_config):
        """Create a firewall group"""
        try:
            group_name = group_config.get('name', 'Unknown')
            logger.info(f"Creating firewall group: {group_name}")
            
            response = self.session.post(
                f"{self.base_url}/proxy/network/api/s/{self.site}/rest/firewallgroup",
                json=group_config,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully created firewall group: {group_name}")
                return True
            else:
                error_msg = response.text
                logger.error(f"❌ Failed to create firewall group {group_name}: {response.status_code} - {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating firewall group {group_name}: {str(e)}")
            return False
    
    def get_current_clients(self):
        """Get current connected clients for classification analysis"""
        try:
            response = self.session.get(f"{self.base_url}/proxy/network/api/s/{self.site}/stat/sta")
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting clients: {str(e)}")
            return []
    
    def deploy_phase2_classification(self):
        """Deploy all Phase 2 device classification groups"""
        
        # Define firewall groups for device classification
        firewall_groups = [
            {
                "name": "MGMT_Infrastructure_Devices",
                "group_type": "address-group",
                "group_members": [],
                "group_description": "Network infrastructure devices (UCG-Fiber, switches, APs)",
                "enabled": True
            },
            {
                "name": "Corporate_Server_Devices", 
                "group_type": "address-group",
                "group_members": [],
                "group_description": "Internal servers and admin workstations",
                "enabled": True
            },
            {
                "name": "Mac_Computer_Devices",
                "group_type": "address-group", 
                "group_members": [],
                "group_description": "Apple Mac computers and laptops",
                "enabled": True
            },
            {
                "name": "iPhone_Mobile_Devices",
                "group_type": "address-group",
                "group_members": [],
                "group_description": "Apple iPhone and iOS devices", 
                "enabled": True
            },
            {
                "name": "Apple_IoT_Devices",
                "group_type": "address-group",
                "group_members": [],
                "group_description": "Apple ecosystem IoT (Apple TV, HomePods, Apple Watch)",
                "enabled": True
            },
            {
                "name": "General_IoT_Devices",
                "group_type": "address-group",
                "group_members": [],
                "group_description": "General IoT devices (Tuya, smart home)",
                "enabled": True
            },
            {
                "name": "Security_Camera_Devices",
                "group_type": "address-group", 
                "group_members": [],
                "group_description": "IP cameras, NVR systems, security equipment",
                "enabled": True
            },
            {
                "name": "Automotive_Devices",
                "group_type": "address-group",
                "group_members": [],
                "group_description": "Tesla vehicles, car chargers, automotive devices",
                "enabled": True
            },
            {
                "name": "Printer_Devices",
                "group_type": "address-group",
                "group_members": [],
                "group_description": "Printers, scanners, print servers",
                "enabled": True
            },
            {
                "name": "Guest_Devices",
                "group_type": "address-group",
                "group_members": [],
                "group_description": "Guest and visitor devices",
                "enabled": True
            },
            {
                "name": "Quarantine_Devices",
                "group_type": "address-group",
                "group_members": [],
                "group_description": "Suspicious or compromised devices",
                "enabled": True
            },
            # Port groups for common services
            {
                "name": "Management_Ports",
                "group_type": "port-group",
                "group_members": ["22", "23", "80", "443", "161", "162", "8443"],
                "group_description": "Common management and monitoring ports",
                "enabled": True
            },
            {
                "name": "Web_Services_Ports", 
                "group_type": "port-group",
                "group_members": ["80", "443", "8080", "8443", "5000-5100"],
                "group_description": "HTTP/HTTPS and web service ports",
                "enabled": True
            },
            {
                "name": "Printer_Ports",
                "group_type": "port-group",
                "group_members": ["515", "631", "9100"],
                "group_description": "Common printer and print service ports",
                "enabled": True
            },
            {
                "name": "Camera_Ports",
                "group_type": "port-group", 
                "group_members": ["554", "80", "443", "8080", "37777"],
                "group_description": "IP camera streaming and management ports",
                "enabled": True
            },
            {
                "name": "IoT_Basic_Ports",
                "group_type": "port-group",
                "group_members": ["80", "443", "53", "123"],
                "group_description": "Basic internet access ports for IoT devices",
                "enabled": True
            }
        ]
        
        logger.info("🚀 Starting Phase 2: Device Classification Deployment")
        logger.info("=" * 60)
        
        # Test connection first
        if not self.test_connection():
            logger.error("❌ Cannot connect to controller. Aborting deployment.")
            return False
        
        # Get current connected devices for analysis
        current_clients = self.get_current_clients()
        logger.info(f"📊 Found {len(current_clients)} connected devices for classification analysis")
        
        # Analyze current devices
        if current_clients:
            logger.info("📱 Current Device Analysis:")
            device_types = {}
            apple_devices = 0
            
            for client in current_clients:
                hostname = client.get('hostname', 'Unknown')
                os_name = client.get('os_name', client.get('oui', 'Unknown'))
                mac = client.get('mac', 'Unknown')
                ip = client.get('ip', 'Unknown')
                
                device_types[os_name] = device_types.get(os_name, 0) + 1
                
                if 'Apple' in str(os_name) or 'iOS' in str(os_name) or 'macOS' in str(os_name):
                    apple_devices += 1
                
                logger.info(f"   📱 {hostname:<20} {ip:<15} {os_name:<15} {mac}")
            
            logger.info(f"\n📊 Device Type Summary:")
            for dev_type, count in sorted(device_types.items()):
                if str(dev_type) != 'Unknown':
                    logger.info(f"   {dev_type}: {count}")
            
            logger.info(f"🍎 Apple ecosystem devices detected: {apple_devices}")
        
        # Get existing firewall groups to avoid conflicts
        existing_groups = self.get_existing_firewall_groups()
        existing_names = {group.get('name') for group in existing_groups if group.get('name')}
        
        logger.info(f"\n📊 Found {len(existing_groups)} existing firewall groups")
        
        # Deploy firewall groups
        success_count = 0
        failed_groups = []
        
        for group in firewall_groups:
            group_name = group['name']
            
            # Check for conflicts
            if group_name in existing_names:
                logger.warning(f"⚠️  Firewall group '{group_name}' already exists, skipping...")
                continue
            
            # Create the firewall group
            if self.create_firewall_group(group):
                success_count += 1
                logger.info(f"  ✅ {group_name} - SUCCESS")
            else:
                failed_groups.append(group_name)
                logger.error(f"  ❌ {group_name} - FAILED")
        
        # Summary
        logger.info("=" * 60)
        logger.info(f"📈 Phase 2 Deployment Summary:")
        logger.info(f"  ✅ Successfully created: {success_count} firewall groups")
        logger.info(f"  ❌ Failed to create: {len(failed_groups)} groups")
        
        if failed_groups:
            logger.error(f"  Failed groups: {failed_groups}")
        
        if success_count > 0:
            logger.info(f"🎉 Phase 2 deployment completed!")
            logger.info(f"📝 What was accomplished:")
            logger.info(f"  ✅ Device classification groups created")
            logger.info(f"  ✅ Port groups defined for common services")
            logger.info(f"  ✅ Foundation ready for traffic rules")
            logger.info(f"  ✅ No impact on current device connectivity")
            logger.info(f"\n📝 Next steps:")
            logger.info(f"  1. Verify firewall groups are accessible")
            logger.info(f"  2. Review device classification accuracy")  
            logger.info(f"  3. Plan Phase 3 implementation timing")
            logger.info(f"  4. Proceed to Phase 3 when ready (HIGH IMPACT)")
            return True
        else:
            logger.error(f"❌ Phase 2 deployment failed - no groups created")
            return False

def main():
    """Main deployment function"""
    try:
        classifier = UniFiDeviceClassifier()
        success = classifier.deploy_phase2_classification()
        
        if success:
            print("\n🎯 Phase 2 SUCCESS!")
            print("   - Device classification groups created")
            print("   - Port groups defined") 
            print("   - Ready for Phase 3 (traffic rules)")
            print("   - Current connectivity unchanged")
            print("\n⚠️  IMPORTANT: Phase 3 will move devices and restrict traffic!")
        else:
            print("\n❌ Phase 2 FAILED!")
            print("   - Check logs for details")
            print("   - Verify credentials and connectivity")
            print("   - Try individual group creation")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Deployment error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)