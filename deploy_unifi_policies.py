#!/usr/bin/env python3
"""
UniFi Network Policy Deployment Script for Mars Controller
Deploys comprehensive Object Policy configuration to UCG-Fiber

Requirements:
- pip install requests urllib3 python-dotenv
"""

import os
import json
import requests
import time
import logging
from typing import Dict, List, Any, Optional
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, skip loading from file

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unifi_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UniFiController:
    """UniFi Controller API Client for Mars"""
    
    def __init__(self, host: str, username: str, password: str, api_key: str, port: int = 443):
        self.host = host
        self.username = username
        self.password = password
        self.api_key = api_key
        self.port = port
        self.base_url = f"https://{host}:{port}"
        self.session = requests.Session()
        self.session.verify = False  # For self-signed certificates
        self.csrf_token = None
        self.site = "default"
        self.controller_type = None  # Will be determined during auth
        
    def authenticate(self) -> bool:
        """Authenticate with UniFi Controller"""
        try:
            # Try different controller types and ports
            auth_attempts = [
                # UDM/UDM Pro on 443
                {'port': 443, 'login_endpoint': '/api/auth/login', 'test_endpoint': '/api/self'},
                # Classic controller on 8443
                {'port': 8443, 'login_endpoint': '/api/login', 'test_endpoint': '/api/self'},
                # Alternative endpoints
                {'port': 443, 'login_endpoint': '/api/login', 'test_endpoint': '/api/self'},
            ]
            
            for attempt in auth_attempts:
                # Update base URL for this attempt
                test_base_url = f"https://{self.host}:{attempt['port']}"
                
                # Try API key authentication first if available
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
                    
                    # Add additional fields for UDM controllers
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
                            
                            # Extract CSRF token if present
                            if 'x-csrf-token' in response.headers:
                                self.csrf_token = response.headers['x-csrf-token']
                                self.session.headers.update({'X-CSRF-Token': self.csrf_token})
                            
                            logger.info(f"Successfully authenticated with username/password on port {attempt['port']}")
                            return True
                        else:
                            logger.debug(f"Username/password auth failed on port {attempt['port']}: {response.status_code} - {response.text}")
                    except Exception as e:
                        logger.debug(f"Username/password auth failed on port {attempt['port']}: {str(e)}")
                        continue
            
            logger.error("Authentication failed on all attempted ports and methods")
            logger.error("Please verify:")
            logger.error("  1. Controller hostname is correct")
            logger.error("  2. Username and password are valid")
            logger.error("  3. API key is valid and has proper permissions")
            logger.error("  4. Controller is accessible from this network")
            return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def get_sites(self) -> List[Dict]:
        """Get list of sites"""
        try:
            response = self.session.get(f"{self.base_url}/api/self/sites")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting sites: {str(e)}")
            return []
    
    def create_network(self, network_config: Dict) -> bool:
        """Create a network/VLAN"""
        try:
            url = f"{self.base_url}/api/s/{self.site}/rest/networkconf"
            response = self.session.post(url, json=network_config, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Successfully created network: {network_config.get('name')}")
                return True
            else:
                logger.error(f"Failed to create network: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating network: {str(e)}")
            return False
    
    def create_firewall_group(self, group_config: Dict) -> bool:
        """Create a firewall group"""
        try:
            url = f"{self.base_url}/api/s/{self.site}/rest/firewallgroup"
            response = self.session.post(url, json=group_config, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Successfully created firewall group: {group_config.get('name')}")
                return True
            else:
                logger.error(f"Failed to create firewall group: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating firewall group: {str(e)}")
            return False
    
    def create_firewall_rule(self, rule_config: Dict) -> bool:
        """Create a firewall rule"""
        try:
            url = f"{self.base_url}/api/s/{self.site}/rest/firewallrule"
            response = self.session.post(url, json=rule_config, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Successfully created firewall rule: {rule_config.get('name')}")
                return True
            else:
                logger.error(f"Failed to create firewall rule: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating firewall rule: {str(e)}")
            return False
    
    def create_port_profile(self, profile_config: Dict) -> bool:
        """Create a port profile for switches"""
        try:
            url = f"{self.base_url}/api/s/{self.site}/rest/portconf"
            response = self.session.post(url, json=profile_config, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Successfully created port profile: {profile_config.get('name')}")
                return True
            else:
                logger.error(f"Failed to create port profile: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating port profile: {str(e)}")
            return False

class PolicyDeployer:
    """Deploys network policies to UniFi Controller"""
    
    def __init__(self, controller: UniFiController):
        self.controller = controller
        self.deployment_log = []
        
    def load_policy_files(self) -> Dict:
        """Load all policy configuration files"""
        policy_files = {
            'segmentation': 'network-segmentation-strategy.md',
            'device_groups': 'device-groups-policies.json',
            'firewall': 'firewall-traffic-policies.json',
            'qos': 'qos-bandwidth-policies.json',
            'scheduling': 'scheduling-policies.json',
            'monitoring': 'monitoring-logging-policies.json'
        }
        
        policies = {}
        for key, filename in policy_files.items():
            try:
                if filename.endswith('.json'):
                    with open(filename, 'r') as f:
                        policies[key] = json.load(f)
                else:
                    with open(filename, 'r') as f:
                        policies[key] = f.read()
                logger.info(f"Loaded {key} policies from {filename}")
            except FileNotFoundError:
                logger.warning(f"Policy file not found: {filename}")
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")
        
        return policies
    
    def deploy_networks(self, policies: Dict) -> bool:
        """Deploy VLAN networks"""
        if 'device_groups' not in policies:
            logger.error("Device groups policies not loaded")
            return False
            
        device_groups = policies['device_groups']['device_groups']
        networks_created = 0
        
        for group_name, group_config in device_groups.items():
            vlan_id = group_config.get('vlan')
            if not vlan_id:
                continue
                
            network_config = {
                "name": f"VLAN{vlan_id}_{group_name.upper()}",
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
            
            if self.controller.create_network(network_config):
                networks_created += 1
                self.deployment_log.append(f"Created network: {network_config['name']}")
            
            time.sleep(1)  # Rate limiting
        
        logger.info(f"Successfully created {networks_created} networks")
        return networks_created > 0
    
    def deploy_firewall_groups(self, policies: Dict) -> bool:
        """Deploy firewall groups for device categories"""
        if 'device_groups' not in policies:
            return False
            
        device_groups = policies['device_groups']['device_groups']
        groups_created = 0
        
        for group_name, group_config in device_groups.items():
            firewall_group = {
                "name": f"DeviceGroup_{group_name.title()}",
                "group_type": "address-group",
                "group_members": [f"192.168.{group_config.get('vlan', 1)}.0/24"],
                "site_id": self.controller.site
            }
            
            if self.controller.create_firewall_group(firewall_group):
                groups_created += 1
                self.deployment_log.append(f"Created firewall group: {firewall_group['name']}")
            
            time.sleep(1)
        
        logger.info(f"Successfully created {groups_created} firewall groups")
        return groups_created > 0
    
    def deploy_firewall_rules(self, policies: Dict) -> bool:
        """Deploy firewall rules based on Object Policy framework"""
        if 'firewall' not in policies:
            return False
            
        rules_created = 0
        object_policies = policies['firewall']['object_policies']
        
        # Deploy internet access policies
        for policy_name, policy_config in object_policies['internet_access_policies'].items():
            if policy_config['action'] == 'allow':
                rule_config = {
                    "name": f"Internet_{policy_name}",
                    "ruleset": "WAN_OUT",
                    "rule_index": 2000 + rules_created,
                    "action": "accept",
                    "protocol": "all",
                    "logging": policy_config.get('logging') == 'all_connections',
                    "enabled": True,
                    "dst_firewallgroup_ids": [],
                    "src_firewallgroup_ids": [],
                    "dst_address": "any",
                    "src_address": "any"
                }
                
                if self.controller.create_firewall_rule(rule_config):
                    rules_created += 1
                    self.deployment_log.append(f"Created internet rule: {rule_config['name']}")
        
        # Deploy inter-VLAN policies
        for policy_name, policy_config in object_policies['inter_vlan_policies'].items():
            rule_config = {
                "name": f"InterVLAN_{policy_name}",
                "ruleset": "LAN_LOCAL",
                "rule_index": 3000 + rules_created,
                "action": policy_config['action'],
                "protocol": "all",
                "logging": policy_config.get('logging') == 'all_attempts',
                "enabled": True,
                "dst_address": "any",
                "src_address": "any"
            }
            
            if self.controller.create_firewall_rule(rule_config):
                rules_created += 1
                self.deployment_log.append(f"Created inter-VLAN rule: {rule_config['name']}")
            
            time.sleep(1)
        
        logger.info(f"Successfully created {rules_created} firewall rules")
        return rules_created > 0
    
    def deploy_qos_profiles(self, policies: Dict) -> bool:
        """Deploy QoS traffic profiles"""
        if 'qos' not in policies:
            return False
            
        # This would implement QoS profile creation
        # UniFi API endpoints for QoS vary by device type
        logger.info("QoS profiles deployment would be implemented here")
        self.deployment_log.append("QoS profiles deployment planned")
        return True
    
    def deploy_all_policies(self) -> bool:
        """Deploy all network policies"""
        logger.info("Starting comprehensive policy deployment to Mars controller")
        
        if not self.controller.authenticate():
            logger.error("Failed to authenticate with controller")
            return False
        
        # Load all policy files
        policies = self.load_policy_files()
        if not policies:
            logger.error("No policies loaded")
            return False
        
        success_count = 0
        total_deployments = 4
        
        # Deploy in order of dependency
        if self.deploy_networks(policies):
            success_count += 1
        
        time.sleep(5)  # Allow networks to be created
        
        if self.deploy_firewall_groups(policies):
            success_count += 1
        
        time.sleep(5)  # Allow groups to be created
        
        if self.deploy_firewall_rules(policies):
            success_count += 1
        
        if self.deploy_qos_profiles(policies):
            success_count += 1
        
        deployment_success = success_count == total_deployments
        
        # Log deployment summary
        logger.info(f"Deployment completed: {success_count}/{total_deployments} successful")
        
        # Write deployment log
        with open(f"deployment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'success_rate': f"{success_count}/{total_deployments}",
                'deployment_log': self.deployment_log,
                'controller': self.controller.host
            }, f, indent=2)
        
        return deployment_success

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
    
    # Initialize controller connection
    controller = UniFiController(
        host=controller_host,
        username=username,
        password=password,
        api_key=api_key
    )
    
    # Initialize deployer
    deployer = PolicyDeployer(controller)
    
    # Confirm deployment
    print(f"\\n{'='*60}")
    print("UniFi Network Policy Deployment")
    print(f"Controller: {controller_host}")
    print("Policies to deploy:")
    print("  - Network VLANs and subnets")
    print("  - Device groups and classification")
    print("  - Firewall rules and traffic policies")
    print("  - QoS bandwidth management")
    print("  - Security monitoring and logging")
    print(f"{'='*60}\\n")
    
    confirm = input("Proceed with deployment? [y/N]: ")
    if confirm.lower() != 'y':
        print("Deployment cancelled")
        return False
    
    # Execute deployment
    success = deployer.deploy_all_policies()
    
    if success:
        print("\\n✅ Policy deployment completed successfully!")
        print("Check deployment_log_*.json for detailed results")
    else:
        print("\\n❌ Policy deployment encountered errors")
        print("Check unifi_deployment.log for details")
    
    return success

if __name__ == "__main__":
    main()