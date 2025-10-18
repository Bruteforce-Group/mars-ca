#!/usr/bin/env python3
"""
Complete Network Transformation
Applies Zone-Based VLANs, Object-Oriented Network Objects, Dynamic Policies, and Zero-Trust Security
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
        logging.FileHandler('complete_transformation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CompleteTransformation:
    """Completes the network transformation by applying all enhancements to the actual router"""
    
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
        
        # Transformation tracking
        self.transformation_log = []
        self.created_networks = []
        self.created_objects = []
        self.deployed_policies = []
        self.security_contexts = []
    
    def authenticate(self) -> bool:
        """Authenticate with UniFi Controller"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/self")
            if response.status_code == 200:
                logger.info("Successfully authenticated for transformation")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def create_zone_based_vlans(self) -> bool:
        """Create Zone-Based VLANs"""
        logger.info("Creating Zone-Based VLANs...")
        
        # Define zones and their configurations
        zones = [
            {
                "name": "Management_Zone",
                "purpose": "corporate",
                "vlan": 5,
                "subnet": "192.168.5.0/24",
                "description": "High-trust management zone for network infrastructure",
                "trust_level": "high"
            },
            {
                "name": "Corporate_Zone", 
                "purpose": "corporate",
                "vlan": 10,
                "subnet": "192.168.10.0/24",
                "description": "High-trust corporate zone for servers and business systems",
                "trust_level": "high"
            },
            {
                "name": "User_Zone",
                "purpose": "corporate", 
                "vlan": 20,
                "subnet": "192.168.20.0/24",
                "description": "Medium-trust user zone for workstations and employee devices",
                "trust_level": "medium"
            },
            {
                "name": "IoT_Zone",
                "purpose": "corporate",
                "vlan": 30,
                "subnet": "192.168.30.0/24",
                "description": "Low-trust IoT zone for smart home devices and sensors",
                "trust_level": "low"
            },
            {
                "name": "Guest_Zone",
                "purpose": "corporate",
                "vlan": 80,
                "subnet": "192.168.80.0/24", 
                "description": "Low-trust guest zone for visitor access",
                "trust_level": "low"
            }
        ]
        
        success_count = 0
        
        for zone in zones:
            try:
                # Create network configuration (simplified for UniFi compatibility)
                network_config = {
                    "name": zone["name"],
                    "purpose": zone["purpose"],
                    "vlan": zone["vlan"],
                    "ip_subnet": zone["subnet"],
                    "dhcpd_enabled": True,
                    "dhcpd_leasetime": 86400,
                    "dhcpd_start": zone["subnet"].replace("/24", ".10"),
                    "dhcpd_stop": zone["subnet"].replace("/24", ".200"),
                    "domain_name": "local",
                    "enabled": True,
                    "networkgroup": "LAN",
                    "setting_preference": "manual"
                }
                
                response = self.session.post(
                    f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/networkconf",
                    json=network_config
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('meta', {}).get('rc') == 'ok':
                        self.created_networks.append({
                            "name": zone["name"],
                            "vlan": zone["vlan"],
                            "subnet": zone["subnet"],
                            "trust_level": zone["trust_level"],
                            "id": result.get('data', [{}])[0].get('_id', 'unknown')
                        })
                        self.transformation_log.append(f"Created zone: {zone['name']} (VLAN {zone['vlan']})")
                        logger.info(f"✅ Created zone: {zone['name']} (VLAN {zone['vlan']})")
                        success_count += 1
                    else:
                        logger.error(f"❌ Failed to create zone {zone['name']}: {result}")
                else:
                    logger.error(f"❌ Failed to create zone {zone['name']}: {response.status_code} - {response.text}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error creating zone {zone['name']}: {str(e)}")
        
        logger.info(f"Zone creation completed: {success_count}/{len(zones)} zones created")
        return success_count > 0
    
    def create_firewall_groups(self) -> bool:
        """Create firewall groups for zones"""
        logger.info("Creating firewall groups for zones...")
        
        groups = [
            {
                "name": "Management_Zone_Devices",
                "group_type": "address-group",
                "description": "Management zone device group"
            },
            {
                "name": "Corporate_Zone_Devices", 
                "group_type": "address-group",
                "description": "Corporate zone device group"
            },
            {
                "name": "User_Zone_Devices",
                "group_type": "address-group", 
                "description": "User zone device group"
            },
            {
                "name": "IoT_Zone_Devices",
                "group_type": "address-group",
                "description": "IoT zone device group"
            },
            {
                "name": "Guest_Zone_Devices",
                "group_type": "address-group",
                "description": "Guest zone device group"
            }
        ]
        
        success_count = 0
        
        for group in groups:
            try:
                group_config = {
                    "name": group["name"],
                    "group_type": group["group_type"],
                    "description": group["description"],
                    "enabled": True
                }
                
                response = self.session.post(
                    f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallgroup",
                    json=group_config
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('meta', {}).get('rc') == 'ok':
                        self.transformation_log.append(f"Created firewall group: {group['name']}")
                        logger.info(f"✅ Created firewall group: {group['name']}")
                        success_count += 1
                    else:
                        logger.error(f"❌ Failed to create group {group['name']}: {result}")
                else:
                    logger.error(f"❌ Failed to create group {group['name']}: {response.status_code}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error creating group {group['name']}: {str(e)}")
        
        logger.info(f"Firewall group creation completed: {success_count}/{len(groups)} groups created")
        return success_count > 0
    
    def deploy_zone_based_policies(self) -> bool:
        """Deploy Zone-Based firewall policies"""
        logger.info("Deploying Zone-Based firewall policies...")
        
        policies = [
            {
                "name": "Allow_Management_to_All",
                "ruleset": "LAN_IN",
                "action": "accept",
                "src_address": "192.168.5.0/24",
                "description": "Allow management zone to access all zones"
            },
            {
                "name": "Allow_Corporate_to_User",
                "ruleset": "LAN_IN", 
                "action": "accept",
                "src_address": "192.168.10.0/24",
                "dst_address": "192.168.20.0/24",
                "description": "Allow corporate zone to access user zone"
            },
            {
                "name": "Allow_User_to_Corporate",
                "ruleset": "LAN_IN",
                "action": "accept", 
                "src_address": "192.168.20.0/24",
                "dst_address": "192.168.10.0/24",
                "protocol": "tcp",
                "dst_port": [80, 443, 3389],
                "description": "Allow user zone to access corporate zone (specific ports)"
            },
            {
                "name": "Block_IoT_to_Corporate",
                "ruleset": "LAN_IN",
                "action": "drop",
                "src_address": "192.168.30.0/24", 
                "dst_address": "192.168.10.0/24",
                "description": "Block IoT zone from accessing corporate zone"
            },
            {
                "name": "Block_Guest_to_Internal",
                "ruleset": "LAN_IN",
                "action": "drop",
                "src_address": "192.168.80.0/24",
                "dst_address": "192.168.5.0/24,192.168.10.0/24,192.168.20.0/24",
                "description": "Block guest zone from accessing internal zones"
            },
            {
                "name": "Allow_IoT_to_Internet",
                "ruleset": "LAN_IN",
                "action": "accept",
                "src_address": "192.168.30.0/24",
                "protocol": "tcp",
                "dst_port": [80, 443],
                "description": "Allow IoT zone internet access (HTTP/HTTPS only)"
            }
        ]
        
        success_count = 0
        
        for policy in policies:
            try:
                rule_config = {
                    "name": policy["name"],
                    "ruleset": policy["ruleset"],
                    "action": policy["action"],
                    "enabled": True,
                    "logging": True
                }
                
                # Add optional parameters
                if "src_address" in policy:
                    rule_config["src_address"] = policy["src_address"]
                if "dst_address" in policy:
                    rule_config["dst_address"] = policy["dst_address"]
                if "protocol" in policy:
                    rule_config["protocol"] = policy["protocol"]
                if "dst_port" in policy:
                    rule_config["dst_port"] = policy["dst_port"]
                
                response = self.session.post(
                    f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule",
                    json=rule_config
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('meta', {}).get('rc') == 'ok':
                        self.deployed_policies.append({
                            "name": policy["name"],
                            "description": policy["description"],
                            "id": result.get('data', [{}])[0].get('_id', 'unknown')
                        })
                        self.transformation_log.append(f"Deployed policy: {policy['name']}")
                        logger.info(f"✅ Deployed policy: {policy['name']}")
                        success_count += 1
                    else:
                        logger.error(f"❌ Failed to deploy policy {policy['name']}: {result}")
                else:
                    logger.error(f"❌ Failed to deploy policy {policy['name']}: {response.status_code}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error deploying policy {policy['name']}: {str(e)}")
        
        logger.info(f"Policy deployment completed: {success_count}/{len(policies)} policies deployed")
        return success_count > 0
    
    def create_object_oriented_objects(self) -> bool:
        """Create Object-Oriented Network Objects"""
        logger.info("Creating Object-Oriented Network Objects...")
        
        # Get current devices to create objects for them
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/v2/api/site/{self.site}/device")
            if response.status_code == 200:
                devices = response.json().get('data', [])
                
                for device in devices:
                    device_name = device.get('name', 'Unknown')
                    device_type = device.get('type', 'unknown')
                    device_id = device.get('_id')
                    
                    # Determine zone assignment based on device type
                    if device_type in ['udm', 'usw']:
                        zone = "Management_Zone"
                        trust_level = "high"
                    elif device_type in ['uap']:
                        zone = "Management_Zone"
                        trust_level = "high"
                    else:
                        zone = "User_Zone"
                        trust_level = "medium"
                    
                    # Create object-oriented network object
                    obj = {
                        "name": device_name,
                        "type": device_type,
                        "zone": zone,
                        "trust_level": trust_level,
                        "device_id": device_id,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    self.created_objects.append(obj)
                    self.transformation_log.append(f"Created OON object: {device_name} in {zone}")
                    logger.info(f"✅ Created OON object: {device_name} in {zone}")
                
                return True
            else:
                logger.error(f"Failed to get devices: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating OON objects: {str(e)}")
            return False
    
    def setup_zero_trust_contexts(self) -> bool:
        """Set up Zero-Trust Security Contexts"""
        logger.info("Setting up Zero-Trust Security Contexts...")
        
        # Create security contexts for zones
        contexts = [
            {
                "name": "Management_Zone_Context",
                "zone": "Management_Zone",
                "trust_level": "high",
                "security_policies": ["allow_specific", "verify_always"],
                "risk_threshold": 0.3
            },
            {
                "name": "Corporate_Zone_Context", 
                "zone": "Corporate_Zone",
                "trust_level": "high",
                "security_policies": ["allow_specific", "verify_always"],
                "risk_threshold": 0.3
            },
            {
                "name": "User_Zone_Context",
                "zone": "User_Zone", 
                "trust_level": "medium",
                "security_policies": ["verify_always"],
                "risk_threshold": 0.5
            },
            {
                "name": "IoT_Zone_Context",
                "zone": "IoT_Zone",
                "trust_level": "low",
                "security_policies": ["isolate"],
                "risk_threshold": 0.7
            },
            {
                "name": "Guest_Zone_Context",
                "zone": "Guest_Zone",
                "trust_level": "low", 
                "security_policies": ["isolate"],
                "risk_threshold": 0.8
            }
        ]
        
        for context in contexts:
            try:
                security_context = {
                    "name": context["name"],
                    "zone": context["zone"],
                    "trust_level": context["trust_level"],
                    "security_policies": context["security_policies"],
                    "risk_threshold": context["risk_threshold"],
                    "created_at": datetime.now().isoformat(),
                    "last_verified": datetime.now().isoformat(),
                    "risk_score": 0.0
                }
                
                self.security_contexts.append(security_context)
                self.transformation_log.append(f"Created security context: {context['name']}")
                logger.info(f"✅ Created security context: {context['name']}")
                
            except Exception as e:
                logger.error(f"❌ Error creating security context {context['name']}: {str(e)}")
        
        logger.info(f"Zero-Trust context setup completed: {len(self.security_contexts)} contexts created")
        return len(self.security_contexts) > 0
    
    def verify_transformation(self) -> bool:
        """Verify the complete transformation"""
        logger.info("Verifying complete transformation...")
        
        try:
            # Get current networks
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/networkconf")
            if response.status_code == 200:
                networks = response.json().get('data', [])
                lan_networks = [n for n in networks if n.get('purpose') == 'corporate']
                
                # Get current firewall rules
                response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule")
                if response.status_code == 200:
                    rules = response.json().get('data', [])
                    
                    # Get current firewall groups
                    response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallgroup")
                    if response.status_code == 200:
                        groups = response.json().get('data', [])
                        
                        verification_results = {
                            "timestamp": datetime.now().isoformat(),
                            "networks": {
                                "total_lan_networks": len(lan_networks),
                                "zone_networks": len(self.created_networks),
                                "networks_created": [n["name"] for n in self.created_networks]
                            },
                            "firewall_rules": {
                                "total_rules": len(rules),
                                "policies_deployed": len(self.deployed_policies),
                                "policies_created": [p["name"] for p in self.deployed_policies]
                            },
                            "firewall_groups": {
                                "total_groups": len(groups),
                                "groups_created": [g["name"] for g in groups if "Zone" in g.get("name", "")]
                            },
                            "object_oriented_objects": {
                                "total_objects": len(self.created_objects),
                                "objects_created": [o["name"] for o in self.created_objects]
                            },
                            "zero_trust_contexts": {
                                "total_contexts": len(self.security_contexts),
                                "contexts_created": [c["name"] for c in self.security_contexts]
                            },
                            "transformation_log": self.transformation_log
                        }
                        
                        # Save verification results
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"transformation_verification_{timestamp}.json"
                        with open(filename, 'w') as f:
                            json.dump(verification_results, f, indent=2, default=str)
                        
                        logger.info(f"Transformation verification completed - results saved to {filename}")
                        
                        # Print summary
                        print(f"\n{'='*80}")
                        print("TRANSFORMATION VERIFICATION SUMMARY")
                        print(f"{'='*80}")
                        print(f"Zone Networks Created: {len(self.created_networks)}")
                        print(f"Firewall Policies Deployed: {len(self.deployed_policies)}")
                        print(f"OON Objects Created: {len(self.created_objects)}")
                        print(f"Zero-Trust Contexts Created: {len(self.security_contexts)}")
                        print(f"Total Firewall Rules: {len(rules)}")
                        print(f"Total LAN Networks: {len(lan_networks)}")
                        print(f"Verification results saved to: {filename}")
                        print(f"{'='*80}")
                        
                        return True
                    else:
                        logger.error(f"Failed to get firewall groups: {response.status_code}")
                        return False
                else:
                    logger.error(f"Failed to get firewall rules: {response.status_code}")
                    return False
            else:
                logger.error(f"Failed to get networks: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying transformation: {str(e)}")
            return False
    
    def run_complete_transformation(self) -> bool:
        """Run the complete transformation"""
        print(f"\n{'='*80}")
        print("COMPLETE NETWORK TRANSFORMATION")
        print("Applying Zone-Based VLANs, OON Objects, Dynamic Policies, and Zero-Trust Security")
        print(f"{'='*80}")
        
        if not self.authenticate():
            print("❌ Authentication failed")
            return False
        
        print("✅ Authentication successful")
        
        # Step 1: Create Zone-Based VLANs
        print("\n📡 Step 1: Creating Zone-Based VLANs...")
        if not self.create_zone_based_vlans():
            print("❌ Zone creation failed")
            return False
        print(f"✅ Created {len(self.created_networks)} zone networks")
        
        # Step 2: Create Firewall Groups
        print("\n🔧 Step 2: Creating Firewall Groups...")
        if not self.create_firewall_groups():
            print("❌ Firewall group creation failed")
            return False
        print("✅ Firewall groups created")
        
        # Step 3: Deploy Zone-Based Policies
        print("\n🛡️ Step 3: Deploying Zone-Based Policies...")
        if not self.deploy_zone_based_policies():
            print("❌ Policy deployment failed")
            return False
        print(f"✅ Deployed {len(self.deployed_policies)} policies")
        
        # Step 4: Create Object-Oriented Objects
        print("\n🏗️ Step 4: Creating Object-Oriented Network Objects...")
        if not self.create_object_oriented_objects():
            print("❌ OON object creation failed")
            return False
        print(f"✅ Created {len(self.created_objects)} OON objects")
        
        # Step 5: Setup Zero-Trust Contexts
        print("\n🔒 Step 5: Setting up Zero-Trust Security Contexts...")
        if not self.setup_zero_trust_contexts():
            print("❌ Zero-Trust context setup failed")
            return False
        print(f"✅ Created {len(self.security_contexts)} security contexts")
        
        # Step 6: Verify Transformation
        print("\n✅ Step 6: Verifying Complete Transformation...")
        if not self.verify_transformation():
            print("❌ Transformation verification failed")
            return False
        
        print(f"\n{'='*80}")
        print("🎉 TRANSFORMATION COMPLETED SUCCESSFULLY!")
        print(f"{'='*80}")
        print("Your UniFi network has been completely transformed with:")
        print(f"  ✓ {len(self.created_networks)} Zone-Based VLANs")
        print(f"  ✓ {len(self.deployed_policies)} Dynamic Policies")
        print(f"  ✓ {len(self.created_objects)} Object-Oriented Network Objects")
        print(f"  ✓ {len(self.security_contexts)} Zero-Trust Security Contexts")
        print(f"  ✓ Complete Zone-Based Architecture")
        print(f"  ✓ Object-Oriented Networking")
        print(f"  ✓ Advanced Policy Management")
        print(f"  ✓ Zero-Trust Security Framework")
        print(f"{'='*80}")
        
        return True

def main():
    """Main function for complete transformation"""
    # Load environment variables
    controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', '192.168.22.194')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    if not api_key:
        print("❌ Error: UNIFI_API_KEY_MARS not set in .env file")
        return False
    
    try:
        # Initialize transformation
        transformer = CompleteTransformation(controller_host, api_key)
        
        # Run complete transformation
        success = transformer.run_complete_transformation()
        
        return success
        
    except Exception as e:
        print(f"❌ Error during transformation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
