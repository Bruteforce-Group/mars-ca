#!/usr/bin/env python3
"""
Working Network Scan Script
Uses the correct UniFi API endpoints discovered during testing
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
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
        logging.FileHandler('working_network_scan.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WorkingNetworkScanner:
    """Working network scanner using correct UniFi API endpoints"""
    
    def __init__(self):
        self.controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', '192.168.22.194')
        self.api_key = os.getenv('UNIFI_API_KEY_MARS')
        self.username = os.getenv('UNIFI_USERNAME_MARS', 'root')
        self.password = os.getenv('UNIFI_PASSWORD_MARS')
        self.session = requests.Session()
        self.session.verify = False
        self.site = "default"
        self.scan_results = {}
        
    def authenticate(self) -> bool:
        """Authenticate with UniFi Controller using API key"""
        try:
            # Test API key authentication
            headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(
                f"https://{self.controller_host}/proxy/network/api/self",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.session.headers.update(headers)
                logger.info("Successfully authenticated with API key")
                return True
            else:
                logger.error(f"API key authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def perform_network_scan(self) -> Dict[str, Any]:
        """Perform comprehensive network scan"""
        logger.info("Starting network scan...")
        
        if not self.authenticate():
            logger.error("Failed to authenticate with controller")
            return {}
        
        # Initialize scan results
        self.scan_results = {
            "timestamp": datetime.now().isoformat(),
            "controller_info": {},
            "network_topology": {},
            "device_inventory": {},
            "security_analysis": {},
            "implementation_recommendations": {}
        }
        
        try:
            # Get controller information
            self._get_controller_info()
            
            # Get network topology
            self._get_network_topology()
            
            # Get device inventory
            self._get_device_inventory()
            
            # Get security analysis
            self._get_security_analysis()
            
            # Generate implementation recommendations
            self._generate_implementation_recommendations()
            
            # Save results
            self._save_scan_results()
            
            logger.info("Network scan completed successfully")
            return self.scan_results
            
        except Exception as e:
            logger.error(f"Error during network scan: {str(e)}")
            return self.scan_results
    
    def _get_controller_info(self):
        """Get controller information"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/self")
            if response.status_code == 200:
                data = response.json()
                self.scan_results["controller_info"] = {
                    "host": self.controller_host,
                    "name": data.get("name", "Unknown"),
                    "version": data.get("version", "Unknown"),
                    "build": data.get("build", "Unknown"),
                    "uuid": data.get("uuid", "Unknown"),
                    "site_id": data.get("site_id", "default")
                }
                logger.info(f"Controller: {data.get('name', 'Unknown')} v{data.get('version', 'Unknown')}")
            else:
                logger.error(f"Failed to get controller info: {response.status_code}")
        except Exception as e:
            logger.error(f"Error getting controller info: {str(e)}")
    
    def _get_network_topology(self):
        """Get network topology"""
        try:
            # Get networks
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/networkconf")
            if response.status_code == 200:
                networks = response.json().get('data', [])
                self.scan_results["network_topology"] = {
                    "total_networks": len(networks),
                    "networks": networks,
                    "vlan_coverage": [n for n in networks if n.get("vlan_enabled")],
                    "network_segmentation": "flat" if len([n for n in networks if n.get("vlan_enabled")]) == 0 else "segmented"
                }
                logger.info(f"Found {len(networks)} networks")
            else:
                logger.error(f"Failed to get networks: {response.status_code}")
        except Exception as e:
            logger.error(f"Error getting network topology: {str(e)}")
    
    def _get_device_inventory(self):
        """Get device inventory"""
        try:
            # Get devices
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/stat/device")
            if response.status_code == 200:
                devices = response.json().get('data', [])
            else:
                devices = []
                logger.error(f"Failed to get devices: {response.status_code}")
            
            # Get clients
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/stat/sta")
            if response.status_code == 200:
                clients = response.json().get('data', [])
            else:
                clients = []
                logger.error(f"Failed to get clients: {response.status_code}")
            
            self.scan_results["device_inventory"] = {
                "total_devices": len(devices),
                "total_clients": len(clients),
                "devices": devices,
                "clients": clients,
                "device_types": self._analyze_device_types(devices),
                "classification_status": {
                    "classified": len([c for c in clients if c.get("is_wired") or c.get("is_guest")]),
                    "unclassified": len([c for c in clients if not (c.get("is_wired") or c.get("is_guest"))]),
                    "classification_rate": f"{(len([c for c in clients if c.get('is_wired') or c.get('is_guest')]) / max(len(clients), 1) * 100):.1f}%"
                }
            }
            logger.info(f"Found {len(devices)} devices, {len(clients)} clients")
        except Exception as e:
            logger.error(f"Error getting device inventory: {str(e)}")
    
    def _analyze_device_types(self, devices: List[Dict]) -> Dict[str, int]:
        """Analyze device types"""
        device_types = {}
        for device in devices:
            device_type = device.get("type", "unknown")
            device_types[device_type] = device_types.get(device_type, 0) + 1
        return device_types
    
    def _get_security_analysis(self):
        """Get security analysis"""
        try:
            # Get firewall groups
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallgroup")
            if response.status_code == 200:
                firewall_groups = response.json().get('data', [])
            else:
                firewall_groups = []
                logger.error(f"Failed to get firewall groups: {response.status_code}")
            
            # Get firewall rules
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule")
            if response.status_code == 200:
                firewall_rules = response.json().get('data', [])
            else:
                firewall_rules = []
                logger.error(f"Failed to get firewall rules: {response.status_code}")
            
            # Analyze security level
            if len(firewall_rules) == 0:
                security_level = "none"
            elif len(firewall_rules) < 5:
                security_level = "basic"
            elif len(firewall_rules) < 20:
                security_level = "moderate"
            else:
                security_level = "advanced"
            
            self.scan_results["security_analysis"] = {
                "firewall_groups": len(firewall_groups),
                "firewall_rules": len(firewall_rules),
                "security_level": security_level,
                "policy_coverage": {
                    "wan_rules": len([r for r in firewall_rules if r.get("ruleset") == "WAN_OUT"]),
                    "lan_rules": len([r for r in firewall_rules if r.get("ruleset") == "LAN_LOCAL"]),
                    "total_rules": len(firewall_rules)
                }
            }
            logger.info(f"Security level: {security_level} ({len(firewall_rules)} rules)")
        except Exception as e:
            logger.error(f"Error getting security analysis: {str(e)}")
    
    def _generate_implementation_recommendations(self):
        """Generate implementation recommendations"""
        try:
            network_segmentation = self.scan_results.get("network_topology", {}).get("network_segmentation", "flat")
            security_level = self.scan_results.get("security_analysis", {}).get("security_level", "none")
            device_count = self.scan_results.get("device_inventory", {}).get("total_devices", 0)
            client_count = self.scan_results.get("device_inventory", {}).get("total_clients", 0)
            
            # Determine strategy
            if network_segmentation == "flat" and security_level in ["none", "basic"]:
                strategy = "comprehensive_implementation"
                priority = "high"
            else:
                strategy = "enhanced_implementation"
                priority = "medium"
            
            recommendations = {
                "strategy": strategy,
                "priority": priority,
                "estimated_duration": "4-6 hours" if strategy == "comprehensive_implementation" else "2-3 hours",
                "risk_level": "medium-high" if strategy == "comprehensive_implementation" else "medium",
                "phases": self._generate_phases(strategy),
                "device_classification_needed": client_count > 0,
                "vlan_segmentation_needed": network_segmentation == "flat",
                "security_enhancement_needed": security_level in ["none", "basic"],
                "estimated_devices_per_zone": {
                    "management_zone": max(1, device_count // 10),
                    "user_zone": max(1, client_count // 3),
                    "iot_zone": max(1, client_count // 4),
                    "guest_zone": max(1, client_count // 10)
                }
            }
            
            self.scan_results["implementation_recommendations"] = recommendations
            logger.info(f"Generated {strategy} implementation recommendations")
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
    
    def _generate_phases(self, strategy: str) -> List[Dict[str, Any]]:
        """Generate implementation phases"""
        if strategy == "comprehensive_implementation":
            return [
                {
                    "phase": 1,
                    "name": "Network Infrastructure Setup",
                    "description": "Create VLAN networks and basic routing",
                    "duration": "45 minutes",
                    "risk": "low"
                },
                {
                    "phase": 2,
                    "name": "Zone Definition and Assignment",
                    "description": "Define security zones and assign VLANs",
                    "duration": "30 minutes",
                    "risk": "low"
                },
                {
                    "phase": 3,
                    "name": "Device Classification System",
                    "description": "Implement automated device classification",
                    "duration": "60 minutes",
                    "risk": "medium"
                },
                {
                    "phase": 4,
                    "name": "Zone-Based Security Policies",
                    "description": "Deploy comprehensive zone-based firewall rules",
                    "duration": "90 minutes",
                    "risk": "high"
                },
                {
                    "phase": 5,
                    "name": "Object-Oriented Networking",
                    "description": "Implement OON principles and automation",
                    "duration": "45 minutes",
                    "risk": "medium"
                },
                {
                    "phase": 6,
                    "name": "Monitoring and Validation",
                    "description": "Set up monitoring and validate implementation",
                    "duration": "30 minutes",
                    "risk": "low"
                }
            ]
        else:
            return [
                {
                    "phase": 1,
                    "name": "Zone Enhancement",
                    "description": "Enhance existing zones with advanced features",
                    "duration": "30 minutes",
                    "risk": "low"
                },
                {
                    "phase": 2,
                    "name": "Policy Optimization",
                    "description": "Optimize existing policies and add new ones",
                    "duration": "60 minutes",
                    "risk": "medium"
                },
                {
                    "phase": 3,
                    "name": "Object-Oriented Integration",
                    "description": "Integrate Object-Oriented Networking features",
                    "duration": "45 minutes",
                    "risk": "low"
                }
            ]
    
    def _save_scan_results(self):
        """Save scan results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"working_network_scan_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.scan_results, f, indent=2, default=str)
        
        logger.info(f"Scan results saved to {filename}")

def main():
    """Main function for working network scan"""
    print(f"\n{'='*80}")
    print("Working Network Scan - UniFi Controller Analysis")
    print(f"{'='*80}")
    print("This scan will analyze your actual UniFi network configuration")
    print("and generate implementation recommendations for Zone-Based rules")
    print("and Object-Oriented Networking.")
    print(f"{'='*80}\n")
    
    # Initialize scanner
    scanner = WorkingNetworkScanner()
    
    # Perform scan
    scan_results = scanner.perform_network_scan()
    
    if scan_results:
        # Print summary
        print(f"\n{'='*80}")
        print("Network Scan Summary")
        print(f"{'='*80}")
        print(f"Controller: {scan_results.get('controller_info', {}).get('name', 'Unknown')}")
        print(f"Version: {scan_results.get('controller_info', {}).get('version', 'Unknown')}")
        print(f"Networks: {scan_results.get('network_topology', {}).get('total_networks', 0)}")
        print(f"Devices: {scan_results.get('device_inventory', {}).get('total_devices', 0)}")
        print(f"Clients: {scan_results.get('device_inventory', {}).get('total_clients', 0)}")
        print(f"Security Level: {scan_results.get('security_analysis', {}).get('security_level', 'Unknown')}")
        print(f"Network Segmentation: {scan_results.get('network_topology', {}).get('network_segmentation', 'Unknown')}")
        
        recommendations = scan_results.get('implementation_recommendations', {})
        if recommendations:
            print(f"Implementation Strategy: {recommendations.get('strategy', 'Unknown')}")
            print(f"Estimated Duration: {recommendations.get('estimated_duration', 'Unknown')}")
            print(f"Risk Level: {recommendations.get('risk_level', 'Unknown')}")
            print(f"Priority: {recommendations.get('priority', 'Unknown')}")
        
        print(f"{'='*80}")
        
        # Print device analysis
        device_inventory = scan_results.get('device_inventory', {})
        if device_inventory:
            print(f"\nDevice Analysis:")
            print(f"  Total Devices: {device_inventory.get('total_devices', 0)}")
            print(f"  Total Clients: {device_inventory.get('total_clients', 0)}")
            print(f"  Classification Rate: {device_inventory.get('classification_status', {}).get('classification_rate', 'Unknown')}")
            
            device_types = device_inventory.get('device_types', {})
            if device_types:
                print(f"  Device Types:")
                for device_type, count in device_types.items():
                    print(f"    {device_type}: {count}")
        
        # Print security analysis
        security_analysis = scan_results.get('security_analysis', {})
        if security_analysis:
            print(f"\nSecurity Analysis:")
            print(f"  Security Level: {security_analysis.get('security_level', 'Unknown')}")
            print(f"  Firewall Groups: {security_analysis.get('firewall_groups', 0)}")
            print(f"  Firewall Rules: {security_analysis.get('firewall_rules', 0)}")
            
            policy_coverage = security_analysis.get('policy_coverage', {})
            if policy_coverage:
                print(f"  WAN Rules: {policy_coverage.get('wan_rules', 0)}")
                print(f"  LAN Rules: {policy_coverage.get('lan_rules', 0)}")
        
        # Print implementation phases
        phases = recommendations.get('phases', [])
        if phases:
            print(f"\nImplementation Phases:")
            for phase in phases:
                print(f"  Phase {phase['phase']}: {phase['name']}")
                print(f"    Duration: {phase['duration']}")
                print(f"    Risk: {phase['risk']}")
                print(f"    Description: {phase['description']}")
        
        print(f"\n{'='*80}")
        print("Network scan completed successfully!")
        print(f"Check working_network_scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json for detailed results")
        print(f"{'='*80}\n")
    else:
        print("❌ Network scan failed. Check the logs for details.")

if __name__ == "__main__":
    main()
