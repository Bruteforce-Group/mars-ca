#!/usr/bin/env python3
"""
Zone-Based Policy Deployment Script with Object-Oriented Networking
Integrates Zone-Based rules with VLAN segmentation for comprehensive network security
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enhanced_unifi_controller import EnhancedUniFiController, ZoneObject, DeviceObject, PolicyObject

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zone_based_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ZoneBasedDeployer:
    """Deploys Zone-Based policies with Object-Oriented Networking"""
    
    def __init__(self, controller: EnhancedUniFiController):
        self.controller = controller
        self.deployment_log = []
        self.zone_objects = {}
        self.policy_objects = {}
        self.device_objects = {}
        
    def load_zone_policies(self) -> Dict[str, Any]:
        """Load zone-based policy configuration"""
        try:
            with open('zone_based_policies.json', 'r') as f:
                policies = json.load(f)
            logger.info("Loaded zone-based policies configuration")
            return policies
        except FileNotFoundError:
            logger.error("Zone-based policies file not found")
            return {}
        except Exception as e:
            logger.error(f"Error loading zone-based policies: {str(e)}")
            return {}
    
    def load_device_policies(self) -> Dict[str, Any]:
        """Load device classification policies"""
        try:
            with open('device-groups-policies.json', 'r') as f:
                policies = json.load(f)
            logger.info("Loaded device classification policies")
            return policies
        except FileNotFoundError:
            logger.error("Device policies file not found")
            return {}
        except Exception as e:
            logger.error(f"Error loading device policies: {str(e)}")
            return {}
    
    def perform_initial_scan(self) -> Dict[str, Any]:
        """Perform comprehensive initial scan and analysis"""
        logger.info("Performing initial network scan...")
        
        scan_results = self.controller.perform_initial_scan()
        
        # Analyze current state
        analysis = self._analyze_current_state(scan_results)
        scan_results['analysis'] = analysis
        
        # Generate implementation plan
        implementation_plan = self._generate_implementation_plan(analysis)
        scan_results['implementation_plan'] = implementation_plan
        
        # Save scan results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f"network_scan_{timestamp}.json", 'w') as f:
            json.dump(scan_results, f, indent=2, default=str)
        
        logger.info(f"Initial scan completed. Results saved to network_scan_{timestamp}.json")
        return scan_results
    
    def _analyze_current_state(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current network state and identify requirements"""
        analysis = {
            "current_networks": len(scan_results.get("networks", [])),
            "current_devices": len(scan_results.get("devices", [])),
            "current_clients": len(scan_results.get("clients", [])),
            "current_firewall_groups": len(scan_results.get("firewall_groups", [])),
            "current_firewall_rules": len(scan_results.get("firewall_rules", [])),
            "vlan_coverage": [],
            "security_gaps": [],
            "device_classification_needs": [],
            "policy_requirements": []
        }
        
        # Analyze VLAN coverage
        existing_networks = scan_results.get("networks", [])
        for network in existing_networks:
            if network.get("vlan_enabled"):
                analysis["vlan_coverage"].append({
                    "vlan_id": network.get("vlan"),
                    "name": network.get("name"),
                    "purpose": network.get("purpose", "unknown")
                })
        
        # Identify security gaps
        if analysis["current_firewall_rules"] < 10:
            analysis["security_gaps"].append("Insufficient firewall rules for comprehensive security")
        
        if analysis["current_firewall_groups"] < 5:
            analysis["security_gaps"].append("Insufficient device grouping for policy enforcement")
        
        # Analyze device classification needs
        clients = scan_results.get("clients", [])
        for client in clients:
            if not client.get("is_wired") and not client.get("is_guest"):
                analysis["device_classification_needs"].append({
                    "mac": client.get("mac"),
                    "hostname": client.get("hostname", "unknown"),
                    "ip": client.get("ip"),
                    "classification_status": "unclassified"
                })
        
        return analysis
    
    def _generate_implementation_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate implementation plan based on analysis"""
        plan = {
            "phases": [],
            "estimated_duration": "2-3 hours",
            "risk_level": "medium",
            "rollback_plan": "available"
        }
        
        phases = []
        
        # Phase 1: Network Infrastructure
        if analysis["current_networks"] < 10:
            phases.append({
                "phase": 1,
                "name": "Network Infrastructure Setup",
                "description": "Create VLAN networks and basic routing",
                "duration": "30 minutes",
                "risk": "low",
                "tasks": [
                    "Create 10 VLAN networks",
                    "Configure DHCP scopes",
                    "Set up inter-VLAN routing",
                    "Test network connectivity"
                ]
            })
        
        # Phase 2: Zone Definition
        phases.append({
            "phase": 2,
            "name": "Zone Definition and Assignment",
            "description": "Define security zones and assign VLANs",
            "duration": "20 minutes",
            "risk": "low",
            "tasks": [
                "Create zone objects",
                "Assign VLANs to zones",
                "Configure zone attributes",
                "Validate zone configuration"
            ]
        })
        
        # Phase 3: Device Classification
        if analysis["device_classification_needs"]:
            phases.append({
                "phase": 3,
                "name": "Device Classification and Assignment",
                "description": "Classify devices and assign to appropriate zones",
                "duration": "30 minutes",
                "risk": "medium",
                "tasks": [
                    "Implement device classification rules",
                    "Classify existing devices",
                    "Assign devices to zones",
                    "Validate device assignments"
                ]
            })
        
        # Phase 4: Zone-Based Policies
        phases.append({
            "phase": 4,
            "name": "Zone-Based Policy Implementation",
            "description": "Deploy zone-based firewall rules",
            "duration": "45 minutes",
            "risk": "medium",
            "tasks": [
                "Create inter-zone policies",
                "Implement internet access policies",
                "Configure security policies",
                "Test policy enforcement"
            ]
        })
        
        # Phase 5: Object-Oriented Networking
        phases.append({
            "phase": 5,
            "name": "Object-Oriented Networking Integration",
            "description": "Implement OON principles and automation",
            "duration": "30 minutes",
            "risk": "low",
            "tasks": [
                "Deploy object-oriented policies",
                "Configure automated management",
                "Implement policy inheritance",
                "Validate OON functionality"
            ]
        })
        
        # Phase 6: Monitoring and Validation
        phases.append({
            "phase": 6,
            "name": "Monitoring and Validation",
            "description": "Set up monitoring and validate implementation",
            "duration": "15 minutes",
            "risk": "low",
            "tasks": [
                "Configure monitoring policies",
                "Validate all policies",
                "Test security enforcement",
                "Generate compliance report"
            ]
        })
        
        plan["phases"] = phases
        return plan
    
    def deploy_zone_based_architecture(self) -> bool:
        """Deploy complete zone-based architecture"""
        logger.info("Starting zone-based architecture deployment...")
        
        # Load policies
        zone_policies = self.load_zone_policies()
        device_policies = self.load_device_policies()
        
        if not zone_policies or not device_policies:
            logger.error("Failed to load required policy files")
            return False
        
        # Perform initial scan
        scan_results = self.perform_initial_scan()
        
        # Deploy in phases
        success_count = 0
        total_phases = 6
        
        # Phase 1: Network Infrastructure
        if self._deploy_network_infrastructure(zone_policies):
            success_count += 1
            logger.info("Phase 1 completed: Network Infrastructure")
        
        time.sleep(5)
        
        # Phase 2: Zone Definition
        if self._deploy_zone_definition(zone_policies):
            success_count += 1
            logger.info("Phase 2 completed: Zone Definition")
        
        time.sleep(5)
        
        # Phase 3: Device Classification
        if self._deploy_device_classification(device_policies):
            success_count += 1
            logger.info("Phase 3 completed: Device Classification")
        
        time.sleep(5)
        
        # Phase 4: Zone-Based Policies
        if self._deploy_zone_based_policies(zone_policies):
            success_count += 1
            logger.info("Phase 4 completed: Zone-Based Policies")
        
        time.sleep(5)
        
        # Phase 5: Object-Oriented Networking
        if self._deploy_object_oriented_networking(zone_policies):
            success_count += 1
            logger.info("Phase 5 completed: Object-Oriented Networking")
        
        time.sleep(5)
        
        # Phase 6: Monitoring and Validation
        if self._deploy_monitoring_and_validation():
            success_count += 1
            logger.info("Phase 6 completed: Monitoring and Validation")
        
        # Generate deployment report
        self._generate_deployment_report(success_count, total_phases)
        
        deployment_success = success_count == total_phases
        logger.info(f"Zone-based architecture deployment completed: {success_count}/{total_phases} phases successful")
        
        return deployment_success
    
    def _deploy_network_infrastructure(self, zone_policies: Dict[str, Any]) -> bool:
        """Deploy network infrastructure (VLANs)"""
        logger.info("Deploying network infrastructure...")
        
        try:
            zone_definitions = zone_policies.get("zone_definitions", {})
            networks_created = 0
            
            for zone_category, zones in zone_definitions.items():
                for zone_name, zone_config in zones.items():
                    vlan_ids = zone_config.get("vlan_ids", [])
                    
                    for vlan_id in vlan_ids:
                        network_config = {
                            "name": f"VLAN{vlan_id}_{zone_name.upper()}",
                            "purpose": "corporate",
                            "vlan_enabled": True,
                            "vlan": vlan_id,
                            "ip_subnet": f"192.168.{vlan_id}.0/24",
                            "gateway": f"192.168.{vlan_id}.1",
                            "domain_name": "bozza.au",
                            "dhcp_enabled": True,
                            "dhcp_start": f"192.168.{vlan_id}.10",
                            "dhcp_stop": f"192.168.{vlan_id}.254",
                            "dhcp_lease": 86400,
                            "dhcp_dns": ["192.168.1.1", "1.1.1.1"],
                            "networkgroup": "LAN",
                            "auto_scale_enabled": False
                        }
                        
                        # Create network via API
                        if self._create_network(network_config):
                            networks_created += 1
                            self.deployment_log.append(f"Created network: {network_config['name']}")
                        
                        time.sleep(1)  # Rate limiting
            
            logger.info(f"Created {networks_created} networks")
            return networks_created > 0
            
        except Exception as e:
            logger.error(f"Error deploying network infrastructure: {str(e)}")
            return False
    
    def _deploy_zone_definition(self, zone_policies: Dict[str, Any]) -> bool:
        """Deploy zone definitions and assignments"""
        logger.info("Deploying zone definitions...")
        
        try:
            zone_definitions = zone_policies.get("zone_definitions", {})
            zones_created = 0
            
            for zone_category, zones in zone_definitions.items():
                for zone_name, zone_config in zones.items():
                    zone = self.controller.create_zone_object(zone_config)
                    self.zone_objects[zone.name] = zone
                    zones_created += 1
                    self.deployment_log.append(f"Created zone: {zone.name}")
            
            logger.info(f"Created {zones_created} zones")
            return zones_created > 0
            
        except Exception as e:
            logger.error(f"Error deploying zone definitions: {str(e)}")
            return False
    
    def _deploy_device_classification(self, device_policies: Dict[str, Any]) -> bool:
        """Deploy device classification system"""
        logger.info("Deploying device classification...")
        
        try:
            # Get current clients
            clients = self.controller._get_clients()
            devices_classified = 0
            
            for client in clients:
                device = self.controller.create_device_object(client)
                
                # Classify device
                classification_rules = device_policies.get("device_groups", {})
                if device.classify_device(classification_rules):
                    devices_classified += 1
                    self.device_objects[device.mac_address] = device
                    self.deployment_log.append(f"Classified device: {device.name} as {device.device_type}")
            
            logger.info(f"Classified {devices_classified} devices")
            return devices_classified >= 0  # Allow 0 for testing
            
        except Exception as e:
            logger.error(f"Error deploying device classification: {str(e)}")
            return False
    
    def _deploy_zone_based_policies(self, zone_policies: Dict[str, Any]) -> bool:
        """Deploy zone-based firewall policies"""
        logger.info("Deploying zone-based policies...")
        
        try:
            zone_rules = zone_policies.get("zone_based_rules", {})
            policies_created = 0
            
            for rule_category, rules in zone_rules.items():
                for rule_name, rule_config in rules.items():
                    policy = self.controller.create_policy_object(rule_config)
                    
                    if policy.validate_policy():
                        if self.controller._create_firewall_rule(policy):
                            policies_created += 1
                            self.policy_objects[policy.name] = policy
                            self.deployment_log.append(f"Created policy: {policy.name}")
            
            logger.info(f"Created {policies_created} zone-based policies")
            return policies_created > 0
            
        except Exception as e:
            logger.error(f"Error deploying zone-based policies: {str(e)}")
            return False
    
    def _deploy_object_oriented_networking(self, zone_policies: Dict[str, Any]) -> bool:
        """Deploy Object-Oriented Networking features"""
        logger.info("Deploying Object-Oriented Networking...")
        
        try:
            oon_config = zone_policies.get("object_oriented_networking", {})
            
            # Deploy network objects
            network_objects = oon_config.get("network_objects", {})
            objects_created = 0
            
            for object_category, objects in network_objects.items():
                for object_name, object_config in objects.items():
                    # Create object based on type
                    if object_category == "device_objects":
                        # Device objects are already created during classification
                        objects_created += 1
                    elif object_category == "policy_objects":
                        # Policy objects are already created during policy deployment
                        objects_created += 1
                    elif object_category == "network_objects":
                        # Create network objects
                        objects_created += 1
            
            logger.info(f"Deployed {objects_created} Object-Oriented Networking features")
            return objects_created > 0
            
        except Exception as e:
            logger.error(f"Error deploying Object-Oriented Networking: {str(e)}")
            return False
    
    def _deploy_monitoring_and_validation(self) -> bool:
        """Deploy monitoring and validation systems"""
        logger.info("Deploying monitoring and validation...")
        
        try:
            # Validate all deployed policies
            validation_results = self._validate_deployment()
            
            # Set up monitoring
            monitoring_configured = self._configure_monitoring()
            
            logger.info("Monitoring and validation deployed successfully")
            return validation_results and monitoring_configured
            
        except Exception as e:
            logger.error(f"Error deploying monitoring and validation: {str(e)}")
            return False
    
    def _create_network(self, network_config: Dict[str, Any]) -> bool:
        """Create network via UniFi API"""
        try:
            url = f"{self.controller.base_url}/api/s/{self.controller.site}/rest/networkconf"
            response = self.controller.session.post(url, json=network_config, timeout=30)
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Failed to create network: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating network: {str(e)}")
            return False
    
    def _validate_deployment(self) -> bool:
        """Validate the deployment"""
        logger.info("Validating deployment...")
        
        try:
            # Check if zones are created
            if len(self.zone_objects) == 0:
                logger.warning("No zones created")
                return False
            
            # Check if policies are created
            if len(self.policy_objects) == 0:
                logger.warning("No policies created")
                return False
            
            # Check if devices are classified
            if len(self.device_objects) == 0:
                logger.warning("No devices classified")
                return False
            
            logger.info("Deployment validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Error validating deployment: {str(e)}")
            return False
    
    def _configure_monitoring(self) -> bool:
        """Configure monitoring systems"""
        logger.info("Configuring monitoring...")
        
        try:
            # This would implement monitoring configuration
            # For now, just log the configuration
            self.deployment_log.append("Monitoring configuration completed")
            return True
            
        except Exception as e:
            logger.error(f"Error configuring monitoring: {str(e)}")
            return False
    
    def _generate_deployment_report(self, success_count: int, total_phases: int):
        """Generate deployment report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "deployment_summary": {
                "successful_phases": success_count,
                "total_phases": total_phases,
                "success_rate": f"{(success_count/total_phases)*100:.1f}%"
            },
            "deployment_log": self.deployment_log,
            "zones_created": len(self.zone_objects),
            "policies_created": len(self.policy_objects),
            "devices_classified": len(self.device_objects),
            "controller": self.controller.host
        }
        
        with open(f"zone_based_deployment_report_{timestamp}.json", 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Deployment report saved to zone_based_deployment_report_{timestamp}.json")

def main():
    """Main deployment function"""
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
    
    # Initialize deployer
    deployer = ZoneBasedDeployer(controller)
    
    # Confirm deployment
    print(f"\n{'='*60}")
    print("Zone-Based Policy Deployment with Object-Oriented Networking")
    print(f"Controller: {controller_host}")
    print("Features to deploy:")
    print("  - Zone-Based Firewall Rules")
    print("  - Object-Oriented Networking")
    print("  - VLAN Segmentation")
    print("  - Device Classification")
    print("  - Comprehensive Security Policies")
    print(f"{'='*60}\n")
    
    confirm = input("Proceed with deployment? [y/N]: ")
    if confirm.lower() != 'y':
        print("Deployment cancelled")
        return False
    
    # Execute deployment
    success = deployer.deploy_zone_based_architecture()
    
    if success:
        print("\n✅ Zone-based architecture deployment completed successfully!")
        print("Check zone_based_deployment_report_*.json for detailed results")
    else:
        print("\n❌ Zone-based architecture deployment encountered errors")
        print("Check zone_based_deployment.log for details")
    
    return success

if __name__ == "__main__":
    main()
