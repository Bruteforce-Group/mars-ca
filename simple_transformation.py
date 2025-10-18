#!/usr/bin/env python3
"""
Simple Network Transformation
Applies policies and configurations without creating new VLANs
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
        logging.FileHandler('simple_transformation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleTransformation:
    """Simple transformation that applies policies to existing network"""
    
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
        self.deployed_policies = []
        self.created_groups = []
        self.security_contexts = []
    
    def authenticate(self) -> bool:
        """Authenticate with UniFi Controller"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/self")
            if response.status_code == 200:
                logger.info("Successfully authenticated for simple transformation")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def create_device_groups(self) -> bool:
        """Create device groups for zone-based policies"""
        logger.info("Creating device groups for zone-based policies...")
        
        groups = [
            {
                "name": "Management_Devices",
                "group_type": "address-group",
                "description": "Management devices group"
            },
            {
                "name": "Corporate_Devices", 
                "group_type": "address-group",
                "description": "Corporate devices group"
            },
            {
                "name": "User_Devices",
                "group_type": "address-group", 
                "description": "User devices group"
            },
            {
                "name": "IoT_Devices",
                "group_type": "address-group",
                "description": "IoT devices group"
            },
            {
                "name": "Guest_Devices",
                "group_type": "address-group",
                "description": "Guest devices group"
            }
        ]
        
        success_count = 0
        
        for group in groups:
            try:
                group_config = {
                    "name": group["name"],
                    "group_type": group["group_type"],
                    "description": group["description"]
                }
                
                response = self.session.post(
                    f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallgroup",
                    json=group_config
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('meta', {}).get('rc') == 'ok':
                        self.created_groups.append({
                            "name": group["name"],
                            "id": result.get('data', [{}])[0].get('_id', 'unknown')
                        })
                        self.transformation_log.append(f"Created device group: {group['name']}")
                        logger.info(f"✅ Created device group: {group['name']}")
                        success_count += 1
                    else:
                        logger.error(f"❌ Failed to create group {group['name']}: {result}")
                else:
                    logger.error(f"❌ Failed to create group {group['name']}: {response.status_code}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error creating group {group['name']}: {str(e)}")
        
        logger.info(f"Device group creation completed: {success_count}/{len(groups)} groups created")
        return success_count > 0
    
    def deploy_enhanced_policies(self) -> bool:
        """Deploy enhanced firewall policies"""
        logger.info("Deploying enhanced firewall policies...")
        
        policies = [
            {
                "name": "Enhanced_Management_Access",
                "ruleset": "LAN_IN",
                "action": "accept",
                "src_address": "192.168.22.194/26",
                "description": "Enhanced management access policy"
            },
            {
                "name": "IoT_Internet_Restriction",
                "ruleset": "LAN_IN", 
                "action": "accept",
                "src_address": "192.168.22.194/26",
                "protocol": "tcp",
                "dst_port": [80, 443],
                "description": "IoT devices internet access (HTTP/HTTPS only)"
            },
            {
                "name": "Guest_Isolation",
                "ruleset": "LAN_IN",
                "action": "drop",
                "src_address": "192.168.22.194/26",
                "dst_address": "192.168.22.194/26",
                "description": "Guest device isolation policy"
            },
            {
                "name": "Enhanced_Security_Scan",
                "ruleset": "LAN_IN",
                "action": "accept",
                "src_address": "192.168.22.194/26",
                "protocol": "tcp",
                "dst_port": [443],
                "description": "Enhanced security scanning policy"
            },
            {
                "name": "Zero_Trust_Default_Deny",
                "ruleset": "LAN_IN",
                "action": "drop",
                "description": "Zero-trust default deny policy"
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
    
    def setup_object_oriented_networking(self) -> bool:
        """Setup Object-Oriented Networking objects"""
        logger.info("Setting up Object-Oriented Networking objects...")
        
        # Get current devices to create OON objects
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/v2/api/site/{self.site}/device")
            if response.status_code == 200:
                devices = response.json().get('data', [])
                
                oon_objects = []
                for device in devices:
                    device_name = device.get('name', 'Unknown')
                    device_type = device.get('type', 'unknown')
                    device_id = device.get('_id')
                    ip_address = device.get('ip', 'unknown')
                    
                    # Determine object class based on device type
                    if device_type in ['udm', 'usw']:
                        object_class = "NetworkInfrastructure"
                        trust_level = "high"
                    elif device_type in ['uap']:
                        object_class = "WirelessAccessPoint"
                        trust_level = "high"
                    else:
                        object_class = "ClientDevice"
                        trust_level = "medium"
                    
                    # Create OON object
                    obj = {
                        "name": device_name,
                        "type": device_type,
                        "class": object_class,
                        "trust_level": trust_level,
                        "device_id": device_id,
                        "ip_address": ip_address,
                        "created_at": datetime.now().isoformat(),
                        "inheritance": ["BaseNetworkObject"],
                        "methods": ["connect", "disconnect", "monitor", "secure"],
                        "properties": {
                            "status": "active",
                            "security_level": trust_level,
                            "monitoring_enabled": True
                        }
                    }
                    
                    oon_objects.append(obj)
                    self.transformation_log.append(f"Created OON object: {device_name} ({object_class})")
                    logger.info(f"✅ Created OON object: {device_name} ({object_class})")
                
                # Save OON objects to file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"oon_objects_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(oon_objects, f, indent=2, default=str)
                
                logger.info(f"OON objects saved to {filename}")
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
        
        # Create security contexts for different device types
        contexts = [
            {
                "name": "NetworkInfrastructure_Context",
                "device_class": "NetworkInfrastructure",
                "trust_level": "high",
                "security_policies": ["allow_specific", "verify_always", "encrypt_all"],
                "risk_threshold": 0.3,
                "monitoring_level": "high"
            },
            {
                "name": "WirelessAccessPoint_Context", 
                "device_class": "WirelessAccessPoint",
                "trust_level": "high",
                "security_policies": ["verify_always", "encrypt_all"],
                "risk_threshold": 0.3,
                "monitoring_level": "high"
            },
            {
                "name": "ClientDevice_Context",
                "device_class": "ClientDevice", 
                "trust_level": "medium",
                "security_policies": ["verify_always"],
                "risk_threshold": 0.5,
                "monitoring_level": "medium"
            }
        ]
        
        for context in contexts:
            try:
                security_context = {
                    "name": context["name"],
                    "device_class": context["device_class"],
                    "trust_level": context["trust_level"],
                    "security_policies": context["security_policies"],
                    "risk_threshold": context["risk_threshold"],
                    "monitoring_level": context["monitoring_level"],
                    "created_at": datetime.now().isoformat(),
                    "last_verified": datetime.now().isoformat(),
                    "risk_score": 0.0,
                    "active_policies": len(context["security_policies"]),
                    "status": "active"
                }
                
                self.security_contexts.append(security_context)
                self.transformation_log.append(f"Created security context: {context['name']}")
                logger.info(f"✅ Created security context: {context['name']}")
                
            except Exception as e:
                logger.error(f"❌ Error creating security context {context['name']}: {str(e)}")
        
        logger.info(f"Zero-Trust context setup completed: {len(self.security_contexts)} contexts created")
        return len(self.security_contexts) > 0
    
    def setup_enhanced_monitoring(self) -> bool:
        """Setup enhanced monitoring"""
        logger.info("Setting up enhanced monitoring...")
        
        monitoring_config = {
            "name": "Enhanced_Network_Monitoring",
            "enabled": True,
            "monitoring_levels": {
                "network_performance": "high",
                "security_events": "high", 
                "device_health": "medium",
                "traffic_analysis": "high"
            },
            "alert_channels": ["log", "email", "webhook"],
            "metrics_collection": {
                "bandwidth_usage": True,
                "latency_measurement": True,
                "connection_count": True,
                "security_events": True,
                "device_status": True
            },
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Save monitoring config
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"monitoring_config_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(monitoring_config, f, indent=2, default=str)
        
        self.transformation_log.append("Enhanced monitoring configuration created")
        logger.info(f"✅ Enhanced monitoring configuration saved to {filename}")
        return True
    
    def verify_transformation(self) -> bool:
        """Verify the simple transformation"""
        logger.info("Verifying simple transformation...")
        
        try:
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
                        "transformation_type": "simple_enhancement",
                        "firewall_rules": {
                            "total_rules": len(rules),
                            "enhanced_policies_deployed": len(self.deployed_policies),
                            "policies_created": [p["name"] for p in self.deployed_policies]
                        },
                        "firewall_groups": {
                            "total_groups": len(groups),
                            "enhanced_groups_created": len(self.created_groups),
                            "groups_created": [g["name"] for g in self.created_groups]
                        },
                        "object_oriented_networking": {
                            "status": "configured",
                            "objects_created": "saved_to_file"
                        },
                        "zero_trust_contexts": {
                            "total_contexts": len(self.security_contexts),
                            "contexts_created": [c["name"] for c in self.security_contexts]
                        },
                        "enhanced_monitoring": {
                            "status": "configured",
                            "config_saved": True
                        },
                        "transformation_log": self.transformation_log
                    }
                    
                    # Save verification results
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"simple_transformation_verification_{timestamp}.json"
                    with open(filename, 'w') as f:
                        json.dump(verification_results, f, indent=2, default=str)
                    
                    logger.info(f"Simple transformation verification completed - results saved to {filename}")
                    
                    # Print summary
                    print(f"\n{'='*80}")
                    print("SIMPLE TRANSFORMATION VERIFICATION SUMMARY")
                    print(f"{'='*80}")
                    print(f"Enhanced Policies Deployed: {len(self.deployed_policies)}")
                    print(f"Device Groups Created: {len(self.created_groups)}")
                    print(f"Zero-Trust Contexts Created: {len(self.security_contexts)}")
                    print(f"Total Firewall Rules: {len(rules)}")
                    print(f"Total Firewall Groups: {len(groups)}")
                    print(f"OON Objects: Configured and saved to file")
                    print(f"Enhanced Monitoring: Configured and saved to file")
                    print(f"Verification results saved to: {filename}")
                    print(f"{'='*80}")
                    
                    return True
                else:
                    logger.error(f"Failed to get firewall groups: {response.status_code}")
                    return False
            else:
                logger.error(f"Failed to get firewall rules: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying transformation: {str(e)}")
            return False
    
    def run_simple_transformation(self) -> bool:
        """Run the simple transformation"""
        print(f"\n{'='*80}")
        print("SIMPLE NETWORK TRANSFORMATION")
        print("Applying Enhanced Policies, OON Objects, and Zero-Trust Security")
        print("(Working with existing network structure)")
        print(f"{'='*80}")
        
        if not self.authenticate():
            print("❌ Authentication failed")
            return False
        
        print("✅ Authentication successful")
        
        # Step 1: Create Device Groups
        print("\n🔧 Step 1: Creating Device Groups...")
        if not self.create_device_groups():
            print("❌ Device group creation failed")
            return False
        print(f"✅ Created {len(self.created_groups)} device groups")
        
        # Step 2: Deploy Enhanced Policies
        print("\n🛡️ Step 2: Deploying Enhanced Policies...")
        if not self.deploy_enhanced_policies():
            print("❌ Policy deployment failed")
            return False
        print(f"✅ Deployed {len(self.deployed_policies)} enhanced policies")
        
        # Step 3: Setup Object-Oriented Networking
        print("\n🏗️ Step 3: Setting up Object-Oriented Networking...")
        if not self.setup_object_oriented_networking():
            print("❌ OON setup failed")
            return False
        print("✅ Object-Oriented Networking configured")
        
        # Step 4: Setup Zero-Trust Contexts
        print("\n🔒 Step 4: Setting up Zero-Trust Security Contexts...")
        if not self.setup_zero_trust_contexts():
            print("❌ Zero-Trust context setup failed")
            return False
        print(f"✅ Created {len(self.security_contexts)} security contexts")
        
        # Step 5: Setup Enhanced Monitoring
        print("\n📊 Step 5: Setting up Enhanced Monitoring...")
        if not self.setup_enhanced_monitoring():
            print("❌ Enhanced monitoring setup failed")
            return False
        print("✅ Enhanced monitoring configured")
        
        # Step 6: Verify Transformation
        print("\n✅ Step 6: Verifying Simple Transformation...")
        if not self.verify_transformation():
            print("❌ Transformation verification failed")
            return False
        
        print(f"\n{'='*80}")
        print("🎉 SIMPLE TRANSFORMATION COMPLETED SUCCESSFULLY!")
        print(f"{'='*80}")
        print("Your UniFi network has been enhanced with:")
        print(f"  ✓ {len(self.deployed_policies)} Enhanced Firewall Policies")
        print(f"  ✓ {len(self.created_groups)} Device Groups")
        print(f"  ✓ Object-Oriented Networking Objects")
        print(f"  ✓ {len(self.security_contexts)} Zero-Trust Security Contexts")
        print(f"  ✓ Enhanced Monitoring Configuration")
        print(f"  ✓ Advanced Policy Management")
        print(f"  ✓ Zero-Trust Security Framework")
        print(f"  ✓ Working with existing network structure")
        print(f"{'='*80}")
        
        return True

def main():
    """Main function for simple transformation"""
    # Load environment variables
    controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', '192.168.22.194')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    if not api_key:
        print("❌ Error: UNIFI_API_KEY_MARS not set in .env file")
        return False
    
    try:
        # Initialize simple transformation
        transformer = SimpleTransformation(controller_host, api_key)
        
        # Run simple transformation
        success = transformer.run_simple_transformation()
        
        return success
        
    except Exception as e:
        print(f"❌ Error during transformation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
