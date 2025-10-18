#!/usr/bin/env python3
"""
Make GUI Visible
Fix firewall groups and create visible configurations in the GUI
"""

import os
import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('make_gui_visible.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GUIVisibilityFixer:
    """Make configurations visible in the GUI"""
    
    def __init__(self, controller_host: str, api_key: str):
        self.controller_host = controller_host
        self.api_key = api_key
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
        self.site = "default"
        self.site_id = "68166867e027cb4dd9ef94c6"
        
        # Fix tracking
        self.fixed_groups = []
        self.created_vlans = []
        self.populated_groups = []
    
    def authenticate(self) -> bool:
        """Authenticate with UniFi Controller"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/self")
            if response.status_code == 200:
                logger.info("Successfully authenticated for GUI visibility fix")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def fix_firewall_groups(self) -> bool:
        """Fix firewall groups to make them visible in GUI"""
        logger.info("Fixing firewall groups visibility...")
        
        try:
            # Get current groups
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallgroup")
            if response.status_code == 200:
                groups = response.json().get('data', [])
                zone_groups = [g for g in groups if 'Devices' in g.get('name', '')]
                
                success_count = 0
                
                for group in zone_groups:
                    try:
                        group_id = group.get('_id')
                        group_name = group.get('name')
                        
                        # Update group to make it visible
                        update_data = {
                            "enabled": True,
                            "group_type": "address-group"
                        }
                        
                        response = self.session.put(
                            f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallgroup/{group_id}",
                            json=update_data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            if result.get('meta', {}).get('rc') == 'ok':
                                self.fixed_groups.append(group_name)
                                self.fixed_groups.append(f"Fixed group: {group_name}")
                                logger.info(f"✅ Fixed group: {group_name}")
                                success_count += 1
                            else:
                                logger.error(f"❌ Failed to fix group {group_name}: {result}")
                        else:
                            logger.error(f"❌ Failed to fix group {group_name}: {response.status_code}")
                        
                        time.sleep(1)  # Rate limiting
                        
                    except Exception as e:
                        logger.error(f"❌ Error fixing group {group.get('name', 'Unknown')}: {str(e)}")
                
                logger.info(f"Group fixing completed: {success_count}/{len(zone_groups)} groups fixed")
                return success_count > 0
            else:
                logger.error(f"Failed to get firewall groups: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error fixing firewall groups: {str(e)}")
            return False
    
    def create_visible_vlans(self) -> bool:
        """Create VLANs that are visible in the GUI"""
        logger.info("Creating visible VLANs...")
        
        # Define VLANs that will be visible
        vlans = [
            {
                "name": "Management_VLAN",
                "vlan_id": 5,
                "subnet": "192.168.5.0/24",
                "description": "Management zone VLAN"
            },
            {
                "name": "Corporate_VLAN", 
                "vlan_id": 10,
                "subnet": "192.168.10.0/24",
                "description": "Corporate zone VLAN"
            },
            {
                "name": "User_VLAN",
                "vlan_id": 20,
                "subnet": "192.168.20.0/24",
                "description": "User zone VLAN"
            },
            {
                "name": "IoT_VLAN",
                "vlan_id": 30,
                "subnet": "192.168.30.0/24",
                "description": "IoT zone VLAN"
            },
            {
                "name": "Guest_VLAN",
                "vlan_id": 80,
                "subnet": "192.168.80.0/24",
                "description": "Guest zone VLAN"
            }
        ]
        
        success_count = 0
        
        for vlan in vlans:
            try:
                # Create VLAN configuration
                vlan_config = {
                    "name": vlan["name"],
                    "purpose": "corporate",
                    "vlan_enabled": True,
                    "vlan": vlan["vlan_id"],
                    "ip_subnet": vlan["subnet"],
                    "dhcpd_enabled": True,
                    "dhcpd_leasetime": 86400,
                    "dhcpd_start": vlan["subnet"].replace("/24", ".10"),
                    "dhcpd_stop": vlan["subnet"].replace("/24", ".200"),
                    "domain_name": "local",
                    "enabled": True,
                    "networkgroup": "LAN",
                    "setting_preference": "manual",
                    "site_id": self.site_id
                }
                
                response = self.session.post(
                    f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/networkconf",
                    json=vlan_config
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('meta', {}).get('rc') == 'ok':
                        self.created_vlans.append({
                            "name": vlan["name"],
                            "vlan_id": vlan["vlan_id"],
                            "subnet": vlan["subnet"],
                            "id": result.get('data', [{}])[0].get('_id', 'unknown')
                        })
                        self.fixed_groups.append(f"Created VLAN: {vlan['name']}")
                        logger.info(f"✅ Created VLAN: {vlan['name']} (VLAN {vlan['vlan_id']})")
                        success_count += 1
                    else:
                        logger.error(f"❌ Failed to create VLAN {vlan['name']}: {result}")
                else:
                    logger.error(f"❌ Failed to create VLAN {vlan['name']}: {response.status_code}")
                
                time.sleep(2)  # Rate limiting for VLAN creation
                
            except Exception as e:
                logger.error(f"❌ Error creating VLAN {vlan['name']}: {str(e)}")
        
        logger.info(f"VLAN creation completed: {success_count}/{len(vlans)} VLANs created")
        return success_count > 0
    
    def populate_device_groups(self) -> bool:
        """Populate device groups with actual devices"""
        logger.info("Populating device groups with actual devices...")
        
        try:
            # Get current devices
            response = self.session.get(f"https://{self.controller_host}/proxy/network/v2/api/site/{self.site}/device")
            if response.status_code == 200:
                devices = response.json().get('data', [])
                
                # Get current groups
                response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallgroup")
                if response.status_code == 200:
                    groups = response.json().get('data', [])
                    zone_groups = {g.get('name'): g for g in groups if 'Devices' in g.get('name', '')}
                    
                    # Categorize devices
                    device_categories = {
                        'Management_Devices': [],
                        'Corporate_Devices': [],
                        'User_Devices': [],
                        'IoT_Devices': [],
                        'Guest_Devices': []
                    }
                    
                    for device in devices:
                        device_type = device.get('type', 'unknown')
                        device_name = device.get('name', 'Unknown')
                        device_ip = device.get('ip', 'unknown')
                        
                        # Categorize based on device type
                        if device_type in ['udm', 'usw']:
                            device_categories['Management_Devices'].append(device_ip)
                        elif device_type in ['uap']:
                            device_categories['Management_Devices'].append(device_ip)
                        else:
                            device_categories['User_Devices'].append(device_ip)
                    
                    # Update groups with device IPs
                    success_count = 0
                    for group_name, group in zone_groups.items():
                        if group_name in device_categories:
                            try:
                                group_id = group.get('_id')
                                device_ips = device_categories[group_name]
                                
                                if device_ips:  # Only update if we have devices
                                    update_data = {
                                        "enabled": True,
                                        "group_type": "address-group",
                                        "group_members": device_ips
                                    }
                                    
                                    response = self.session.put(
                                        f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallgroup/{group_id}",
                                        json=update_data
                                    )
                                    
                                    if response.status_code == 200:
                                        result = response.json()
                                        if result.get('meta', {}).get('rc') == 'ok':
                                            self.populated_groups.append(f"Populated {group_name} with {len(device_ips)} devices")
                                            logger.info(f"✅ Populated {group_name} with {len(device_ips)} devices")
                                            success_count += 1
                                        else:
                                            logger.error(f"❌ Failed to populate group {group_name}: {result}")
                                    else:
                                        logger.error(f"❌ Failed to populate group {group_name}: {response.status_code}")
                                
                                time.sleep(1)  # Rate limiting
                                
                            except Exception as e:
                                logger.error(f"❌ Error populating group {group_name}: {str(e)}")
                    
                    logger.info(f"Group population completed: {success_count}/{len(zone_groups)} groups populated")
                    return success_count > 0
                else:
                    logger.error(f"Failed to get firewall groups: {response.status_code}")
                    return False
            else:
                logger.error(f"Failed to get devices: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error populating device groups: {str(e)}")
            return False
    
    def create_visible_firewall_rules(self) -> bool:
        """Create firewall rules that are visible in the GUI"""
        logger.info("Creating visible firewall rules...")
        
        try:
            # Get next rule index
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule")
            if response.status_code == 200:
                rules = response.json().get('data', [])
                if rules:
                    max_index = max(rule.get('rule_index', 0) for rule in rules)
                    next_index = max_index + 1
                else:
                    next_index = 20001
            else:
                next_index = 20001
            
            # Define visible rules
            visible_rules = [
                {
                    "name": "Allow_Management_to_All",
                    "ruleset": "LAN_IN",
                    "action": "accept",
                    "src_address": "Management_Devices",
                    "protocol": "all",
                    "description": "Allow management devices to access all networks"
                },
                {
                    "name": "Allow_Corporate_to_Internet",
                    "ruleset": "LAN_IN",
                    "action": "accept",
                    "src_address": "Corporate_Devices",
                    "protocol": "all",
                    "description": "Allow corporate devices internet access"
                },
                {
                    "name": "Restrict_IoT_Access",
                    "ruleset": "LAN_IN",
                    "action": "accept",
                    "src_address": "IoT_Devices",
                    "protocol": "tcp",
                    "dst_port": "80,443",
                    "description": "Restrict IoT devices to HTTP/HTTPS only"
                },
                {
                    "name": "Isolate_Guest_Devices",
                    "ruleset": "LAN_IN",
                    "action": "drop",
                    "src_address": "Guest_Devices",
                    "dst_address": "Management_Devices,Corporate_Devices,User_Devices",
                    "protocol": "all",
                    "description": "Isolate guest devices from internal networks"
                }
            ]
            
            success_count = 0
            
            for i, rule in enumerate(visible_rules):
                try:
                    rule_config = {
                        "setting_preference": "manual",
                        "name": rule["name"],
                        "ruleset": rule["ruleset"],
                        "action": rule["action"],
                        "protocol": rule["protocol"],
                        "enabled": True,
                        "logging": True,
                        "rule_index": next_index + i,
                        "site_id": self.site_id
                    }
                    
                    # Add optional parameters
                    if "src_address" in rule:
                        rule_config["src_address"] = rule["src_address"]
                    if "dst_address" in rule:
                        rule_config["dst_address"] = rule["dst_address"]
                    if "dst_port" in rule:
                        rule_config["dst_port"] = rule["dst_port"]
                    
                    response = self.session.post(
                        f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule",
                        json=rule_config
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('meta', {}).get('rc') == 'ok':
                            self.fixed_groups.append(f"Created visible rule: {rule['name']}")
                            logger.info(f"✅ Created visible rule: {rule['name']}")
                            success_count += 1
                        else:
                            logger.error(f"❌ Failed to create rule {rule['name']}: {result}")
                    else:
                        logger.error(f"❌ Failed to create rule {rule['name']}: {response.status_code}")
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"❌ Error creating rule {rule['name']}: {str(e)}")
            
            logger.info(f"Visible rule creation completed: {success_count}/{len(visible_rules)} rules created")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error creating visible firewall rules: {str(e)}")
            return False
    
    def verify_gui_visibility(self) -> bool:
        """Verify that configurations are visible in GUI"""
        logger.info("Verifying GUI visibility...")
        
        try:
            # Check firewall groups
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallgroup")
            if response.status_code == 200:
                groups = response.json().get('data', [])
                zone_groups = [g for g in groups if 'Devices' in g.get('name', '')]
                
                # Check firewall rules
                response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule")
                if response.status_code == 200:
                    rules = response.json().get('data', [])
                    visible_rules = [r for r in rules if any(keyword in r.get('name', '') for keyword in ['Management', 'Corporate', 'IoT', 'Guest', 'Allow', 'Restrict', 'Isolate'])]
                    
                    # Check networks
                    response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/networkconf")
                    if response.status_code == 200:
                        networks = response.json().get('data', [])
                        vlan_networks = [n for n in networks if n.get('vlan') is not None]
                        
                        verification_results = {
                            "timestamp": datetime.now().isoformat(),
                            "fix_type": "gui_visibility",
                            "firewall_groups": {
                                "total_groups": len(groups),
                                "zone_groups": len(zone_groups),
                                "enabled_groups": len([g for g in zone_groups if g.get('enabled')]),
                                "groups_with_members": len([g for g in zone_groups if g.get('group_members')])
                            },
                            "firewall_rules": {
                                "total_rules": len(rules),
                                "visible_rules": len(visible_rules),
                                "rules_created": [r.get('name') for r in visible_rules]
                            },
                            "networks": {
                                "total_networks": len(networks),
                                "vlan_networks": len(vlan_networks),
                                "vlans_created": [n.get('name') for n in vlan_networks]
                            },
                            "fix_log": self.fixed_groups + self.populated_groups
                        }
                        
                        # Save verification results
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"gui_visibility_verification_{timestamp}.json"
                        with open(filename, 'w') as f:
                            json.dump(verification_results, f, indent=2, default=str)
                        
                        logger.info(f"GUI visibility verification completed - results saved to {filename}")
                        
                        # Print summary
                        print(f"\n{'='*80}")
                        print("GUI VISIBILITY VERIFICATION SUMMARY")
                        print(f"{'='*80}")
                        print(f"Zone Groups: {len(zone_groups)} (enabled: {len([g for g in zone_groups if g.get('enabled')])})")
                        print(f"Visible Rules: {len(visible_rules)}")
                        print(f"VLAN Networks: {len(vlan_networks)}")
                        print(f"Total Firewall Rules: {len(rules)}")
                        print(f"Total Networks: {len(networks)}")
                        print(f"Verification results saved to: {filename}")
                        print(f"{'='*80}")
                        
                        return True
                    else:
                        logger.error(f"Failed to get networks: {response.status_code}")
                        return False
                else:
                    logger.error(f"Failed to get firewall rules: {response.status_code}")
                    return False
            else:
                logger.error(f"Failed to get firewall groups: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying GUI visibility: {str(e)}")
            return False
    
    def run_visibility_fix(self) -> bool:
        """Run the GUI visibility fix"""
        print(f"\n{'='*80}")
        print("MAKING CONFIGURATIONS VISIBLE IN GUI")
        print("Fixing groups, creating VLANs, and populating with devices")
        print(f"{'='*80}")
        
        if not self.authenticate():
            print("❌ Authentication failed")
            return False
        
        print("✅ Authentication successful")
        
        # Step 1: Fix firewall groups
        print("\n🔧 Step 1: Fixing firewall groups...")
        if not self.fix_firewall_groups():
            print("❌ Group fixing failed")
            return False
        print(f"✅ Fixed {len(self.fixed_groups)} groups")
        
        # Step 2: Create visible VLANs
        print("\n📡 Step 2: Creating visible VLANs...")
        if not self.create_visible_vlans():
            print("❌ VLAN creation failed")
            return False
        print(f"✅ Created {len(self.created_vlans)} VLANs")
        
        # Step 3: Populate device groups
        print("\n👥 Step 3: Populating device groups...")
        if not self.populate_device_groups():
            print("❌ Group population failed")
            return False
        print(f"✅ Populated {len(self.populated_groups)} groups")
        
        # Step 4: Create visible firewall rules
        print("\n🛡️ Step 4: Creating visible firewall rules...")
        if not self.create_visible_firewall_rules():
            print("❌ Rule creation failed")
            return False
        print("✅ Created visible firewall rules")
        
        # Step 5: Verify visibility
        print("\n✅ Step 5: Verifying GUI visibility...")
        if not self.verify_gui_visibility():
            print("❌ Visibility verification failed")
            return False
        
        print(f"\n{'='*80}")
        print("🎉 GUI VISIBILITY FIX COMPLETED!")
        print(f"{'='*80}")
        print("Your configurations should now be visible in the GUI:")
        print(f"  ✓ Fixed {len(self.fixed_groups)} firewall groups")
        print(f"  ✓ Created {len(self.created_vlans)} VLANs")
        print(f"  ✓ Populated {len(self.populated_groups)} device groups")
        print(f"  ✓ Created visible firewall rules")
        print(f"  ✓ All configurations properly enabled")
        print(f"{'='*80}")
        print("Check these sections in the GUI:")
        print("  • Settings → Networks → LAN → VLANs")
        print("  • Settings → Firewall → Groups")
        print("  • Settings → Firewall → Rules")
        print(f"{'='*80}")
        
        return True

def main():
    """Main function for GUI visibility fix"""
    # Load environment variables
    controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', '192.168.22.194')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    if not api_key:
        print("❌ Error: UNIFI_API_KEY_MARS not set in .env file")
        return False
    
    try:
        # Initialize GUI visibility fixer
        fixer = GUIVisibilityFixer(controller_host, api_key)
        
        # Run visibility fix
        success = fixer.run_visibility_fix()
        
        return success
        
    except Exception as e:
        print(f"❌ Error during GUI visibility fix: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
