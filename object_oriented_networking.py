#!/usr/bin/env python3
"""
Object-Oriented Networking Implementation
Provides inheritance, templating, and dynamic configuration management
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union, Type
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import requests
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
        logging.FileHandler('oon_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class NetworkObject:
    """Base class for all network objects with inheritance support"""
    name: str
    description: str = ""
    enabled: bool = True
    zone_assignment: Optional[str] = None
    trust_level: str = "unknown"
    parent: Optional['NetworkObject'] = None
    children: List['NetworkObject'] = field(default_factory=list)
    template: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary for API calls"""
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "zone_assignment": self.zone_assignment,
            "trust_level": self.trust_level,
            "template": self.template,
            "attributes": self.attributes
        }
    
    def inherit_from(self, parent: 'NetworkObject') -> None:
        """Inherit properties from parent object"""
        self.parent = parent
        parent.children.append(self)
        
        # Inherit common properties
        if not self.zone_assignment and parent.zone_assignment:
            self.zone_assignment = parent.zone_assignment
        if not self.trust_level or self.trust_level == "unknown":
            self.trust_level = parent.trust_level
        if not self.template and parent.template:
            self.template = parent.template
    
    def apply_template(self, template: 'NetworkTemplate') -> None:
        """Apply template configuration to this object"""
        self.template = template.name
        self.attributes.update(template.default_attributes)
        
        # Apply template-specific configurations
        if hasattr(template, 'apply_to_object'):
            template.apply_to_object(self)
    
    def get_inheritance_chain(self) -> List['NetworkObject']:
        """Get the full inheritance chain from root to this object"""
        chain = []
        current = self
        while current:
            chain.insert(0, current)
            current = current.parent
        return chain
    
    def get_all_children(self) -> List['NetworkObject']:
        """Get all children recursively"""
        all_children = []
        for child in self.children:
            all_children.append(child)
            all_children.extend(child.get_all_children())
        return all_children

