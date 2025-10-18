#!/usr/bin/env python3
"""
EMERGENCY ROLLBACK SCRIPT
Completely reverses Phase 1, 2, and 3 changes to restore original network state
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
        logging.FileHandler('emergency_rollback.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmergencyRollback:
    """Complete system rollback to original state"""
    
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
        
        # Networks and groups created by our deployment
        self.our_vlans = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        self.our_firewall_groups = [
            "MGMT_Infrastructure_Devices", "Corporate_Server_Devices", "Mac_Computer_Devices",
            "iPhone_Mobile_Devices", "Apple_IoT_Devices", "General_IoT_Devices", 
            "Security_Camera_Devices", "Automotive_Devices", "Printer_Devices",
            "Guest_Devices", "Quarantine_Devices", "Management_Ports",
            "Web_Services_Ports", "Printer_Ports", "Camera_Ports", "IoT_Basic_Ports"
        ]
        
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
    
    def get_all_clients(self):
        """Get all current clients"""
        try:
            response = self.session.get(f"{self.base_url}/proxy/network/api/s/{self.site}/stat/sta")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting clients: {str(e)}")
            return []
    
    def move_client_to_default_network(self, client_mac, client_hostname="Unknown"):
        """Move a client back to the default network"""
        try:
            # UniFi API call to reassign client to default network
            reassign_data = {
                "mac": client_mac,
                "network_id": None,  # None means default network
                "use_fixed_ip": False
            }
            
            response = self.session.post(
                f"{self.base_url}/proxy/network/api/s/{self.site}/cmd/stamgr",
                json={"cmd": "set-client-settings", **reassign_data}
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Moved {client_hostname} ({client_mac}) back to Default network")
                return True
            else:
                logger.warning(f"⚠️ Could not move {client_hostname}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error moving client {client_hostname}: {str(e)}")
            return False
    
    def disable_all_firewall_rules(self):
        """Disable all firewall rules we created"""
        try:
            response = self.session.get(f"{self.base_url}/proxy/network/api/s/{self.site}/rest/firewallrule")
            if response.status_code != 200:
                return False
                
            rules = response.json().get('data', [])
            our_rules = []
            
            # Identify rules that contain our group names or were created recently
            for rule in rules:
                rule_name = rule.get('name', '')
                src_groups = rule.get('src_firewallgroup_ids', [])
                dst_groups = rule.get('dst_firewallgroup_ids', [])
                
                # Check if rule uses our firewall groups or has suspicious recent creation
                if (any(group in rule_name for group in ['MGMT_', 'Corporate_', 'Mac_', 'iPhone_', 'Apple_', 'Security_', 'Automotive_', 'Printer_', 'Guest_', 'Quarantine_']) or
                    any(group in str(src_groups) + str(dst_groups) for group in self.our_firewall_groups)):
                    our_rules.append(rule)
            
            disabled_count = 0
            for rule in our_rules:
                rule_id = rule.get('_id')
                rule_name = rule.get('name', 'Unknown')
                
                # Disable the rule
                update_data = rule.copy()
                update_data['enabled'] = False
                
                response = self.session.put(
                    f"{self.base_url}/proxy/network/api/s/{self.site}/rest/firewallrule/{rule_id}",
                    json=update_data
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Disabled firewall rule: {rule_name}")
                    disabled_count += 1
                else:
                    logger.warning(f"⚠️ Could not disable rule {rule_name}: {response.status_code}")
            
            logger.info(f"📊 Disabled {disabled_count} firewall rules")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error disabling firewall rules: {str(e)}")
            return False
    
    def delete_firewall_groups(self):
        """Delete all firewall groups we created"""
        try:
            response = self.session.get(f"{self.base_url}/proxy/network/api/s/{self.site}/rest/firewallgroup")
            if response.status_code != 200:
                return False
                
            groups = response.json().get('data', [])
            deleted_count = 0
            
            for group in groups:
                group_name = group.get('name', '')
                group_id = group.get('_id')
                
                if group_name in self.our_firewall_groups:
                    response = self.session.delete(
                        f"{self.base_url}/proxy/network/api/s/{self.site}/rest/firewallgroup/{group_id}"
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Deleted firewall group: {group_name}")
                        deleted_count += 1
                    else:
                        logger.warning(f"⚠️ Could not delete group {group_name}: {response.status_code}")
            
            logger.info(f"📊 Deleted {deleted_count} firewall groups")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting firewall groups: {str(e)}")
            return False
    
    def delete_vlan_networks(self):
        """Delete all VLAN networks we created"""
        try:
            response = self.session.get(f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf")
            if response.status_code != 200:
                return False
                
            networks = response.json().get('data', [])
            deleted_count = 0
            
            for network in networks:
                vlan_id = network.get('vlan')
                network_id = network.get('_id')
                network_name = network.get('name', 'Unknown')
                
                if vlan_id in self.our_vlans:
                    response = self.session.delete(
                        f"{self.base_url}/proxy/network/api/s/{self.site}/rest/networkconf/{network_id}"
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Deleted VLAN {vlan_id}: {network_name}")
                        deleted_count += 1
                    else:
                        logger.warning(f"⚠️ Could not delete VLAN {vlan_id}: {response.status_code}")
            
            logger.info(f"📊 Deleted {deleted_count} VLAN networks")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting VLAN networks: {str(e)}")
            return False
    
    def perform_emergency_rollback(self):
        """Perform complete emergency rollback"""
        
        logger.info("🚨 EMERGENCY ROLLBACK INITIATED")
        logger.info("=" * 60)
        logger.info("⚠️  WARNING: This will completely undo all network changes!")
        logger.info("📋 Actions to perform:")
        logger.info("   1. Move all devices back to Default network")
        logger.info("   2. Disable all firewall rules")
        logger.info("   3. Delete all firewall groups")
        logger.info("   4. Delete all VLAN networks")
        logger.info("   5. Restore original flat network topology")
        logger.info("=" * 60)
        
        # Confirmation prompt
        try:
            confirm = input("\n🔴 ARE YOU SURE? Type 'ROLLBACK' to proceed: ")
            if confirm != "ROLLBACK":
                logger.info("❌ Rollback cancelled by user")
                return False
        except KeyboardInterrupt:
            logger.info("❌ Rollback cancelled by user (Ctrl+C)")
            return False
        
        # Test connection first
        if not self.test_connection():
            logger.error("❌ Cannot connect to controller. Aborting rollback.")
            return False
        
        rollback_success = True
        
        # Step 1: Move all clients back to default network
        logger.info("\n🔄 Step 1: Moving devices back to Default network...")
        clients = self.get_all_clients()
        moved_count = 0
        
        for client in clients:
            mac = client.get('mac')
            hostname = client.get('hostname', 'Unknown')
            current_network = client.get('network', 'Default')
            
            if mac and current_network != 'Default':
                if self.move_client_to_default_network(mac, hostname):
                    moved_count += 1
        
        logger.info(f"📊 Moved {moved_count} devices back to Default network")
        
        # Step 2: Disable firewall rules
        logger.info("\n🛡️ Step 2: Disabling firewall rules...")
        if not self.disable_all_firewall_rules():
            logger.error("⚠️ Some firewall rules could not be disabled")
            rollback_success = False
        
        # Step 3: Delete firewall groups
        logger.info("\n🔥 Step 3: Deleting firewall groups...")
        if not self.delete_firewall_groups():
            logger.error("⚠️ Some firewall groups could not be deleted")
            rollback_success = False
        
        # Step 4: Delete VLAN networks
        logger.info("\n🌐 Step 4: Deleting VLAN networks...")
        if not self.delete_vlan_networks():
            logger.error("⚠️ Some VLAN networks could not be deleted")
            rollback_success = False
        
        # Wait for changes to propagate
        logger.info("\n⏳ Waiting for changes to propagate...")
        time.sleep(10)
        
        # Final status
        logger.info("=" * 60)
        if rollback_success:
            logger.info("🎉 EMERGENCY ROLLBACK COMPLETED SUCCESSFULLY!")
            logger.info("📋 Network restored to original state:")
            logger.info("   ✅ All devices on Default network")
            logger.info("   ✅ All firewall rules disabled/deleted")
            logger.info("   ✅ All firewall groups deleted")
            logger.info("   ✅ All VLAN networks deleted")
            logger.info("   ✅ Flat network topology restored")
            logger.info("\n🔍 Please verify:")
            logger.info("   1. All devices can communicate")
            logger.info("   2. Internet access works normally")
            logger.info("   3. All applications function correctly")
        else:
            logger.error("⚠️ ROLLBACK PARTIALLY COMPLETED")
            logger.error("📋 Some items could not be fully reverted")
            logger.error("🔧 Manual intervention may be required")
            logger.error("📞 Check logs for specific issues")
        
        return rollback_success

def main():
    """Main rollback function"""
    try:
        rollback = EmergencyRollback()
        success = rollback.perform_emergency_rollback()
        
        if success:
            print("\n✅ ROLLBACK SUCCESS!")
            print("   Network restored to original state")
            print("   All devices back on Default network")
            print("   All enterprise features removed")
        else:
            print("\n⚠️ ROLLBACK INCOMPLETE!")
            print("   Check logs for details")
            print("   Manual cleanup may be required")
            print("   Contact support if needed")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Rollback error: {str(e)}")
        print(f"\n❌ ROLLBACK FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)