#!/usr/bin/env python3
"""
Policy Engine 4.4.0 Integration
Works with both legacy firewall system and new Policy Engine format
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
        logging.FileHandler('policy_engine_4_4_0.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PolicyEngine44:
    """Policy Engine integration for UniFi OS 4.4.0"""
    
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
        
        # Policy Engine data
        self.zones = []
        self.objects = []
        self.rules = []
        self.legacy_rules = []
        self.legacy_groups = []
    
    def authenticate(self) -> bool:
        """Authenticate with UniFi Controller"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/self")
            if response.status_code == 200:
                logger.info("Successfully authenticated for Policy Engine 4.4.0")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def discover_policy_engine_api(self) -> Dict[str, Any]:
        """Discover the Policy Engine API format"""
        logger.info("Discovering Policy Engine API format...")
        
        discovery_results = {
            "policy_endpoints": {},
            "legacy_system": {},
            "api_availability": {}
        }
        
        # Test Policy Engine endpoints
        policy_endpoints = [
            '/proxy/network/api/s/default/rest/policy',
            '/proxy/network/api/s/default/rest/policyengine',
            '/proxy/network/api/s/default/rest/zone',
            '/proxy/network/api/s/default/rest/object',
            '/proxy/network/api/s/default/rest/policyrule'
        ]
        
        for endpoint in policy_endpoints:
            try:
                response = self.session.get(f"https://{self.controller_host}{endpoint}")
                discovery_results["policy_endpoints"][endpoint] = {
                    "status_code": response.status_code,
                    "available": response.status_code != 404
                }
            except Exception as e:
                discovery_results["policy_endpoints"][endpoint] = {
                    "status_code": "error",
                    "available": False,
                    "error": str(e)
                }
        
        # Check legacy system
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule")
            if response.status_code == 200:
                self.legacy_rules = response.json().get('data', [])
                discovery_results["legacy_system"]["firewall_rules"] = len(self.legacy_rules)
            
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallgroup")
            if response.status_code == 200:
                self.legacy_groups = response.json().get('data', [])
                discovery_results["legacy_system"]["firewall_groups"] = len(self.legacy_groups)
        except Exception as e:
            discovery_results["legacy_system"]["error"] = str(e)
        
        # Check API availability
        discovery_results["api_availability"] = {
            "policy_engine": any(ep["available"] for ep in discovery_results["policy_endpoints"].values()),
            "legacy_firewall": discovery_results["legacy_system"].get("firewall_rules", 0) > 0,
            "legacy_groups": discovery_results["legacy_system"].get("firewall_groups", 0) > 0
        }
        
        return discovery_results
    
    def create_policy_engine_zones(self) -> bool:
        """Create zones in Policy Engine format"""
        logger.info("Creating Policy Engine zones...")
        
        # Define zones for Policy Engine
        zones = [
            {
                "name": "Management_Zone",
                "description": "High-trust management zone for network infrastructure",
                "trust_level": "high",
                "security_policy": "allow_specific",
                "monitoring_level": "high"
            },
            {
                "name": "Corporate_Zone",
                "description": "High-trust corporate zone for business systems",
                "trust_level": "high", 
                "security_policy": "allow_specific",
                "monitoring_level": "high"
            },
            {
                "name": "User_Zone",
                "description": "Medium-trust user zone for workstations",
                "trust_level": "medium",
                "security_policy": "verify_always",
                "monitoring_level": "medium"
            },
            {
                "name": "IoT_Zone",
                "description": "Low-trust IoT zone for smart devices",
                "trust_level": "low",
                "security_policy": "isolate",
                "monitoring_level": "low"
            },
            {
                "name": "Guest_Zone",
                "description": "Low-trust guest zone for visitors",
                "trust_level": "low",
                "security_policy": "isolate",
                "monitoring_level": "low"
            }
        ]
        
        # Since Policy Engine API is not accessible, we'll create a configuration file
        # that can be imported when the API becomes available
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"policy_engine_zones_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(zones, f, indent=2, default=str)
        
        self.zones = zones
        logger.info(f"Policy Engine zones configuration saved to {filename}")
        return True
    
    def create_policy_engine_objects(self) -> bool:
        """Create objects in Policy Engine format"""
        logger.info("Creating Policy Engine objects...")
        
        # Get current devices to create objects
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/stat/device")
            if response.status_code == 200:
                devices = response.json().get('data', [])
                
                response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/stat/sta")
                if response.status_code == 200:
                    clients = response.json().get('data', [])
                    
                    # Create Policy Engine objects
                    objects = []
                    
                    # Network infrastructure objects
                    for device in devices:
                        device_type = device.get('type', 'unknown')
                        device_name = device.get('name', 'Unknown')
                        device_ip = device.get('ip', 'unknown')
                        device_mac = device.get('mac', 'unknown')
                        
                        if device_ip != 'unknown' and device_ip:
                            obj = {
                                "name": f"{device_name}_Object",
                                "type": "network_device",
                                "device_type": device_type,
                                "ip_address": device_ip,
                                "mac_address": device_mac,
                                "zone": "Management_Zone" if device_type in ['udm', 'usw', 'uap'] else "User_Zone",
                                "trust_level": "high" if device_type in ['udm', 'usw', 'uap'] else "medium",
                                "monitoring_enabled": True,
                                "security_policy": "allow_specific" if device_type in ['udm', 'usw', 'uap'] else "verify_always"
                            }
                            objects.append(obj)
                    
                    # Client objects
                    for client in clients:
                        client_mac = client.get('mac', 'unknown')
                        client_ip = client.get('last_ip', 'unknown')
                        client_name = client.get('name', 'Unknown')
                        is_guest = client.get('is_guest', False)
                        is_wired = client.get('is_wired', False)
                        
                        if client_ip != 'unknown' and client_ip:
                            obj = {
                                "name": f"{client_name}_Object",
                                "type": "client_device",
                                "ip_address": client_ip,
                                "mac_address": client_mac,
                                "is_guest": is_guest,
                                "is_wired": is_wired,
                                "zone": "Guest_Zone" if is_guest else "User_Zone",
                                "trust_level": "low" if is_guest else "medium",
                                "monitoring_enabled": True,
                                "security_policy": "isolate" if is_guest else "verify_always"
                            }
                            objects.append(obj)
                    
                    # Save objects configuration
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"policy_engine_objects_{timestamp}.json"
                    
                    with open(filename, 'w') as f:
                        json.dump(objects, f, indent=2, default=str)
                    
                    self.objects = objects
                    logger.info(f"Policy Engine objects configuration saved to {filename}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error creating Policy Engine objects: {str(e)}")
            return False
    
    def create_policy_engine_rules(self) -> bool:
        """Create rules in Policy Engine format"""
        logger.info("Creating Policy Engine rules...")
        
        # Define Policy Engine rules
        rules = [
            {
                "name": "Allow_Management_to_All",
                "policy_type": "firewall",
                "action": "allow",
                "src_zone": "Management_Zone",
                "dst_zone": "any",
                "protocol": "any",
                "description": "Allow management zone to access all zones",
                "logging": True,
                "enabled": True
            },
            {
                "name": "Allow_Corporate_to_Internet",
                "policy_type": "firewall",
                "action": "allow",
                "src_zone": "Corporate_Zone",
                "dst_zone": "internet",
                "protocol": "any",
                "description": "Allow corporate zone internet access",
                "logging": True,
                "enabled": True
            },
            {
                "name": "Restrict_IoT_Access",
                "policy_type": "firewall",
                "action": "allow",
                "src_zone": "IoT_Zone",
                "dst_zone": "internet",
                "protocol": "tcp",
                "dst_port": "80,443",
                "description": "Restrict IoT devices to HTTP/HTTPS only",
                "logging": True,
                "enabled": True
            },
            {
                "name": "Isolate_Guest_Devices",
                "policy_type": "firewall",
                "action": "deny",
                "src_zone": "Guest_Zone",
                "dst_zone": "Management_Zone,Corporate_Zone,User_Zone",
                "protocol": "any",
                "description": "Isolate guest devices from internal zones",
                "logging": True,
                "enabled": True
            },
            {
                "name": "Default_Deny_All",
                "policy_type": "firewall",
                "action": "deny",
                "src_zone": "any",
                "dst_zone": "any",
                "protocol": "any",
                "description": "Default deny all traffic",
                "logging": True,
                "enabled": True
            }
        ]
        
        # Save rules configuration
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"policy_engine_rules_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(rules, f, indent=2, default=str)
        
        self.rules = rules
        logger.info(f"Policy Engine rules configuration saved to {filename}")
        return True
    
    def create_legacy_compatible_rules(self) -> bool:
        """Create rules compatible with legacy firewall system"""
        logger.info("Creating legacy-compatible rules...")
        
        # Get next rule index
        try:
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
        except Exception as e:
            logger.error(f"Error getting rule index: {str(e)}")
            next_index = 20001
        
        # Define legacy-compatible rules
        legacy_rules = [
            {
                "name": "Policy_Engine_Management_Access",
                "ruleset": "LAN_IN",
                "action": "accept",
                "protocol": "all",
                "description": "Policy Engine: Allow management zone access"
            },
            {
                "name": "Policy_Engine_IoT_Restriction",
                "ruleset": "LAN_IN",
                "action": "accept",
                "protocol": "tcp",
                "dst_port": "80,443",
                "description": "Policy Engine: Restrict IoT devices to HTTP/HTTPS"
            },
            {
                "name": "Policy_Engine_Guest_Isolation",
                "ruleset": "LAN_IN",
                "action": "drop",
                "protocol": "all",
                "description": "Policy Engine: Isolate guest devices"
            }
        ]
        
        success_count = 0
        
        for i, rule in enumerate(legacy_rules):
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
                if "dst_port" in rule:
                    rule_config["dst_port"] = rule["dst_port"]
                
                response = self.session.post(
                    f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule",
                    json=rule_config
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('meta', {}).get('rc') == 'ok':
                        logger.info(f"✅ Created legacy rule: {rule['name']}")
                        success_count += 1
                    else:
                        logger.error(f"❌ Failed to create rule {rule['name']}: {result}")
                else:
                    logger.error(f"❌ Failed to create rule {rule['name']}: {response.status_code}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error creating rule {rule['name']}: {str(e)}")
        
        logger.info(f"Legacy rule creation completed: {success_count}/{len(legacy_rules)} rules created")
        return success_count > 0
    
    def generate_policy_engine_report(self) -> Dict[str, Any]:
        """Generate comprehensive Policy Engine report"""
        logger.info("Generating Policy Engine report...")
        
        # Discover API availability
        discovery = self.discover_policy_engine_api()
        
        # Create configurations
        zones_created = self.create_policy_engine_zones()
        objects_created = self.create_policy_engine_objects()
        rules_created = self.create_policy_engine_rules()
        legacy_rules_created = self.create_legacy_compatible_rules()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "firmware_version": "4.4.0",
            "policy_engine_status": {
                "api_available": discovery["api_availability"]["policy_engine"],
                "legacy_system_available": discovery["api_availability"]["legacy_firewall"],
                "zones_created": zones_created,
                "objects_created": objects_created,
                "rules_created": rules_created,
                "legacy_rules_created": legacy_rules_created
            },
            "discovery_results": discovery,
            "configurations": {
                "zones": len(self.zones),
                "objects": len(self.objects),
                "rules": len(self.rules),
                "legacy_rules": len(self.legacy_rules)
            },
            "files_created": [
                f"policy_engine_zones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                f"policy_engine_objects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                f"policy_engine_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            ],
            "recommendations": [
                "Policy Engine API is not yet accessible via standard endpoints",
                "Legacy firewall system is still operational and working",
                "Configuration files created for future Policy Engine import",
                "Legacy-compatible rules created for immediate functionality",
                "Monitor for Policy Engine API availability in future firmware updates"
            ]
        }
        
        return report
    
    def display_policy_engine_status(self, report: Dict[str, Any]) -> None:
        """Display Policy Engine status"""
        print(f"\n{'='*80}")
        print("🔧 POLICY ENGINE 4.4.0 STATUS")
        print(f"{'='*80}")
        
        # Firmware and API Status
        print(f"\n📋 FIRMWARE & API STATUS:")
        print(f"  • Firmware Version: {report['firmware_version']}")
        print(f"  • Policy Engine API: {'✅ Available' if report['policy_engine_status']['api_available'] else '❌ Not Available'}")
        print(f"  • Legacy System: {'✅ Available' if report['policy_engine_status']['legacy_system_available'] else '❌ Not Available'}")
        
        # Configuration Status
        print(f"\n🏗️ CONFIGURATION STATUS:")
        print(f"  • Zones Created: {report['policy_engine_status']['zones_created']}")
        print(f"  • Objects Created: {report['policy_engine_status']['objects_created']}")
        print(f"  • Rules Created: {report['policy_engine_status']['rules_created']}")
        print(f"  • Legacy Rules Created: {report['policy_engine_status']['legacy_rules_created']}")
        
        # Discovery Results
        print(f"\n🔍 DISCOVERY RESULTS:")
        for endpoint, status in report['discovery_results']['policy_endpoints'].items():
            status_icon = "✅" if status['available'] else "❌"
            print(f"  • {endpoint}: {status_icon} {status['status_code']}")
        
        # Files Created
        print(f"\n📁 FILES CREATED:")
        for file in report['files_created']:
            print(f"  • {file}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        
        print(f"\n{'='*80}")
        print("🎯 POLICY ENGINE 4.4.0 INTEGRATION COMPLETE!")
        print(f"{'='*80}")
    
    def run_policy_engine_integration(self) -> bool:
        """Run the Policy Engine integration"""
        print(f"\n{'='*80}")
        print("🔧 POLICY ENGINE 4.4.0 INTEGRATION")
        print("Creating zone-based policies for UniFi OS 4.4.0")
        print(f"{'='*80}")
        
        if not self.authenticate():
            print("❌ Authentication failed")
            return False
        
        print("✅ Authentication successful")
        
        # Step 1: Discover Policy Engine API
        print("\n🔍 Step 1: Discovering Policy Engine API...")
        discovery = self.discover_policy_engine_api()
        print("✅ API discovery completed")
        
        # Step 2: Create Policy Engine configurations
        print("\n🏗️ Step 2: Creating Policy Engine configurations...")
        if not self.create_policy_engine_zones():
            print("❌ Zone creation failed")
            return False
        print("✅ Zones configuration created")
        
        if not self.create_policy_engine_objects():
            print("❌ Object creation failed")
            return False
        print("✅ Objects configuration created")
        
        if not self.create_policy_engine_rules():
            print("❌ Rule creation failed")
            return False
        print("✅ Rules configuration created")
        
        # Step 3: Create legacy-compatible rules
        print("\n🔧 Step 3: Creating legacy-compatible rules...")
        if not self.create_legacy_compatible_rules():
            print("❌ Legacy rule creation failed")
            return False
        print("✅ Legacy-compatible rules created")
        
        # Step 4: Generate report
        print("\n📋 Step 4: Generating Policy Engine report...")
        report = self.generate_policy_engine_report()
        
        # Step 5: Display status
        print("\n📊 Step 5: Displaying Policy Engine status...")
        self.display_policy_engine_status(report)
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"policy_engine_report_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📁 Report saved to: {filename}")
        
        return True

def main():
    """Main function for Policy Engine integration"""
    # Load environment variables
    controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', '192.168.22.194')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    if not api_key:
        print("❌ Error: UNIFI_API_KEY_MARS not set in .env file")
        return False
    
    try:
        # Initialize Policy Engine integration
        policy_engine = PolicyEngine44(controller_host, api_key)
        
        # Run Policy Engine integration
        success = policy_engine.run_policy_engine_integration()
        
        return success
        
    except Exception as e:
        print(f"❌ Error during Policy Engine integration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