class NetworkTemplate(ABC):
    """Abstract base class for network templates"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.default_attributes = {}
        self.required_attributes = []
        self.optional_attributes = []
    
    @abstractmethod
    def apply_to_object(self, obj: NetworkObject) -> None:
        """Apply template configuration to a network object"""
        pass
    
    def validate_object(self, obj: NetworkObject) -> bool:
        """Validate that object meets template requirements"""
        for attr in self.required_attributes:
            if attr not in obj.attributes:
                return False
        return True

class ZoneTemplate(NetworkTemplate):
    """Template for network zones"""
    
    def __init__(self, name: str, trust_level: str, security_policy: str):
        super().__init__(name, f"Template for {trust_level} zone")
        self.trust_level = trust_level
        self.security_policy = security_policy
        self.default_attributes = {
            "trust_level": trust_level,
            "security_policy": security_policy,
            "default_action": "deny",
            "logging_enabled": True,
            "monitoring_enabled": True
        }
        self.required_attributes = ["trust_level", "security_policy"]
    
    def apply_to_object(self, obj: NetworkObject) -> None:
        """Apply zone template to object"""
        obj.trust_level = self.trust_level
        obj.attributes.update(self.default_attributes)

class DeviceTemplate(NetworkTemplate):
    """Template for device groups"""
    
    def __init__(self, name: str, device_type: str, security_requirements: List[str]):
        super().__init__(name, f"Template for {device_type} devices")
        self.device_type = device_type
        self.security_requirements = security_requirements
        self.default_attributes = {
            "device_type": device_type,
            "security_requirements": security_requirements,
            "isolation_level": "standard",
            "monitoring_level": "standard",
            "update_policy": "automatic"
        }
        self.required_attributes = ["device_type", "security_requirements"]
    
    def apply_to_object(self, obj: NetworkObject) -> None:
        """Apply device template to object"""
        obj.attributes.update(self.default_attributes)

class PolicyTemplate(NetworkTemplate):
    """Template for firewall policies"""
    
    def __init__(self, name: str, policy_type: str, default_rules: List[Dict[str, Any]]):
        super().__init__(name, f"Template for {policy_type} policies")
        self.policy_type = policy_type
        self.default_rules = default_rules
        self.default_attributes = {
            "policy_type": policy_type,
            "default_rules": default_rules,
            "priority": "medium",
            "logging": True,
            "monitoring": True
        }
        self.required_attributes = ["policy_type", "default_rules"]
    
    def apply_to_object(self, obj: NetworkObject) -> None:
        """Apply policy template to object"""
        obj.attributes.update(self.default_attributes)

class ObjectOrientedNetworkManager:
    """Manages Object-Oriented Networking with inheritance and templating"""
    
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
        
        # Object registry
        self.objects: Dict[str, NetworkObject] = {}
        self.templates: Dict[str, NetworkTemplate] = {}
        self.inheritance_chains: Dict[str, List[NetworkObject]] = {}
        
        # Initialize templates
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize default network templates"""
        # Zone templates
        self.templates["trust_zone"] = ZoneTemplate(
            "trust_zone", "high", "permissive"
        )
        self.templates["semi_trust_zone"] = ZoneTemplate(
            "semi_trust_zone", "medium", "restrictive"
        )
        self.templates["untrust_zone"] = ZoneTemplate(
            "untrust_zone", "low", "strict"
        )
        
        # Device templates
        self.templates["management_devices"] = DeviceTemplate(
            "management_devices", "management", ["encryption", "authentication", "monitoring"]
        )
        self.templates["user_devices"] = DeviceTemplate(
            "user_devices", "workstation", ["authentication", "monitoring"]
        )
        self.templates["iot_devices"] = DeviceTemplate(
            "iot_devices", "iot", ["isolation", "monitoring"]
        )
        self.templates["security_devices"] = DeviceTemplate(
            "security_devices", "security", ["encryption", "authentication", "isolation", "monitoring"]
        )
        
        # Policy templates
        self.templates["inter_zone_policy"] = PolicyTemplate(
            "inter_zone_policy", "inter_zone", [
                {"action": "allow", "protocol": "tcp", "ports": [80, 443]},
                {"action": "allow", "protocol": "udp", "ports": [53, 123]},
                {"action": "deny", "protocol": "all", "ports": "all"}
            ]
        )
        self.templates["internet_policy"] = PolicyTemplate(
            "internet_policy", "internet", [
                {"action": "allow", "protocol": "tcp", "ports": [80, 443]},
                {"action": "allow", "protocol": "udp", "ports": [53, 123]},
                {"action": "deny", "protocol": "all", "ports": "all"}
            ]
        )
    
    def create_object(self, obj: NetworkObject, parent_name: Optional[str] = None, 
                     template_name: Optional[str] = None) -> bool:
        """Create a network object with inheritance and templating"""
        try:
            # Apply template if specified
            if template_name and template_name in self.templates:
                template = self.templates[template_name]
                obj.apply_template(template)
            
            # Set up inheritance if parent specified
            if parent_name and parent_name in self.objects:
                parent = self.objects[parent_name]
                obj.inherit_from(parent)
            
            # Register object
            self.objects[obj.name] = obj
            
            # Update inheritance chains
            self._update_inheritance_chains(obj)
            
            logger.info(f"Created object '{obj.name}' with template '{template_name}' and parent '{parent_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error creating object '{obj.name}': {str(e)}")
            return False
    
    def _update_inheritance_chains(self, obj: NetworkObject):
        """Update inheritance chains for all affected objects"""
        # Update chain for this object
        self.inheritance_chains[obj.name] = obj.get_inheritance_chain()
        
        # Update chains for all children
        for child in obj.get_all_children():
            self.inheritance_chains[child.name] = child.get_inheritance_chain()
    
    def get_object(self, name: str) -> Optional[NetworkObject]:
        """Get a network object by name"""
        return self.objects.get(name)
    
    def get_template(self, name: str) -> Optional[NetworkTemplate]:
        """Get a template by name"""
        return self.templates.get(name)
    
    def list_objects_by_type(self, object_type: str) -> List[NetworkObject]:
        """List all objects of a specific type"""
        return [obj for obj in self.objects.values() 
                if obj.attributes.get("object_type") == object_type]
    
    def list_objects_by_zone(self, zone: str) -> List[NetworkObject]:
        """List all objects in a specific zone"""
        return [obj for obj in self.objects.values() 
                if obj.zone_assignment == zone]
    
    def get_inheritance_tree(self, root_name: str) -> Dict[str, Any]:
        """Get the inheritance tree starting from a root object"""
        if root_name not in self.objects:
            return {}
        
        root = self.objects[root_name]
        
        def build_tree(obj: NetworkObject) -> Dict[str, Any]:
            tree = {
                "name": obj.name,
                "type": obj.attributes.get("object_type", "unknown"),
                "zone": obj.zone_assignment,
                "trust_level": obj.trust_level,
                "template": obj.template,
                "children": [build_tree(child) for child in obj.children]
            }
            return tree
        
        return build_tree(root)
    
    def apply_template_to_zone(self, zone_name: str, template_name: str) -> bool:
        """Apply a template to all objects in a zone"""
        try:
            if template_name not in self.templates:
                logger.error(f"Template '{template_name}' not found")
                return False
            
            template = self.templates[template_name]
            zone_objects = self.list_objects_by_zone(zone_name)
            
            for obj in zone_objects:
                obj.apply_template(template)
                logger.info(f"Applied template '{template_name}' to object '{obj.name}'")
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying template to zone: {str(e)}")
            return False
    
    def create_policy_from_template(self, policy_name: str, template_name: str, 
                                  custom_rules: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Create a policy from a template with optional custom rules"""
        try:
            if template_name not in self.templates:
                logger.error(f"Template '{template_name}' not found")
                return False
            
            template = self.templates[template_name]
            
            # Create policy object
            policy_obj = NetworkObject(
                name=policy_name,
                description=f"Policy created from template '{template_name}'",
                attributes={"object_type": "policy"}
            )
            
            # Apply template
            policy_obj.apply_template(template)
            
            # Add custom rules if provided
            if custom_rules:
                policy_obj.attributes["custom_rules"] = custom_rules
            
            # Register object
            self.objects[policy_name] = policy_obj
            
            logger.info(f"Created policy '{policy_name}' from template '{template_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error creating policy from template: {str(e)}")
            return False
    
    def deploy_to_unifi(self, object_name: str) -> bool:
        """Deploy a network object to UniFi controller"""
        try:
            if object_name not in self.objects:
                logger.error(f"Object '{object_name}' not found")
                return False
            
            obj = self.objects[object_name]
            
            # Determine deployment type based on object attributes
            object_type = obj.attributes.get("object_type", "unknown")
            
            if object_type == "zone":
                return self._deploy_zone(obj)
            elif object_type == "device_group":
                return self._deploy_device_group(obj)
            elif object_type == "policy":
                return self._deploy_policy(obj)
            else:
                logger.error(f"Unknown object type: {object_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error deploying object '{object_name}': {str(e)}")
            return False
    
    def _deploy_zone(self, zone_obj: NetworkObject) -> bool:
        """Deploy a zone object to UniFi"""
        try:
            # Create network configuration
            network_config = {
                "name": zone_obj.name,
                "purpose": "corporate",
                "vlan": zone_obj.attributes.get("vlan_id"),
                "ip_subnet": zone_obj.attributes.get("subnet"),
                "enabled": zone_obj.enabled
            }
            
            response = self.session.post(
                f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/networkconf",
                json=network_config
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully deployed zone '{zone_obj.name}'")
                return True
            else:
                logger.error(f"Failed to deploy zone: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deploying zone: {str(e)}")
            return False
    
    def _deploy_device_group(self, group_obj: NetworkObject) -> bool:
        """Deploy a device group object to UniFi"""
        try:
            # Create firewall group configuration
            group_config = {
                "name": group_obj.name,
                "group_type": "address-group",
                "enabled": group_obj.enabled
            }
            
            response = self.session.post(
                f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallgroup",
                json=group_config
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully deployed device group '{group_obj.name}'")
                return True
            else:
                logger.error(f"Failed to deploy device group: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deploying device group: {str(e)}")
            return False
    
    def _deploy_policy(self, policy_obj: NetworkObject) -> bool:
        """Deploy a policy object to UniFi"""
        try:
            # Create firewall rule configuration
            rule_config = {
                "name": policy_obj.name,
                "ruleset": policy_obj.attributes.get("ruleset", "LAN_IN"),
                "action": policy_obj.attributes.get("action", "accept"),
                "enabled": policy_obj.enabled
            }
            
            response = self.session.post(
                f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule",
                json=rule_config
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully deployed policy '{policy_obj.name}'")
                return True
            else:
                logger.error(f"Failed to deploy policy: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deploying policy: {str(e)}")
            return False
    
    def generate_inheritance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive inheritance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_objects": len(self.objects),
            "total_templates": len(self.templates),
            "inheritance_chains": self.inheritance_chains,
            "object_hierarchy": {},
            "template_usage": {}
        }
        
        # Build object hierarchy
        roots = [obj for obj in self.objects.values() if obj.parent is None]
        for root in roots:
            report["object_hierarchy"][root.name] = self.get_inheritance_tree(root.name)
        
        # Analyze template usage
        for obj in self.objects.values():
            if obj.template:
                if obj.template not in report["template_usage"]:
                    report["template_usage"][obj.template] = 0
                report["template_usage"][obj.template] += 1
        
        return report

def main():
    """Main function for Object-Oriented Networking demonstration"""
    print(f"\n{'='*80}")
    print("Object-Oriented Networking with Inheritance and Templating")
    print(f"{'='*80}")
    
    # Load environment variables
    controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', '192.168.22.194')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    if not api_key:
        print("❌ Error: UNIFI_API_KEY_MARS not set in .env file")
        return False
    
    try:
        # Initialize OON Manager
        print("Initializing Object-Oriented Networking Manager...")
        oon_manager = ObjectOrientedNetworkManager(controller_host, api_key)
        
        # Create zone hierarchy
        print("\nCreating zone hierarchy...")
        
        # Root zone
        root_zone = NetworkObject(
            name="Network_Root",
            description="Root network zone",
            attributes={"object_type": "zone", "vlan_id": 1, "subnet": "192.168.1.0/24"}
        )
        oon_manager.create_object(root_zone, template_name="trust_zone")
        
        # Trust zones
        management_zone = NetworkObject(
            name="Management_Zone",
            description="High-trust management zone",
            attributes={"object_type": "zone", "vlan_id": 5, "subnet": "192.168.5.0/24"}
        )
        oon_manager.create_object(management_zone, parent_name="Network_Root", template_name="trust_zone")
        
        corporate_zone = NetworkObject(
            name="Corporate_Zone",
            description="High-trust corporate zone",
            attributes={"object_type": "zone", "vlan_id": 10, "subnet": "192.168.10.0/24"}
        )
        oon_manager.create_object(corporate_zone, parent_name="Network_Root", template_name="trust_zone")
        
        # Semi-trust zones
        user_zone = NetworkObject(
            name="User_Zone",
            description="Medium-trust user zone",
            attributes={"object_type": "zone", "vlan_id": 20, "subnet": "192.168.20.0/24"}
        )
        oon_manager.create_object(user_zone, parent_name="Network_Root", template_name="semi_trust_zone")
        
        # Untrust zones
        guest_zone = NetworkObject(
            name="Guest_Zone",
            description="Low-trust guest zone",
            attributes={"object_type": "zone", "vlan_id": 80, "subnet": "192.168.80.0/24"}
        )
        oon_manager.create_object(guest_zone, parent_name="Network_Root", template_name="untrust_zone")
        
        # Create device groups with inheritance
        print("\nCreating device groups with inheritance...")
        
        management_devices = NetworkObject(
            name="Management_Devices",
            description="Management infrastructure devices",
            attributes={"object_type": "device_group"}
        )
        oon_manager.create_object(management_devices, parent_name="Management_Zone", template_name="management_devices")
        
        corporate_devices = NetworkObject(
            name="Corporate_Devices",
            description="Corporate server devices",
            attributes={"object_type": "device_group"}
        )
        oon_manager.create_object(corporate_devices, parent_name="Corporate_Zone", template_name="management_devices")
        
        user_devices = NetworkObject(
            name="User_Devices",
            description="User workstation devices",
            attributes={"object_type": "device_group"}
        )
        oon_manager.create_object(user_devices, parent_name="User_Zone", template_name="user_devices")
        
        # Create policies from templates
        print("\nCreating policies from templates...")
        
        oon_manager.create_policy_from_template(
            "Management_to_Corporate",
            "inter_zone_policy",
            [{"source": "Management_Zone", "destination": "Corporate_Zone"}]
        )
        
        oon_manager.create_policy_from_template(
            "Corporate_to_Internet",
            "internet_policy",
            [{"source": "Corporate_Zone", "destination": "internet"}]
        )
        
        # Generate inheritance report
        print("\nGenerating inheritance report...")
        report = oon_manager.generate_inheritance_report()
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"oon_inheritance_report_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n{'='*80}")
        print("✅ OBJECT-ORIENTED NETWORKING SETUP COMPLETED!")
        print(f"{'='*80}")
        print(f"Created {report['total_objects']} network objects")
        print(f"Using {report['total_templates']} templates")
        print(f"Inheritance report saved to: {filename}")
        print("\nKey Features Implemented:")
        print("  ✓ Object inheritance and parent-child relationships")
        print("  ✓ Template-based object creation")
        print("  ✓ Dynamic attribute inheritance")
        print("  ✓ Hierarchical object management")
        print("  ✓ Template validation and application")
        print("  ✓ Comprehensive inheritance reporting")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
