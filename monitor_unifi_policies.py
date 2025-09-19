#!/usr/bin/env python3
"""
UniFi Network Policy Monitoring and Validation Script
Monitors and validates deployed policies on Mars controller

Requirements:
- pip install requests urllib3 python-dotenv tabulate
"""

import os
import json
import requests
import time
import logging
from typing import Dict, List, Any, Optional
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta
from tabulate import tabulate

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unifi_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UniFiMonitor:
    """Monitor UniFi Controller status and policies"""
    
    def __init__(self, host: str, username: str, password: str, api_key: str, port: int = 443):
        self.host = host
        self.username = username
        self.password = password
        self.api_key = api_key
        self.port = port
        self.base_url = f"https://{host}:{port}"
        self.session = requests.Session()
        self.session.verify = False
        self.site = "default"
        
    def authenticate(self) -> bool:
        """Authenticate with UniFi Controller"""
        try:
            if self.api_key:
                self.session.headers.update({
                    'X-API-Key': self.api_key,
                    'Content-Type': 'application/json'
                })
                
                response = self.session.get(f"{self.base_url}/api/self")
                if response.status_code == 200:
                    logger.info("Successfully authenticated with API key")
                    return True
            
            # Fallback to username/password
            login_data = {
                "username": self.username,
                "password": self.password,
                "remember": True,
                "strict": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("Successfully authenticated with credentials")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        try:
            response = self.session.get(f"{self.base_url}/api/s/{self.site}/stat/sysinfo")
            if response.status_code == 200:
                return response.json().get('data', [{}])[0]
            return {}
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {}
    
    def get_networks(self) -> List[Dict]:
        """Get configured networks"""
        try:
            response = self.session.get(f"{self.base_url}/api/s/{self.site}/rest/networkconf")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting networks: {str(e)}")
            return []
    
    def get_firewall_groups(self) -> List[Dict]:
        """Get firewall groups"""
        try:
            response = self.session.get(f"{self.base_url}/api/s/{self.site}/rest/firewallgroup")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting firewall groups: {str(e)}")
            return []
    
    def get_firewall_rules(self) -> List[Dict]:
        """Get firewall rules"""
        try:
            response = self.session.get(f"{self.base_url}/api/s/{self.site}/rest/firewallrule")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting firewall rules: {str(e)}")
            return []
    
    def get_devices(self) -> List[Dict]:
        """Get connected devices"""
        try:
            response = self.session.get(f"{self.base_url}/api/s/{self.site}/stat/sta")
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logger.error(f"Error getting devices: {str(e)}")
            return []
    
    def get_traffic_stats(self) -> Dict:
        """Get traffic statistics"""
        try:
            # Get last 24 hours of traffic data
            end_time = int(time.time() * 1000)
            start_time = end_time - (24 * 60 * 60 * 1000)  # 24 hours ago
            
            params = {
                'start': start_time,
                'end': end_time,
                'attrs': ['bytes', 'num_sta', 'time']
            }
            
            response = self.session.get(
                f"{self.base_url}/api/s/{self.site}/stat/report/hourly.site",
                params=params
            )
            
            if response.status_code == 200:
                return response.json().get('data', [])
            return {}
        except Exception as e:
            logger.error(f"Error getting traffic stats: {str(e)}")
            return {}
    
    def get_alerts(self, hours: int = 24) -> List[Dict]:
        """Get recent alerts"""
        try:
            response = self.session.get(f"{self.base_url}/api/s/{self.site}/list/alarm")
            if response.status_code == 200:
                alerts = response.json().get('data', [])
                # Filter to last N hours
                cutoff_time = time.time() - (hours * 3600)
                return [alert for alert in alerts if alert.get('time', 0) > cutoff_time]
            return []
        except Exception as e:
            logger.error(f"Error getting alerts: {str(e)}")
            return []

class PolicyValidator:
    """Validate deployed policies against configuration"""
    
    def __init__(self, monitor: UniFiMonitor):
        self.monitor = monitor
        self.validation_results = []
    
    def load_expected_policies(self) -> Dict:
        """Load expected policy configuration"""
        try:
            with open('device-groups-policies.json', 'r') as f:
                device_policies = json.load(f)
            
            with open('firewall-traffic-policies.json', 'r') as f:
                firewall_policies = json.load(f)
            
            return {
                'device_groups': device_policies,
                'firewall': firewall_policies
            }
        except Exception as e:
            logger.error(f"Error loading expected policies: {str(e)}")
            return {}
    
    def validate_networks(self, expected_policies: Dict) -> Dict:
        """Validate network configuration"""
        networks = self.monitor.get_networks()
        device_groups = expected_policies.get('device_groups', {}).get('device_groups', {})
        
        expected_vlans = set()
        for group_config in device_groups.values():
            if 'vlan' in group_config:
                expected_vlans.add(group_config['vlan'])
        
        configured_vlans = set()
        for network in networks:
            if network.get('vlan_enabled') and 'vlan' in network:
                configured_vlans.add(network['vlan'])
        
        missing_vlans = expected_vlans - configured_vlans
        extra_vlans = configured_vlans - expected_vlans
        
        result = {
            'status': 'PASS' if not missing_vlans else 'FAIL',
            'expected_vlans': len(expected_vlans),
            'configured_vlans': len(configured_vlans),
            'missing_vlans': list(missing_vlans),
            'extra_vlans': list(extra_vlans),
            'networks': networks
        }
        
        self.validation_results.append(('Networks', result['status'], f"{len(configured_vlans)}/{len(expected_vlans)} VLANs"))
        return result
    
    def validate_firewall_rules(self, expected_policies: Dict) -> Dict:
        """Validate firewall rules"""
        rules = self.monitor.get_firewall_rules()
        expected_rules = expected_policies.get('firewall', {}).get('object_policies', {})
        
        # Count expected rules
        expected_count = 0
        for policy_group in expected_rules.values():
            if isinstance(policy_group, dict):
                expected_count += len(policy_group)
        
        configured_count = len(rules)
        
        result = {
            'status': 'PARTIAL' if configured_count < expected_count else 'PASS',
            'expected_rules': expected_count,
            'configured_rules': configured_count,
            'rules': rules
        }
        
        self.validation_results.append(('Firewall Rules', result['status'], f"{configured_count}/{expected_count} rules"))
        return result
    
    def validate_device_classification(self) -> Dict:
        """Validate device classification"""
        devices = self.monitor.get_devices()
        networks = self.monitor.get_networks()
        
        # Create VLAN mapping
        vlan_map = {}
        for network in networks:
            if network.get('vlan_enabled'):
                vlan_map[network.get('vlan', 1)] = network.get('name', 'Unknown')
        
        device_distribution = {}
        unclassified_devices = []
        
        for device in devices:
            vlan = device.get('vlan', 1)
            network_name = vlan_map.get(vlan, f'VLAN{vlan}')
            
            if network_name not in device_distribution:
                device_distribution[network_name] = 0
            device_distribution[network_name] += 1
            
            # Check if device appears to be unclassified (on default VLAN)
            if vlan == 1 and device.get('oui') != '24:5A:4C':  # Not UniFi infrastructure
                unclassified_devices.append({
                    'mac': device.get('mac'),
                    'ip': device.get('ip'),
                    'hostname': device.get('hostname', 'Unknown'),
                    'oui': device.get('oui')
                })
        
        result = {
            'status': 'WARN' if unclassified_devices else 'PASS',
            'total_devices': len(devices),
            'device_distribution': device_distribution,
            'unclassified_count': len(unclassified_devices),
            'unclassified_devices': unclassified_devices
        }
        
        self.validation_results.append(('Device Classification', result['status'], f"{len(devices)} devices, {len(unclassified_devices)} unclassified"))
        return result
    
    def generate_report(self) -> Dict:
        """Generate comprehensive validation report"""
        if not self.monitor.authenticate():
            return {'error': 'Authentication failed'}
        
        logger.info("Starting policy validation")
        
        expected_policies = self.load_expected_policies()
        if not expected_policies:
            return {'error': 'Could not load expected policies'}
        
        # Run validations
        system_info = self.monitor.get_system_info()
        network_validation = self.validate_networks(expected_policies)
        firewall_validation = self.validate_firewall_rules(expected_policies)
        device_validation = self.validate_device_classification()
        traffic_stats = self.monitor.get_traffic_stats()
        alerts = self.monitor.get_alerts(24)
        
        # Overall status
        overall_status = 'PASS'
        for _, status, _ in self.validation_results:
            if status == 'FAIL':
                overall_status = 'FAIL'
                break
            elif status in ['WARN', 'PARTIAL']:
                overall_status = 'WARN'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'controller': self.monitor.host,
            'overall_status': overall_status,
            'system_info': system_info,
            'validations': {
                'networks': network_validation,
                'firewall_rules': firewall_validation,
                'device_classification': device_validation
            },
            'traffic_stats': traffic_stats,
            'recent_alerts': alerts,
            'summary': self.validation_results
        }
        
        return report

