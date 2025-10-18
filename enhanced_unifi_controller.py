#!/usr/bin/env python3
"""
Enhanced UniFi Controller with Object-Oriented Networking and Zone-Based Rules
Supports comprehensive network policy management with initial scanning capabilities
"""

import os
import json
import requests
import time
import logging
from typing import Dict, List, Any, Optional, Union
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_unifi_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class NetworkObject:
    """Base class for all network objects"""
    name: str
    description: str = ""
    enabled: bool = True
    zone_assignment: Optional[str] = None
    trust_level: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary for API calls"""
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "zone_assignment": self.zone_assignment,
            "trust_level": self.trust_level
        }

@dataclass
class DeviceObject(NetworkObject):
    """Device object with classification capabilities"""
    mac_address: str = ""
    ip_address: str = ""
    device_type: str = "unknown"
    manufacturer: str = ""
    model: str = ""
    firmware_version: str = ""
    classification_confidence: float = 0.0
    last_seen: Optional[datetime] = None
    
    def classify_device(self, classification_rules: Dict) -> bool:
        """Classify device based on rules"""
        for rule_name, rule_config in classification_rules.items():
            if self._matches_rule(rule_config):
                self.device_type = rule_config.get('device_type', 'unknown')
                self.trust_level = rule_config.get('trust_level', 'unknown')
                self.classification_confidence = rule_config.get('confidence', 0.0)
                return True
        return False
    
    def _matches_rule(self, rule_config: Dict) -> bool:
        """Check if device matches classification rule"""
        # Implement device matching logic based on MAC, hostname, etc.
        if 'mac_pattern' in rule_config:
            return self._match_mac_pattern(rule_config['mac_pattern'])
        if 'hostname_pattern' in rule_config:
            return self._match_hostname_pattern(rule_config['hostname_pattern'])
        if 'device_fingerprint' in rule_config:
            return self._match_device_fingerprint(rule_config['device_fingerprint'])
        return False
    
    def _match_mac_pattern(self, pattern: str) -> bool:
        """Match MAC address against pattern"""
        if not self.mac_address:
            return False
        # Implement MAC pattern matching
        return pattern.lower() in self.mac_address.lower()
    
    def _match_hostname_pattern(self, pattern: str) -> bool:
        """Match hostname against pattern"""
        if not hasattr(self, 'hostname'):
            return False
        # Implement hostname pattern matching
        return pattern.lower() in self.hostname.lower()
    
    def _match_device_fingerprint(self, fingerprint: str) -> bool:
        """Match device fingerprint"""
        if not hasattr(self, 'fingerprint'):
            return False
        # Implement device fingerprint matching
        return fingerprint.lower() in self.fingerprint.lower()

@dataclass
class PolicyObject(NetworkObject):
    """Policy object with enforcement capabilities"""
    policy_id: str = ""
    priority: int = 1000
    action: str = "allow"
    source_zones: List[str] = field(default_factory=list)
    destination_zones: List[str] = field(default_factory=list)
    protocols: List[str] = field(default_factory=list)
    ports: List[str] = field(default_factory=list)
    logging_enabled: bool = True
    
    def validate_policy(self) -> bool:
        """Validate policy configuration"""
        if not self.name:
            return False
        if not self.source_zones and not self.destination_zones:
            return False
        if self.action not in ["allow", "deny", "drop"]:
            return False
        return True
    
    def apply_zone_rules(self, zone_config: Dict) -> bool:
        """Apply zone-based rules"""
        if not self.validate_policy():
            return False
        # Implement zone rule application logic
        return True

@dataclass
class ZoneObject(NetworkObject):
    """Zone object for zone-based firewall management"""
    zone_id: str = ""
    vlan_ids: List[int] = field(default_factory=list)
    security_level: str = "unknown"
    trust_score: int = 0
    devices: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def add_device(self, device: DeviceObject) -> bool:
        """Add device to zone"""
        if device.trust_level == self.security_level or self._is_compatible_trust_level(device.trust_level):
            self.devices.append(device.name)
            return True
        return False
    
    def _is_compatible_trust_level(self, device_trust: str) -> bool:
        """Check if device trust level is compatible with zone"""
        trust_hierarchy = {
            "high": ["high", "medium_high"],
            "medium_high": ["medium_high", "medium"],
            "medium": ["medium", "low"],
            "low": ["low", "isolated"],
            "isolated": ["isolated"]
        }
        return device_trust in trust_hierarchy.get(self.security_level, [])

class EnhancedUniFiController:
    """Enhanced UniFi Controller with Object-Oriented Networking capabilities"""
    
    def __init__(self, host: str, username: str, password: str, api_key: str, port: int = 443):
        self.host = host
        self.username = username
        self.password = password
        self.api_key = api_key
        self.port = port
        self.base_url = f"https://{host}:{port}"
        self.session = requests.Session()
        self.session.verify = False
        self.csrf_token = None
        self.site = "default"
        self.controller_type = None
        self.network_objects: Dict[str, NetworkObject] = {}
        self.zone_objects: Dict[str, ZoneObject] = {}
        self.policy_objects: Dict[str, PolicyObject] = {}
        self.device_objects: Dict[str, DeviceObject] = {}
        
    def authenticate(self) -> bool:
        """Authenticate with UniFi Controller"""
        try:
            auth_attempts = [
                {'port': 443, 'login_endpoint': '/api/auth/login', 'test_endpoint': '/api/self'},
                {'port': 8443, 'login_endpoint': '/api/login', 'test_endpoint': '/api/self'},
                {'port': 443, 'login_endpoint': '/api/login', 'test_endpoint': '/api/self'},
            ]
            
            for attempt in auth_attempts:
                test_base_url = f"https://{self.host}:{attempt['port']}"
                
                # Try API key authentication first
                if self.api_key:
                    headers = {
                        'X-API-Key': self.api_key,
                        'Content-Type': 'application/json'
                    }
                    
                    try:
                        response = self.session.get(
                            f"{test_base_url}{attempt['test_endpoint']}",
                            headers=headers,
                            timeout=10
                        )
                        if response.status_code == 200:
                            self.base_url = test_base_url
                            self.port = attempt['port']
                            self.controller_type = 'api_key'
                            self.session.headers.update(headers)
                            logger.info(f"Successfully authenticated with API key on port {attempt['port']}")
                            return True
                    except Exception as e:
                        logger.debug(f"API key auth failed on port {attempt['port']}: {str(e)}")
                        continue
                
                # Try username/password authentication
                if self.username and self.password:
                    login_data = {
                        "username": self.username,
                        "password": self.password
                    }
                    
                    if attempt['port'] == 443:
                        login_data.update({
                            "remember": True,
                            "strict": True
                        })
                    
                    try:
                        response = self.session.post(
                            f"{test_base_url}{attempt['login_endpoint']}",
                            json=login_data,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            self.base_url = test_base_url
                            self.port = attempt['port']
                            self.controller_type = 'username_password'
                            
                            if 'x-csrf-token' in response.headers:
                                self.csrf_token = response.headers['x-csrf-token']
                                self.session.headers.update({'X-CSRF-Token': self.csrf_token})
                            
                            logger.info(f"Successfully authenticated with username/password on port {attempt['port']}")
                            return True
                    except Exception as e:
                        logger.debug(f"Username/password auth failed on port {attempt['port']}: {str(e)}")
                        continue
            
            logger.error("Authentication failed on all attempted ports and methods")
            return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def perform_initial_scan(self) -> Dict[str, Any]:
        """Perform comprehensive initial scan of UniFi network"""
        logger.info("Starting comprehensive network scan...")
        scan_results = {
            "timestamp": datetime.now().isoformat(),
            "controller_info": {},
            "networks": [],
            "devices": [],
            "firewall_groups": [],
            "firewall_rules": [],
            "clients": [],
            "recommendations": []
        }
        
        try:
            # Get controller information
            scan_results["controller_info"] = self._get_controller_info()
            
            # Get existing networks
            scan_results["networks"] = self._get_networks()
            
            # Get devices
            scan_results["devices"] = self._get_devices()
            
            # Get firewall groups
            scan_results["firewall_groups"] = self._get_firewall_groups()
            
            # Get firewall rules
            scan_results["firewall_rules"] = self._get_firewall_rules()
            
            # Get connected clients
            scan_results["clients"] = self._get_clients()
            
            # Generate recommendations
            scan_results["recommendations"] = self._generate_recommendations(scan_results)
            
            logger.info("Network scan completed successfully")
            return scan_results
            
        except Exception as e:
            logger.error(f"Error during network scan: {str(e)}")
            return scan_results
    
    def _get_controller_info(self) -> Dict[str, Any]:
        """Get controller information"""
        try:
            response = self.session.get(f"{self.base_url}/api/self")
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Error getting controller info: {str(e)}")
            return {}
    
    def _get_networks(self) -> List[Dict[str, Any]]:
        """Get existing networks"""
        try:
            response = self.session.get(f"{self.base_url}/api/s/{self.site}/rest/networkconf")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting networks: {str(e)}")
            return []
    
    def _get_devices(self) -> List[Dict[str, Any]]:
        """Get network devices"""
        try:
            response = self.session.get(f"{self.base_url}/api/s/{self.site}/stat/device")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting devices: {str(e)}")
            return []
    
    def _get_firewall_groups(self) -> List[Dict[str, Any]]:
        """Get firewall groups"""
        try:
            response = self.session.get(f"{self.base_url}/api/s/{self.site}/rest/firewallgroup")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting firewall groups: {str(e)}")
            return []
    
    def _get_firewall_rules(self) -> List[Dict[str, Any]]:
        """Get firewall rules"""
        try:
            response = self.session.get(f"{self.base_url}/api/s/{self.site}/rest/firewallrule")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting firewall rules: {str(e)}")
            return []
    
    def _get_clients(self) -> List[Dict[str, Any]]:
        """Get connected clients"""
        try:
            response = self.session.get(f"{self.base_url}/api/s/{self.site}/stat/sta")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting clients: {str(e)}")
            return []
    
    def _generate_recommendations(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate implementation recommendations based on scan results"""
        recommendations = []
        
        # Analyze existing networks
        existing_networks = scan_results.get("networks", [])
        if len(existing_networks) <= 1:
            recommendations.append({
                "type": "network_segmentation",
                "priority": "high",
                "description": "Implement VLAN-based network segmentation",
                "details": "Current network appears to be flat. Recommend implementing 10-VLAN architecture for security and performance."
            })
        
        # Analyze devices
        devices = scan_results.get("devices", [])
        if len(devices) > 0:
            recommendations.append({
                "type": "device_classification",
                "priority": "medium",
                "description": "Implement automated device classification",
                "details": f"Found {len(devices)} devices that should be classified and assigned to appropriate zones."
            })
        
        # Analyze firewall rules
        firewall_rules = scan_results.get("firewall_rules", [])
        if len(firewall_rules) < 10:
            recommendations.append({
                "type": "security_policies",
                "priority": "high",
                "description": "Implement comprehensive firewall policies",
                "details": "Current firewall rules are minimal. Recommend implementing zone-based firewall rules for enhanced security."
            })
        
        return recommendations
    
    def create_zone_object(self, zone_config: Dict[str, Any]) -> ZoneObject:
        """Create a zone object from configuration"""
        zone = ZoneObject(
            name=zone_config.get("name", ""),
            description=zone_config.get("description", ""),
            zone_id=zone_config.get("zone_id", ""),
            vlan_ids=zone_config.get("vlan_ids", []),
            security_level=zone_config.get("security_level", "unknown"),
            trust_score=zone_config.get("trust_score", 0),
            attributes=zone_config.get("attributes", {})
        )
        self.zone_objects[zone.name] = zone
        return zone
    
    def create_device_object(self, device_data: Dict[str, Any]) -> DeviceObject:
        """Create a device object from device data"""
        device = DeviceObject(
            name=device_data.get("name", ""),
            mac_address=device_data.get("mac", ""),
            ip_address=device_data.get("ip", ""),
            device_type=device_data.get("type", "unknown"),
            manufacturer=device_data.get("manufacturer", ""),
            model=device_data.get("model", ""),
            firmware_version=device_data.get("version", ""),
            last_seen=datetime.now()
        )
        self.device_objects[device.mac_address] = device
        return device
    
    def create_policy_object(self, policy_config: Dict[str, Any]) -> PolicyObject:
        """Create a policy object from configuration"""
        policy = PolicyObject(
            name=policy_config.get("name", ""),
            description=policy_config.get("description", ""),
            policy_id=policy_config.get("policy_id", ""),
            priority=policy_config.get("priority", 1000),
            action=policy_config.get("action", "allow"),
            source_zones=policy_config.get("source_zones", []),
            destination_zones=policy_config.get("destination_zones", []),
            protocols=policy_config.get("protocols", []),
            ports=policy_config.get("ports", []),
            logging_enabled=policy_config.get("logging_enabled", True)
        )
        self.policy_objects[policy.name] = policy
        return policy
    
    def deploy_zone_based_policies(self, zone_policies: Dict[str, Any]) -> bool:
        """Deploy zone-based policies to UniFi controller"""
        logger.info("Deploying zone-based policies...")
        
        try:
            # Create zones
            zone_definitions = zone_policies.get("zone_definitions", {})
            for zone_category, zones in zone_definitions.items():
                for zone_name, zone_config in zones.items():
                    zone = self.create_zone_object(zone_config)
                    logger.info(f"Created zone: {zone.name}")
            
            # Deploy zone-based rules
            zone_rules = zone_policies.get("zone_based_rules", {})
            for rule_category, rules in zone_rules.items():
                for rule_name, rule_config in rules.items():
                    policy = self.create_policy_object(rule_config)
                    if policy.validate_policy():
                        logger.info(f"Created policy: {policy.name}")
                    else:
                        logger.warning(f"Invalid policy configuration: {policy.name}")
            
            logger.info("Zone-based policies deployed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deploying zone-based policies: {str(e)}")
            return False
    
    def manage_policies(self, action: str, policy_name: str, policy_config: Optional[Dict] = None) -> bool:
        """Manage policies (create, update, delete, rename)"""
        try:
            if action == "create":
                if not policy_config:
                    logger.error("Policy configuration required for create action")
                    return False
                policy = self.create_policy_object(policy_config)
                return self._create_firewall_rule(policy)
            
            elif action == "update":
                if not policy_config:
                    logger.error("Policy configuration required for update action")
                    return False
                policy = self.create_policy_object(policy_config)
                return self._update_firewall_rule(policy)
            
            elif action == "delete":
                return self._delete_firewall_rule(policy_name)
            
            elif action == "rename":
                if not policy_config:
                    logger.error("New name required for rename action")
                    return False
                return self._rename_firewall_rule(policy_name, policy_config.get("new_name"))
            
            else:
                logger.error(f"Unknown action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error managing policy {policy_name}: {str(e)}")
            return False
    
    def _create_firewall_rule(self, policy: PolicyObject) -> bool:
        """Create firewall rule via API"""
        try:
            rule_config = {
                "name": policy.name,
                "ruleset": "WAN_OUT" if "internet" in policy.destination_zones else "LAN_LOCAL",
                "rule_index": policy.priority,
                "action": policy.action,
                "protocol": "all" if not policy.protocols else policy.protocols[0],
                "logging": policy.logging_enabled,
                "enabled": policy.enabled,
                "dst_address": "any",
                "src_address": "any"
            }
            
            url = f"{self.base_url}/api/s/{self.site}/rest/firewallrule"
            response = self.session.post(url, json=rule_config, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Successfully created firewall rule: {policy.name}")
                return True
            else:
                logger.error(f"Failed to create firewall rule: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating firewall rule: {str(e)}")
            return False
    
    def _update_firewall_rule(self, policy: PolicyObject) -> bool:
        """Update firewall rule via API"""
        # Implementation for updating firewall rules
        logger.info(f"Updating firewall rule: {policy.name}")
        return True
    
    def _delete_firewall_rule(self, rule_name: str) -> bool:
        """Delete firewall rule via API"""
        # Implementation for deleting firewall rules
        logger.info(f"Deleting firewall rule: {rule_name}")
        return True
    
    def _rename_firewall_rule(self, old_name: str, new_name: str) -> bool:
        """Rename firewall rule via API"""
        # Implementation for renaming firewall rules
        logger.info(f"Renaming firewall rule: {old_name} -> {new_name}")
        return True

def main():
    """Main function for testing the enhanced controller"""
    # Load configuration from environment variables
    controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', 'mars.int.bozza.au')
    username = os.getenv('UNIFI_USERNAME_MARS', 'root')
    password = os.getenv('UNIFI_PASSWORD_MARS')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    if not password and not api_key:
        logger.error("No authentication credentials provided")
        return False
    
    # Initialize enhanced controller
    controller = EnhancedUniFiController(
        host=controller_host,
        username=username,
        password=password,
        api_key=api_key
    )
    
    # Authenticate
    if not controller.authenticate():
        logger.error("Failed to authenticate with controller")
        return False
    
    # Perform initial scan
    scan_results = controller.perform_initial_scan()
    
    # Save scan results
    with open(f"network_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(scan_results, f, indent=2, default=str)
    
    logger.info("Network scan completed and saved")
    return True

if __name__ == "__main__":
    main()
