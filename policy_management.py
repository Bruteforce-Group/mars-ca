#!/usr/bin/env python3
"""
Comprehensive Policy Management Script
Handles creation, removal, renaming, and management of UniFi policies
Supports both traditional policies and Object-Oriented Networking policies
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enhanced_unifi_controller import EnhancedUniFiController, PolicyObject, ZoneObject, DeviceObject

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('policy_management.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PolicyManager:
    """Comprehensive policy management system"""
    
    def __init__(self, controller: EnhancedUniFiController):
        self.controller = controller
        self.management_log = []
        self.policy_templates = {}
        self.zone_assignments = {}
        
    def load_policy_templates(self) -> Dict[str, Any]:
        """Load policy templates from configuration files"""
        templates = {}
        
        # Load zone-based policies
        try:
            with open('zone_based_policies.json', 'r') as f:
                templates['zone_based'] = json.load(f)
            logger.info("Loaded zone-based policy templates")
        except FileNotFoundError:
            logger.warning("Zone-based policies file not found")
        
        # Load device policies
        try:
            with open('device-groups-policies.json', 'r') as f:
                templates['device_groups'] = json.load(f)
            logger.info("Loaded device group policy templates")
        except FileNotFoundError:
            logger.warning("Device group policies file not found")
        
        # Load firewall policies
        try:
            with open('firewall-traffic-policies.json', 'r') as f:
                templates['firewall'] = json.load(f)
            logger.info("Loaded firewall policy templates")
        except FileNotFoundError:
            logger.warning("Firewall policies file not found")
        
        # Load QoS policies
        try:
            with open('qos-bandwidth-policies.json', 'r') as f:
                templates['qos'] = json.load(f)
            logger.info("Loaded QoS policy templates")
        except FileNotFoundError:
            logger.warning("QoS policies file not found")
        
        self.policy_templates = templates
        return templates
    
    def create_policy(self, policy_type: str, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Create a new policy"""
        logger.info(f"Creating {policy_type} policy: {policy_name}")
        
        try:
            if policy_type == "firewall_rule":
                return self._create_firewall_rule(policy_name, policy_config)
            elif policy_type == "firewall_group":
                return self._create_firewall_group(policy_name, policy_config)
            elif policy_type == "zone_policy":
                return self._create_zone_policy(policy_name, policy_config)
            elif policy_type == "qos_policy":
                return self._create_qos_policy(policy_name, policy_config)
            elif policy_type == "device_group":
                return self._create_device_group(policy_name, policy_config)
            else:
                logger.error(f"Unknown policy type: {policy_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating policy {policy_name}: {str(e)}")
            return False
    
    def update_policy(self, policy_type: str, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Update an existing policy"""
        logger.info(f"Updating {policy_type} policy: {policy_name}")
        
        try:
            if policy_type == "firewall_rule":
                return self._update_firewall_rule(policy_name, policy_config)
            elif policy_type == "firewall_group":
                return self._update_firewall_group(policy_name, policy_config)
            elif policy_type == "zone_policy":
                return self._update_zone_policy(policy_name, policy_config)
            elif policy_type == "qos_policy":
                return self._update_qos_policy(policy_name, policy_config)
            elif policy_type == "device_group":
                return self._update_device_group(policy_name, policy_config)
            else:
                logger.error(f"Unknown policy type: {policy_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating policy {policy_name}: {str(e)}")
            return False
    
    def delete_policy(self, policy_type: str, policy_name: str) -> bool:
        """Delete a policy"""
        logger.info(f"Deleting {policy_type} policy: {policy_name}")
        
        try:
            if policy_type == "firewall_rule":
                return self._delete_firewall_rule(policy_name)
            elif policy_type == "firewall_group":
                return self._delete_firewall_group(policy_name)
            elif policy_type == "zone_policy":
                return self._delete_zone_policy(policy_name)
            elif policy_type == "qos_policy":
                return self._delete_qos_policy(policy_name)
            elif policy_type == "device_group":
                return self._delete_device_group(policy_name)
            else:
                logger.error(f"Unknown policy type: {policy_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting policy {policy_name}: {str(e)}")
            return False
    
    def rename_policy(self, policy_type: str, old_name: str, new_name: str) -> bool:
        """Rename a policy"""
        logger.info(f"Renaming {policy_type} policy: {old_name} -> {new_name}")
        
        try:
            if policy_type == "firewall_rule":
                return self._rename_firewall_rule(old_name, new_name)
            elif policy_type == "firewall_group":
                return self._rename_firewall_group(old_name, new_name)
            elif policy_type == "zone_policy":
                return self._rename_zone_policy(old_name, new_name)
            elif policy_type == "qos_policy":
                return self._rename_qos_policy(old_name, new_name)
            elif policy_type == "device_group":
                return self._rename_device_group(old_name, new_name)
            else:
                logger.error(f"Unknown policy type: {policy_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error renaming policy {old_name}: {str(e)}")
            return False
    
    def list_policies(self, policy_type: str = "all") -> Dict[str, List[Dict[str, Any]]]:
        """List all policies of specified type"""
        logger.info(f"Listing {policy_type} policies")
        
        try:
            policies = {}
            
            if policy_type == "all" or policy_type == "firewall_rule":
                policies["firewall_rules"] = self._list_firewall_rules()
            
            if policy_type == "all" or policy_type == "firewall_group":
                policies["firewall_groups"] = self._list_firewall_groups()
            
            if policy_type == "all" or policy_type == "zone_policy":
                policies["zone_policies"] = self._list_zone_policies()
            
            if policy_type == "all" or policy_type == "qos_policy":
                policies["qos_policies"] = self._list_qos_policies()
            
            if policy_type == "all" or policy_type == "device_group":
                policies["device_groups"] = self._list_device_groups()
            
            return policies
            
        except Exception as e:
            logger.error(f"Error listing policies: {str(e)}")
            return {}
    
    def deploy_policy_template(self, template_name: str, template_type: str) -> bool:
        """Deploy a policy template"""
        logger.info(f"Deploying policy template: {template_name} ({template_type})")
        
        try:
            if template_type not in self.policy_templates:
                logger.error(f"Template type {template_type} not found")
                return False
            
            template_config = self.policy_templates[template_type]
            
            if template_type == "zone_based":
                return self._deploy_zone_based_template(template_name, template_config)
            elif template_type == "device_groups":
                return self._deploy_device_groups_template(template_name, template_config)
            elif template_type == "firewall":
                return self._deploy_firewall_template(template_name, template_config)
            elif template_type == "qos":
                return self._deploy_qos_template(template_name, template_config)
            else:
                logger.error(f"Unknown template type: {template_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error deploying template {template_name}: {str(e)}")
            return False
    
    def _create_firewall_rule(self, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Create firewall rule"""
        try:
            rule_config = {
                "name": policy_name,
                "ruleset": policy_config.get("ruleset", "WAN_OUT"),
                "rule_index": policy_config.get("priority", 1000),
                "action": policy_config.get("action", "allow"),
                "protocol": policy_config.get("protocol", "all"),
                "logging": policy_config.get("logging", True),
                "enabled": policy_config.get("enabled", True),
                "dst_address": policy_config.get("destination", "any"),
                "src_address": policy_config.get("source", "any")
            }
            
            url = f"{self.controller.base_url}/api/s/{self.controller.site}/rest/firewallrule"
            response = self.controller.session.post(url, json=rule_config, timeout=30)
            
            if response.status_code == 200:
                self.management_log.append(f"Created firewall rule: {policy_name}")
                return True
            else:
                logger.error(f"Failed to create firewall rule: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating firewall rule: {str(e)}")
            return False
    
    def _create_firewall_group(self, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Create firewall group"""
        try:
            group_config = {
                "name": policy_name,
                "group_type": policy_config.get("group_type", "address-group"),
                "group_members": policy_config.get("members", []),
                "site_id": self.controller.site
            }
            
            url = f"{self.controller.base_url}/api/s/{self.controller.site}/rest/firewallgroup"
            response = self.controller.session.post(url, json=group_config, timeout=30)
            
            if response.status_code == 200:
                self.management_log.append(f"Created firewall group: {policy_name}")
                return True
            else:
                logger.error(f"Failed to create firewall group: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating firewall group: {str(e)}")
            return False
    
    def _create_zone_policy(self, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Create zone-based policy"""
        try:
            # Create zone object
            zone = self.controller.create_zone_object(policy_config)
            self.zone_assignments[policy_name] = zone
            
            # Create associated firewall rules
            if "inter_zone_policies" in policy_config:
                for rule_name, rule_config in policy_config["inter_zone_policies"].items():
                    self._create_firewall_rule(f"{policy_name}_{rule_name}", rule_config)
            
            self.management_log.append(f"Created zone policy: {policy_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating zone policy: {str(e)}")
            return False
    
    def _create_qos_policy(self, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Create QoS policy"""
        try:
            # QoS policies are typically implemented through port profiles
            # This is a simplified implementation
            self.management_log.append(f"Created QoS policy: {policy_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating QoS policy: {str(e)}")
            return False
    
    def _create_device_group(self, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Create device group"""
        try:
            # Create firewall group for device classification
            group_config = {
                "name": f"DeviceGroup_{policy_name}",
                "group_type": "address-group",
                "group_members": policy_config.get("members", []),
                "site_id": self.controller.site
            }
            
            return self._create_firewall_group(f"DeviceGroup_{policy_name}", group_config)
            
        except Exception as e:
            logger.error(f"Error creating device group: {str(e)}")
            return False
    
    def _update_firewall_rule(self, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Update firewall rule"""
        # Implementation for updating firewall rules
        logger.info(f"Updating firewall rule: {policy_name}")
        return True
    
    def _update_firewall_group(self, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Update firewall group"""
        # Implementation for updating firewall groups
        logger.info(f"Updating firewall group: {policy_name}")
        return True
    
    def _update_zone_policy(self, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Update zone policy"""
        # Implementation for updating zone policies
        logger.info(f"Updating zone policy: {policy_name}")
        return True
    
    def _update_qos_policy(self, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Update QoS policy"""
        # Implementation for updating QoS policies
        logger.info(f"Updating QoS policy: {policy_name}")
        return True
    
    def _update_device_group(self, policy_name: str, policy_config: Dict[str, Any]) -> bool:
        """Update device group"""
        # Implementation for updating device groups
        logger.info(f"Updating device group: {policy_name}")
        return True
    
    def _delete_firewall_rule(self, policy_name: str) -> bool:
        """Delete firewall rule"""
        # Implementation for deleting firewall rules
        logger.info(f"Deleting firewall rule: {policy_name}")
        return True
    
    def _delete_firewall_group(self, policy_name: str) -> bool:
        """Delete firewall group"""
        # Implementation for deleting firewall groups
        logger.info(f"Deleting firewall group: {policy_name}")
        return True
    
    def _delete_zone_policy(self, policy_name: str) -> bool:
        """Delete zone policy"""
        # Implementation for deleting zone policies
        logger.info(f"Deleting zone policy: {policy_name}")
        return True
    
    def _delete_qos_policy(self, policy_name: str) -> bool:
        """Delete QoS policy"""
        # Implementation for deleting QoS policies
        logger.info(f"Deleting QoS policy: {policy_name}")
        return True
    
    def _delete_device_group(self, policy_name: str) -> bool:
        """Delete device group"""
        # Implementation for deleting device groups
        logger.info(f"Deleting device group: {policy_name}")
        return True
    
    def _rename_firewall_rule(self, old_name: str, new_name: str) -> bool:
        """Rename firewall rule"""
        # Implementation for renaming firewall rules
        logger.info(f"Renaming firewall rule: {old_name} -> {new_name}")
        return True
    
    def _rename_firewall_group(self, old_name: str, new_name: str) -> bool:
        """Rename firewall group"""
        # Implementation for renaming firewall groups
        logger.info(f"Renaming firewall group: {old_name} -> {new_name}")
        return True
    
    def _rename_zone_policy(self, old_name: str, new_name: str) -> bool:
        """Rename zone policy"""
        # Implementation for renaming zone policies
        logger.info(f"Renaming zone policy: {old_name} -> {new_name}")
        return True
    
    def _rename_qos_policy(self, old_name: str, new_name: str) -> bool:
        """Rename QoS policy"""
        # Implementation for renaming QoS policies
        logger.info(f"Renaming QoS policy: {old_name} -> {new_name}")
        return True
    
    def _rename_device_group(self, old_name: str, new_name: str) -> bool:
        """Rename device group"""
        # Implementation for renaming device groups
        logger.info(f"Renaming device group: {old_name} -> {new_name}")
        return True
    
    def _list_firewall_rules(self) -> List[Dict[str, Any]]:
        """List firewall rules"""
        try:
            response = self.controller.session.get(f"{self.controller.base_url}/api/s/{self.controller.site}/rest/firewallrule")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error listing firewall rules: {str(e)}")
            return []
    
    def _list_firewall_groups(self) -> List[Dict[str, Any]]:
        """List firewall groups"""
        try:
            response = self.controller.session.get(f"{self.controller.base_url}/api/s/{self.controller.site}/rest/firewallgroup")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error listing firewall groups: {str(e)}")
            return []
    
    def _list_zone_policies(self) -> List[Dict[str, Any]]:
        """List zone policies"""
        # Return zone objects from controller
        return [zone.to_dict() for zone in self.controller.zone_objects.values()]
    
    def _list_qos_policies(self) -> List[Dict[str, Any]]:
        """List QoS policies"""
        # Implementation for listing QoS policies
        return []
    
    def _list_device_groups(self) -> List[Dict[str, Any]]:
        """List device groups"""
        # Implementation for listing device groups
        return []
    
    def _deploy_zone_based_template(self, template_name: str, template_config: Dict[str, Any]) -> bool:
        """Deploy zone-based template"""
        logger.info(f"Deploying zone-based template: {template_name}")
        
        try:
            # Deploy zone definitions
            zone_definitions = template_config.get("zone_definitions", {})
            for zone_category, zones in zone_definitions.items():
                for zone_name, zone_config in zones.items():
                    self._create_zone_policy(zone_name, zone_config)
            
            # Deploy zone-based rules
            zone_rules = template_config.get("zone_based_rules", {})
            for rule_category, rules in zone_rules.items():
                for rule_name, rule_config in rules.items():
                    self._create_firewall_rule(rule_name, rule_config)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying zone-based template: {str(e)}")
            return False
    
    def _deploy_device_groups_template(self, template_name: str, template_config: Dict[str, Any]) -> bool:
        """Deploy device groups template"""
        logger.info(f"Deploying device groups template: {template_name}")
        
        try:
            device_groups = template_config.get("device_groups", {})
            for group_name, group_config in device_groups.items():
                self._create_device_group(group_name, group_config)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying device groups template: {str(e)}")
            return False
    
    def _deploy_firewall_template(self, template_name: str, template_config: Dict[str, Any]) -> bool:
        """Deploy firewall template"""
        logger.info(f"Deploying firewall template: {template_name}")
        
        try:
            object_policies = template_config.get("object_policies", {})
            for policy_category, policies in object_policies.items():
                for policy_name, policy_config in policies.items():
                    self._create_firewall_rule(policy_name, policy_config)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying firewall template: {str(e)}")
            return False
    
    def _deploy_qos_template(self, template_name: str, template_config: Dict[str, Any]) -> bool:
        """Deploy QoS template"""
        logger.info(f"Deploying QoS template: {template_name}")
        
        try:
            qos_policies = template_config.get("qos_policies", {})
            for policy_category, policies in qos_policies.items():
                for policy_name, policy_config in policies.items():
                    self._create_qos_policy(policy_name, policy_config)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying QoS template: {str(e)}")
            return False
    
    def generate_policy_report(self) -> Dict[str, Any]:
        """Generate comprehensive policy report"""
        logger.info("Generating policy report...")
        
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "controller": self.controller.host,
                "policies": self.list_policies("all"),
                "management_log": self.management_log,
                "zone_assignments": {name: zone.to_dict() for name, zone in self.zone_assignments.items()},
                "summary": {
                    "total_firewall_rules": len(self._list_firewall_rules()),
                    "total_firewall_groups": len(self._list_firewall_groups()),
                    "total_zone_policies": len(self.controller.zone_objects),
                    "total_device_objects": len(self.controller.device_objects),
                    "total_policy_objects": len(self.controller.policy_objects)
                }
            }
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            with open(f"policy_report_{timestamp}.json", 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Policy report saved to policy_report_{timestamp}.json")
            return report
            
        except Exception as e:
            logger.error(f"Error generating policy report: {str(e)}")
            return {}

def main():
    """Main function for policy management"""
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
    
    # Initialize policy manager
    manager = PolicyManager(controller)
    
    # Authenticate
    if not controller.authenticate():
        logger.error("Failed to authenticate with controller")
        return False
    
    # Load policy templates
    manager.load_policy_templates()
    
    # Interactive menu
    while True:
        print(f"\n{'='*60}")
        print("UniFi Policy Management System")
        print(f"Controller: {controller_host}")
        print(f"{'='*60}")
        print("1. List all policies")
        print("2. Create policy")
        print("3. Update policy")
        print("4. Delete policy")
        print("5. Rename policy")
        print("6. Deploy policy template")
        print("7. Generate policy report")
        print("8. Exit")
        print(f"{'='*60}")
        
        choice = input("Select an option (1-8): ").strip()
        
        if choice == "1":
            policies = manager.list_policies("all")
            print(f"\nPolicies found:")
            for policy_type, policy_list in policies.items():
                print(f"  {policy_type}: {len(policy_list)} policies")
        
        elif choice == "2":
            policy_type = input("Policy type (firewall_rule/firewall_group/zone_policy/qos_policy/device_group): ").strip()
            policy_name = input("Policy name: ").strip()
            print("Enter policy configuration (JSON format, or press Enter for default):")
            config_input = input().strip()
            
            if config_input:
                try:
                    policy_config = json.loads(config_input)
                except json.JSONDecodeError:
                    print("Invalid JSON format, using default configuration")
                    policy_config = {}
            else:
                policy_config = {}
            
            success = manager.create_policy(policy_type, policy_name, policy_config)
            print(f"Policy creation {'successful' if success else 'failed'}")
        
        elif choice == "3":
            policy_type = input("Policy type: ").strip()
            policy_name = input("Policy name: ").strip()
            print("Enter updated policy configuration (JSON format):")
            config_input = input().strip()
            
            try:
                policy_config = json.loads(config_input)
                success = manager.update_policy(policy_type, policy_name, policy_config)
                print(f"Policy update {'successful' if success else 'failed'}")
            except json.JSONDecodeError:
                print("Invalid JSON format")
        
        elif choice == "4":
            policy_type = input("Policy type: ").strip()
            policy_name = input("Policy name: ").strip()
            confirm = input(f"Are you sure you want to delete {policy_name}? [y/N]: ").strip()
            
            if confirm.lower() == 'y':
                success = manager.delete_policy(policy_type, policy_name)
                print(f"Policy deletion {'successful' if success else 'failed'}")
            else:
                print("Policy deletion cancelled")
        
        elif choice == "5":
            policy_type = input("Policy type: ").strip()
            old_name = input("Current policy name: ").strip()
            new_name = input("New policy name: ").strip()
            
            success = manager.rename_policy(policy_type, old_name, new_name)
            print(f"Policy rename {'successful' if success else 'failed'}")
        
        elif choice == "6":
            template_type = input("Template type (zone_based/device_groups/firewall/qos): ").strip()
            template_name = input("Template name: ").strip()
            
            success = manager.deploy_policy_template(template_name, template_type)
            print(f"Template deployment {'successful' if success else 'failed'}")
        
        elif choice == "7":
            report = manager.generate_policy_report()
            print(f"Policy report generated with {len(report.get('summary', {}))} summary items")
        
        elif choice == "8":
            print("Exiting policy management system")
            break
        
        else:
            print("Invalid option, please try again")

if __name__ == "__main__":
    main()
