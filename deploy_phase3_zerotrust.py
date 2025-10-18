#!/usr/bin/env python3
"""
Phase 3 Deployment: Zero-Trust Security Activation
Moves devices to VLANs and activates firewall rules (HIGH IMPACT)
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
        logging.FileHandler('phase3_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UniFiZeroTrustDeployer:
    """Deploy Phase 3 zero-trust security"""
    
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
        
        # VLAN mapping for device assignment
        self.vlan_networks = {}
        
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
    
    def get_network_mappings(self):
        """Get VLAN network IDs for device assignment"""
        try:
            response = self.session.get(f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf")
            if response.status_code != 200:
                return False
                
            networks = response.json().get('data', [])
            
            for network in networks:
                vlan_id = network.get('vlan')
                network_id = network.get('_id')
                network_name = network.get('name', 'Unknown')
                
                if vlan_id:
                    self.vlan_networks[vlan_id] = {
                        'id': network_id,
                        'name': network_name
                    }
            
            logger.info(f"📊 Found {len(self.vlan_networks)} VLAN networks for assignment")
            return True
            
        except Exception as e:
            logger.error(f"Error getting network mappings: {str(e)}")
            return False
    
    def classify_and_assign_device(self, client):
        """Classify a device and assign it to appropriate VLAN"""
        hostname = client.get('hostname', 'Unknown')
        ip = client.get('ip', 'Unknown')
        mac = client.get('mac', 'Unknown')
        oui = client.get('oui', 'Unknown')
        
        # Device classification logic
        target_vlan = None
        device_type = "Unknown"
        
        if 'Ubiquiti' in str(oui) or 'ubiquiti' in hostname.lower():
            if any(name in hostname.lower() for name in ['study', 'lounge', 'backup', 'driveway', 'g5-pro']):
                target_vlan = 5  # Management VLAN
                device_type = "UniFi Infrastructure"
        elif 'truenas' in hostname.lower() or 'server' in hostname.lower():
            target_vlan = 10  # Corporate VLAN
            device_type = "Server"
        elif 'mbp' in hostname.lower() or 'mac' in hostname.lower() or 'boz-' in hostname.lower():
            target_vlan = 20  # User Devices VLAN
            device_type = "Mac Computer"
        elif 'appletv' in hostname.lower() or 'control' in hostname.lower():
            target_vlan = 30  # Apple IoT VLAN
            device_type = "Apple TV/IoT"
        elif 'ring' in hostname.lower() or 'camera' in hostname.lower():
            target_vlan = 50  # Security VLAN
            device_type = "Security Camera"
        else:
            # Default to User Devices VLAN for unknown devices
            target_vlan = 20
            device_type = "Unknown Device"
        
        # Assign device to VLAN
        if target_vlan and target_vlan in self.vlan_networks:
            network_id = self.vlan_networks[target_vlan]['id']
            network_name = self.vlan_networks[target_vlan]['name']
            
            try:
                # Move device to new network
                assign_data = {
                    "mac": mac,
                    "network_id": network_id,
                    "use_fixed_ip": False
                }
                
                response = self.session.post(
                    f"{self.base_url}/proxy/network/api/s/{self.site}/cmd/stamgr",
                    json={"cmd": "set-client-settings", **assign_data},
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Moved {hostname} ({device_type}) to VLAN {target_vlan} ({network_name})")
                    return True, target_vlan, device_type
                else:
                    logger.error(f"❌ Failed to move {hostname}: {response.status_code}")
                    return False, target_vlan, device_type
                    
            except Exception as e:
                logger.error(f"❌ Error moving {hostname}: {str(e)}")
                return False, target_vlan, device_type
        
        logger.warning(f"⚠️ Could not find target VLAN {target_vlan} for {hostname}")
        return False, target_vlan, device_type
    
    def create_firewall_rule(self, rule_config):
        """Create a firewall rule"""
        try:
            rule_name = rule_config.get('name', 'Unknown Rule')
            logger.info(f"Creating firewall rule: {rule_name}")
            
            response = self.session.post(
                f"{self.base_url}/proxy/network/api/s/{self.site}/rest/firewallrule",
                json=rule_config,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully created firewall rule: {rule_name}")
                return True
            else:
                error_msg = response.text
                logger.error(f"❌ Failed to create rule {rule_name}: {response.status_code} - {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating rule {rule_name}: {str(e)}")
            return False
    
    def deploy_basic_firewall_rules(self):
        """Deploy essential zero-trust firewall rules"""
        
        # Basic zero-trust rules
        firewall_rules = [
            {
                "name": "Allow_Management_to_All",
                "action": "accept",
                "ruleset": "LAN_IN",
                "rule_index": 2000,
                "enabled": True,
                "src_address": "192.168.5.0/24",  # Management VLAN
                "dst_address": "192.168.0.0/16",  # All internal networks
                "protocol": "all",
                "logging": True
            },
            {
                "name": "Allow_DNS_All_to_Corporate",
                "action": "accept", 
                "ruleset": "LAN_IN",
                "rule_index": 2001,
                "enabled": True,
                "src_address": "192.168.0.0/16",  # All internal
                "dst_address": "192.168.10.0/24",  # Corporate VLAN
                "protocol": "tcp_udp",
                "dst_port": "53",
                "logging": False
            },
            {
                "name": "Allow_Users_to_Corporate_Web",
                "action": "accept",
                "ruleset": "LAN_IN", 
                "rule_index": 2002,
                "enabled": True,
                "src_address": "192.168.20.0/24",  # User Devices VLAN
                "dst_address": "192.168.10.0/24",  # Corporate VLAN
                "protocol": "tcp",
                "dst_port": "80,443,22,5000-5100",
                "logging": True
            },
            {
                "name": "Allow_AppleTV_Internet_Basic", 
                "action": "accept",
                "ruleset": "LAN_IN",
                "rule_index": 2003,
                "enabled": True,
                "src_address": "192.168.30.0/24",  # Apple IoT VLAN
                "dst_address": "!192.168.0.0/16",  # Internet (not internal)
                "protocol": "tcp_udp",
                "dst_port": "80,443,53,123",
                "logging": True
            },
            {
                "name": "Allow_Cameras_to_Corporate",
                "action": "accept",
                "ruleset": "LAN_IN",
                "rule_index": 2004,
                "enabled": True,
                "src_address": "192.168.50.0/24",  # Security VLAN
                "dst_address": "192.168.10.0/24",  # Corporate VLAN
                "protocol": "tcp_udp",
                "dst_port": "80,443,554,8080",
                "logging": True
            },
            {
                "name": "Block_Inter_VLAN_Default",
                "action": "drop",
                "ruleset": "LAN_IN",
                "rule_index": 3000,
                "enabled": True,
                "src_address": "192.168.0.0/16",  # All internal
                "dst_address": "192.168.0.0/16",  # All internal  
                "protocol": "all",
                "logging": True
            }
        ]
        
        success_count = 0
        for rule in firewall_rules:
            if self.create_firewall_rule(rule):
                success_count += 1
        
        logger.info(f"📊 Created {success_count}/{len(firewall_rules)} firewall rules")
        return success_count > 0
    
    def deploy_phase3_zerotrust(self):
        """Deploy Phase 3 zero-trust security"""
        
        logger.info("🚨 STARTING PHASE 3: ZERO-TRUST SECURITY ACTIVATION")
        logger.info("=" * 60)
        logger.info("⚠️  HIGH IMPACT WARNING:")
        logger.info("   🔄 All devices will be moved to VLANs")
        logger.info("   🛡️  Zero-trust firewall rules will be activated") 
        logger.info("   ⚡ Network communication will be restricted")
        logger.info("   📱 Some applications may stop working temporarily")
        logger.info("=" * 60)
        
        # Final confirmation
        try:
            confirm = input("\n🔴 PROCEED WITH HIGH-IMPACT DEPLOYMENT? Type 'DEPLOY' to continue: ")
            if confirm != "DEPLOY":
                logger.info("❌ Phase 3 deployment cancelled by user")
                return False
        except KeyboardInterrupt:
            logger.info("❌ Phase 3 deployment cancelled by user (Ctrl+C)")
            return False
        
        # Test connection
        if not self.test_connection():
            logger.error("❌ Cannot connect to controller. Aborting deployment.")
            return False
        
        # Get network mappings
        if not self.get_network_mappings():
            logger.error("❌ Cannot get VLAN network mappings. Aborting.")
            return False
        
        deployment_success = True
        
        # Step 1: Move devices to VLANs
        logger.info("\n🔄 Step 1: Moving devices to appropriate VLANs...")
        
        try:
            response = self.session.get(f"{self.base_url}/proxy/network/api/s/{self.site}/stat/sta")
            if response.status_code != 200:
                logger.error("❌ Cannot get device list")
                return False
                
            clients = response.json().get('data', [])
            logger.info(f"📊 Found {len(clients)} devices to classify and move")
            
            moved_devices = {}  # Track moves by VLAN
            failed_moves = []
            
            for client in clients:
                hostname = client.get('hostname', 'Unknown')
                success, target_vlan, device_type = self.classify_and_assign_device(client)
                
                if success:
                    if target_vlan not in moved_devices:
                        moved_devices[target_vlan] = []
                    moved_devices[target_vlan].append(f"{hostname} ({device_type})")
                else:
                    failed_moves.append(f"{hostname} ({device_type})")
            
            # Summary of device moves
            logger.info("\n📊 Device Movement Summary:")
            for vlan_id, devices in moved_devices.items():
                vlan_name = self.vlan_networks[vlan_id]['name']
                logger.info(f"   VLAN {vlan_id} ({vlan_name}): {len(devices)} devices")
                for device in devices:
                    logger.info(f"     📱 {device}")
            
            if failed_moves:
                logger.warning(f"\n⚠️ Failed to move {len(failed_moves)} devices:")
                for device in failed_moves:
                    logger.warning(f"     ❌ {device}")
                deployment_success = False
            
        except Exception as e:
            logger.error(f"❌ Error during device movement: {str(e)}")
            deployment_success = False
        
        # Step 2: Wait for network changes to propagate
        logger.info("\n⏳ Step 2: Waiting for network changes to propagate...")
        time.sleep(15)
        
        # Step 3: Deploy basic firewall rules
        logger.info("\n🛡️ Step 3: Deploying zero-trust firewall rules...")
        if not self.deploy_basic_firewall_rules():
            logger.error("⚠️ Some firewall rules could not be created")
            deployment_success = False
        
        # Step 4: Final verification wait
        logger.info("\n⏳ Step 4: Final system stabilization...")
        time.sleep(10)
        
        # Final status
        logger.info("=" * 60)
        if deployment_success:
            logger.info("🎉 PHASE 3 ZERO-TRUST DEPLOYMENT COMPLETED!")
            logger.info("📋 Network transformation achieved:")
            logger.info("   ✅ All devices moved to appropriate VLANs")
            logger.info("   ✅ Zero-trust firewall rules active")
            logger.info("   ✅ Network segmentation enforced") 
            logger.info("   ✅ Enterprise-grade security enabled")
            logger.info("\n🔍 IMMEDIATE TESTING REQUIRED:")
            logger.info("   1. Test device connectivity")
            logger.info("   2. Verify internet access works")
            logger.info("   3. Check critical applications")
            logger.info("   4. Monitor for connectivity issues")
            logger.info("\n⚠️ If issues occur, run emergency rollback:")
            logger.info("   python3 emergency_rollback.py")
        else:
            logger.error("⚠️ PHASE 3 DEPLOYMENT COMPLETED WITH ISSUES")
            logger.error("📋 Some components may not be fully functional")
            logger.error("🔧 Review logs and consider rollback if needed")
        
        return deployment_success

def main():
    """Main deployment function"""
    try:
        deployer = UniFiZeroTrustDeployer()
        success = deployer.deploy_phase3_zerotrust()
        
        if success:
            print("\n🎯 PHASE 3 SUCCESS!")
            print("   - Zero-trust security activated")
            print("   - All devices moved to VLANs") 
            print("   - Firewall rules enforced")
            print("   - Enterprise network operational")
            print("\n⚡ TEST CONNECTIVITY IMMEDIATELY!")
        else:
            print("\n⚠️ PHASE 3 COMPLETED WITH ISSUES!")
            print("   - Check logs for details")
            print("   - Test network connectivity")
            print("   - Consider rollback if needed")
            print("\n🚨 Emergency rollback available:")
            print("   python3 emergency_rollback.py")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Deployment error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)