def print_status_report(report: Dict):
    """Print formatted status report"""
    print(f"\\n{'='*80}")
    print(f"UniFi Network Policy Status Report")
    print(f"Controller: {report.get('controller', 'Unknown')}")
    print(f"Generated: {report.get('timestamp', 'Unknown')}")
    print(f"Overall Status: {report.get('overall_status', 'Unknown')}")
    print(f"{'='*80}")
    
    # System Information
    if 'system_info' in report:
        sys_info = report['system_info']
        print(f"\\n📊 System Information:")
        print(f"  Version: {sys_info.get('version', 'Unknown')}")
        print(f"  Uptime: {sys_info.get('uptime', 'Unknown')} seconds")
        print(f"  Load Average: {sys_info.get('loadavg_1', 'Unknown')}")
    
    # Validation Summary
    if 'summary' in report:
        print(f"\\n🔍 Validation Summary:")
        table_data = []
        for component, status, details in report['summary']:
            status_emoji = {'PASS': '✅', 'FAIL': '❌', 'WARN': '⚠️', 'PARTIAL': '🔶'}.get(status, '❓')
            table_data.append([component, f"{status_emoji} {status}", details])
        
        print(tabulate(table_data, headers=['Component', 'Status', 'Details'], tablefmt='grid'))
    
    # Device Classification
    if 'device_classification' in report.get('validations', {}):
        dev_val = report['validations']['device_classification']
        print(f"\\n📱 Device Distribution:")
        
        if dev_val.get('device_distribution'):
            dist_table = []
            for network, count in dev_val['device_distribution'].items():
                dist_table.append([network, count])
            print(tabulate(dist_table, headers=['Network', 'Device Count'], tablefmt='simple'))
        
        if dev_val.get('unclassified_devices'):
            print(f"\\n⚠️  Unclassified Devices ({len(dev_val['unclassified_devices'])}):")
            unclass_table = []
            for device in dev_val['unclassified_devices'][:10]:  # Show first 10
                unclass_table.append([
                    device.get('hostname', 'Unknown'),
                    device.get('ip', 'Unknown'),
                    device.get('mac', 'Unknown')
                ])
            print(tabulate(unclass_table, headers=['Hostname', 'IP', 'MAC'], tablefmt='simple'))
    
    # Recent Alerts
    if report.get('recent_alerts'):
        print(f"\\n🚨 Recent Alerts ({len(report['recent_alerts'])}):")
        alert_table = []
        for alert in report['recent_alerts'][:5]:  # Show first 5
            alert_time = datetime.fromtimestamp(alert.get('time', 0)).strftime('%Y-%m-%d %H:%M')
            alert_table.append([
                alert_time,
                alert.get('key', 'Unknown'),
                alert.get('msg', 'Unknown')[:50] + '...' if len(alert.get('msg', '')) > 50 else alert.get('msg', 'Unknown')
            ])
        print(tabulate(alert_table, headers=['Time', 'Type', 'Message'], tablefmt='simple'))
    
    print(f"\\n{'='*80}\\n")

def main():
    """Main monitoring function"""
    # Load configuration from environment variables
    controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', 'mars.int.bozza.au')
    username = os.getenv('UNIFI_USERNAME_MARS', 'root')
    password = os.getenv('UNIFI_PASSWORD_MARS')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    if not password and not api_key:
        logger.error("No authentication credentials provided")
        return False
    
    # Initialize monitor
    monitor = UniFiMonitor(
        host=controller_host,
        username=username,
        password=password,
        api_key=api_key
    )
    
    # Initialize validator
    validator = PolicyValidator(monitor)
    
    # Generate report
    report = validator.generate_report()
    
    if 'error' in report:
        print(f"Error: {report['error']}")
        return False
    
    # Print status report
    print_status_report(report)
    
    # Save detailed report
    report_filename = f"policy_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"📄 Detailed report saved to: {report_filename}")
    
    return report.get('overall_status') in ['PASS', 'WARN']

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)