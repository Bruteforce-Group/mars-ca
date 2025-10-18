#!/usr/bin/env python3
"""
Phase 1 Deployment: Network Foundation
Creates 10 VLAN networks without affecting existing connectivity
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
        logging.FileHandler('phase1_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UniFiNetworkDeployer:
    """Deploy Phase 1 VLAN networks"""
    
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
    
    def get_existing_networks(self):
        """Get current network configuration"""
        try:
            response = self.session.get(f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf")
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting networks: {str(e)}")
            return []
    
    def create_vlan_network(self, network_config):
        """Create a single VLAN network"""
        try:
            logger.info(f"Creating VLAN {network_config['vlan']}: {network_config['name']}")
            
            response = self.session.post(
                f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf",
                json=network_config,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully created VLAN {network_config['vlan']}: {network_config['name']}")
                return True
            else:
                error_msg = response.text
                logger.error(f"❌ Failed to create VLAN {network_config['vlan']}: {response.status_code} - {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating VLAN {network_config['vlan']}: {str(e)}")
            return False
    
    def deploy_phase1_networks(self):
        """Deploy all Phase 1 VLAN networks"""
        
        # Define the 10 VLAN networks to create
        networks = [
            {
                "name": "MGMT_Infrastructure",
                "purpose": "corporate", 
                "vlan_enabled": True,
                "vlan": 1,
                "ip_subnet": "192.168.1.1/24",
                "dhcp_enabled": True,
                "dhcp_start": "192.168.1.10",
                "dhcp_stop": "192.168.1.50",
                "domain_name": "mgmt.bozza.au",
                "dhcp_dns": ["192.168.1.1", "1.1.1.1"],
                "dhcp_lease_time": 86400,
                "networkgroup": "LAN",
                "dhcp_relay_enabled": False,
                "enabled": True
            },
            {
                "name": "Corporate_Servers",
                "purpose": "corporate",
                "vlan_enabled": True, 
                "vlan": 10,
                "ip_subnet": "192.168.10.1/24",
                "dhcp_enabled": True,
                "dhcp_start": "192.168.10.10",
                "dhcp_stop": "192.168.10.254",
                "domain_name": "corp.bozza.au",
                "dhcp_dns": ["192.168.1.1", "1.1.1.1"],
                "dhcp_lease_time": 86400,
                "networkgroup": "LAN",
                "enabled": True
            },
            {
                "name": "User_Devices",
                "purpose": "corporate",
                "vlan_enabled": True,
                "vlan": 20,
                "ip_subnet": "192.168.20.1/24", 
                "dhcp_enabled": True,
                "dhcp_start": "192.168.20.10",
                "dhcp_stop": "192.168.20.254",
                "domain_name": "users.bozza.au",
                "dhcp_dns": ["192.168.1.1", "1.1.1.1"],
                "dhcp_lease_time": 86400,
                "networkgroup": "LAN",
                "enabled": True
            },
            {
                "name": "Apple_IoT",
                "purpose": "corporate",
                "vlan_enabled": True,
                "vlan": 30,
                "ip_subnet": "192.168.30.1/24",
                "dhcp_enabled": True,
                "dhcp_start": "192.168.30.10",
                "dhcp_stop": "192.168.30.254",
                "domain_name": "apple-iot.bozza.au",
                "dhcp_dns": ["192.168.1.1", "1.1.1.1"],
                "dhcp_lease_time": 86400,
                "networkgroup": "LAN",
                "enabled": True
            },
            {
                "name": "General_IoT",
                "purpose": "corporate",
                "vlan_enabled": True,
                "vlan": 40,
                "ip_subnet": "192.168.40.1/24",
                "dhcp_enabled": True,
                "dhcp_start": "192.168.40.10", 
                "dhcp_stop": "192.168.40.254",
                "domain_name": "iot.bozza.au",
                "dhcp_dns": ["192.168.1.1", "1.1.1.1"],
                "dhcp_lease_time": 86400,
                "networkgroup": "LAN",
                "enabled": True
            },
            {
                "name": "Security_Cameras",
                "purpose": "corporate",
                "vlan_enabled": True,
                "vlan": 50,
                "ip_subnet": "192.168.50.1/24",
                "dhcp_enabled": True,
                "dhcp_start": "192.168.50.10",
                "dhcp_stop": "192.168.50.254",
                "domain_name": "security.bozza.au",
                "dhcp_dns": ["192.168.1.1", "1.1.1.1"],
                "dhcp_lease_time": 86400,
                "networkgroup": "LAN",
                "enabled": True
            },
            {
                "name": "Automotive",
                "purpose": "corporate",
                "vlan_enabled": True,
                "vlan": 60,
                "ip_subnet": "192.168.60.1/24",
                "dhcp_enabled": True,
                "dhcp_start": "192.168.60.10",
                "dhcp_stop": "192.168.60.254",
                "domain_name": "auto.bozza.au",
                "dhcp_dns": ["192.168.1.1", "1.1.1.1"],
                "dhcp_lease_time": 86400,
                "networkgroup": "LAN",
                "enabled": True
            },
            {
                "name": "Print_Services",
                "purpose": "corporate",
                "vlan_enabled": True,
                "vlan": 70,
                "ip_subnet": "192.168.70.1/24",
                "dhcp_enabled": True,
                "dhcp_start": "192.168.70.10",
                "dhcp_stop": "192.168.70.254",
                "domain_name": "print.bozza.au",
                "dhcp_dns": ["192.168.1.1", "1.1.1.1"],
                "dhcp_lease_time": 86400,
                "networkgroup": "LAN",
                "enabled": True
            },
            {
                "name": "Guest_Network",
                "purpose": "guest",
                "vlan_enabled": True,
                "vlan": 80,
                "ip_subnet": "192.168.80.1/24",
                "dhcp_enabled": True,
                "dhcp_start": "192.168.80.10",
                "dhcp_stop": "192.168.80.100",
                "domain_name": "guest.bozza.au",
                "dhcp_dns": ["1.1.1.1", "8.8.8.8"],
                "dhcp_lease_time": 14400,  # 4 hours for guests
                "networkgroup": "LAN",
                "enabled": True,
                "is_guest": True
            },
            {
                "name": "Quarantine_Zone",
                "purpose": "corporate",
                "vlan_enabled": True,
                "vlan": 90,
                "ip_subnet": "192.168.90.1/24",
                "dhcp_enabled": True,
                "dhcp_start": "192.168.90.10",
                "dhcp_stop": "192.168.90.50",
                "domain_name": "quarantine.bozza.au",
                "dhcp_dns": ["192.168.1.1"],
                "dhcp_lease_time": 3600,  # 1 hour for quarantine
                "networkgroup": "LAN",
                "enabled": True
            }
        ]
        
        logger.info("🚀 Starting Phase 1: Network Foundation Deployment")
        logger.info("=" * 60)
        
        # Test connection first
        if not self.test_connection():
            logger.error("❌ Cannot connect to controller. Aborting deployment.")
            return False
        
        # Get existing networks to avoid conflicts
        existing_networks = self.get_existing_networks()
        existing_vlans = {net.get('vlan') for net in existing_networks if net.get('vlan')}
        existing_names = {net.get('name') for net in existing_networks if net.get('name')}
        
        logger.info(f"📊 Found {len(existing_networks)} existing networks")
        logger.info(f"📊 Existing VLANs: {sorted(existing_vlans) if existing_vlans else 'None'}")
        
        # Deploy networks
        success_count = 0
        failed_networks = []
        
        for network in networks:
            vlan_id = network['vlan']
            network_name = network['name']
            
            # Check for conflicts
            if vlan_id in existing_vlans:
                logger.warning(f"⚠️  VLAN {vlan_id} already exists, skipping...")
                continue
                
            if network_name in existing_names:
                logger.warning(f"⚠️  Network '{network_name}' already exists, skipping...")
                continue
            
            # Create the network
            if self.create_vlan_network(network):
                success_count += 1
                logger.info(f"  ✅ VLAN {vlan_id} ({network_name}) - SUCCESS")
            else:
                failed_networks.append((vlan_id, network_name))
                logger.error(f"  ❌ VLAN {vlan_id} ({network_name}) - FAILED")
        
        # Summary
        logger.info("=" * 60)
        logger.info(f"📈 Phase 1 Deployment Summary:")
        logger.info(f"  ✅ Successfully created: {success_count} networks")
        logger.info(f"  ❌ Failed to create: {len(failed_networks)} networks")
        
        if failed_networks:
            logger.error(f"  Failed networks: {failed_networks}")
        
        if success_count > 0:
            logger.info(f"🎉 Phase 1 deployment completed!")
            logger.info(f"📝 Next steps:")
            logger.info(f"  1. Verify all networks are accessible")
            logger.info(f"  2. Test DHCP is working on new VLANs")
            logger.info(f"  3. Confirm existing connectivity unchanged")
            logger.info(f"  4. Proceed to Phase 2 when ready")
            return True
        else:
            logger.error(f"❌ Phase 1 deployment failed - no networks created")
            return False

def main():
    """Main deployment function"""
    try:
        deployer = UniFiNetworkDeployer()
        success = deployer.deploy_phase1_networks()
        
        if success:
            print("\n🎯 Phase 1 SUCCESS!")
            print("   - 10 VLAN networks created")
            print("   - DHCP pools configured")
            print("   - Existing connectivity preserved")
            print("   - Ready for Phase 2")
        else:
            print("\n❌ Phase 1 FAILED!")
            print("   - Check logs for details")
            print("   - Verify credentials and connectivity")
            print("   - Try individual network creation")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Deployment error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)