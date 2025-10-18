#!/usr/bin/env python3
"""
Network Cleanup Manager
Handles removal of existing VLANs, Groups, and Lists with user approval
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
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
        logging.FileHandler('network_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NetworkCleanupManager:
    """Manages cleanup of existing network objects with user approval"""
    
    def __init__(self):
        self.controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', '192.168.22.194')
        self.api_key = os.getenv('UNIFI_API_KEY_MARS')
        self.username = os.getenv('UNIFI_USERNAME_MARS', 'root')
        self.password = os.getenv('UNIFI_PASSWORD_MARS')
        self.session = requests.Session()
        self.session.verify = False
        self.site = "default"
        self.cleanup_log = []
        self.objects_to_remove = {
            "networks": [],
            "firewall_groups": [],
            "firewall_rules": [],
            "port_profiles": [],
            "wifi_networks": []
        }
        
    def authenticate(self) -> bool:
        """Authenticate with UniFi Controller"""
        try:
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
                logger.info("Successfully authenticated for cleanup operations")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def analyze_existing_objects(self) -> Dict[str, Any]:
        """Analyze existing network objects and identify cleanup candidates"""
        logger.info("Analyzing existing network objects...")
        
        if not self.authenticate():
            logger.error("Failed to authenticate with controller")
            return {}
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "networks": [],
            "firewall_groups": [],
            "firewall_rules": [],
            "port_profiles": [],
            "wifi_networks": [],
            "cleanup_recommendations": {},
            "impact_assessment": {}
        }
        
        try:
            # Get networks
            analysis["networks"] = self._get_networks()
            
            # Get firewall groups
            analysis["firewall_groups"] = self._get_firewall_groups()
            
            # Get firewall rules
            analysis["firewall_rules"] = self._get_firewall_rules()
            
            # Get port profiles
            analysis["port_profiles"] = self._get_port_profiles()
            
            # Get WiFi networks
            analysis["wifi_networks"] = self._get_wifi_networks()
            
            # Generate cleanup recommendations
            analysis["cleanup_recommendations"] = self._generate_cleanup_recommendations(analysis)
            
            # Assess impact
            analysis["impact_assessment"] = self._assess_cleanup_impact(analysis)
            
            logger.info("Object analysis completed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing existing objects: {str(e)}")
            return analysis
    
    def _get_networks(self) -> List[Dict[str, Any]]:
        """Get existing networks"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/networkconf")
            if response.status_code == 200:
                networks = response.json().get('data', [])
                # Filter out WAN networks and system networks
                filtered_networks = [
                    n for n in networks 
                    if n.get('purpose') not in ['wan', 'wan2'] and not n.get('attr_hidden_id')
                ]
                logger.info(f"Found {len(filtered_networks)} LAN networks")
                return filtered_networks
            return []
        except Exception as e:
            logger.error(f"Error getting networks: {str(e)}")
            return []
    
    def _get_firewall_groups(self) -> List[Dict[str, Any]]:
        """Get existing firewall groups"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallgroup")
            if response.status_code == 200:
                groups = response.json().get('data', [])
                logger.info(f"Found {len(groups)} firewall groups")
                return groups
            return []
        except Exception as e:
            logger.error(f"Error getting firewall groups: {str(e)}")
            return []
    
    def _get_firewall_rules(self) -> List[Dict[str, Any]]:
        """Get existing firewall rules"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule")
            if response.status_code == 200:
                rules = response.json().get('data', [])
                logger.info(f"Found {len(rules)} firewall rules")
                return rules
            return []
        except Exception as e:
            logger.error(f"Error getting firewall rules: {str(e)}")
            return []
    
    def _get_port_profiles(self) -> List[Dict[str, Any]]:
        """Get existing port profiles"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/portconf")
            if response.status_code == 200:
                profiles = response.json().get('data', [])
                # Filter out default profiles
                filtered_profiles = [
                    p for p in profiles 
                    if not p.get('attr_hidden_id') and not p.get('attr_no_delete')
                ]
                logger.info(f"Found {len(filtered_profiles)} custom port profiles")
                return filtered_profiles
            return []
        except Exception as e:
            logger.error(f"Error getting port profiles: {str(e)}")
            return []
    
    def _get_wifi_networks(self) -> List[Dict[str, Any]]:
        """Get existing WiFi networks"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/wlanconf")
            if response.status_code == 200:
                wifis = response.json().get('data', [])
                logger.info(f"Found {len(wifis)} WiFi networks")
                return wifis
            return []
        except Exception as e:
            logger.error(f"Error getting WiFi networks: {str(e)}")
            return []
    
    def _generate_cleanup_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cleanup recommendations based on analysis"""
        recommendations = {
            "networks": {
                "candidates": [],
                "reason": "",
                "impact": "medium"
            },
            "firewall_groups": {
                "candidates": [],
                "reason": "",
                "impact": "low"
            },
            "firewall_rules": {
                "candidates": [],
                "reason": "",
                "impact": "high"
            },
            "port_profiles": {
                "candidates": [],
                "reason": "",
                "impact": "low"
            },
            "wifi_networks": {
                "candidates": [],
                "reason": "",
                "impact": "high"
            }
        }
        
        # Analyze networks
        networks = analysis.get("networks", [])
        if len(networks) > 10:
            # Too many networks, recommend cleanup
            recommendations["networks"]["candidates"] = [
                {
                    "id": n.get("_id"),
                    "name": n.get("name"),
                    "purpose": n.get("purpose"),
                    "vlan": n.get("vlan"),
                    "reason": "Excessive number of networks - may conflict with new zone-based architecture"
                }
                for n in networks[10:]  # Keep first 10, remove rest
            ]
            recommendations["networks"]["reason"] = f"Found {len(networks)} networks, recommending removal of {len(networks) - 10} excess networks"
            recommendations["networks"]["impact"] = "high"
        
        # Analyze firewall groups
        firewall_groups = analysis.get("firewall_groups", [])
        if len(firewall_groups) > 20:
            recommendations["firewall_groups"]["candidates"] = [
                {
                    "id": g.get("_id"),
                    "name": g.get("name"),
                    "group_type": g.get("group_type"),
                    "reason": "Excessive firewall groups - may conflict with new zone-based groups"
                }
                for g in firewall_groups[20:]  # Keep first 20, remove rest
            ]
            recommendations["firewall_groups"]["reason"] = f"Found {len(firewall_groups)} firewall groups, recommending removal of {len(firewall_groups) - 20} excess groups"
        
        # Analyze firewall rules
        firewall_rules = analysis.get("firewall_rules", [])
        if len(firewall_rules) > 30:
            recommendations["firewall_rules"]["candidates"] = [
                {
                    "id": r.get("_id"),
                    "name": r.get("name"),
                    "ruleset": r.get("ruleset"),
                    "action": r.get("action"),
                    "reason": "Excessive firewall rules - may conflict with new zone-based rules"
                }
                for r in firewall_rules[30:]  # Keep first 30, remove rest
            ]
            recommendations["firewall_rules"]["reason"] = f"Found {len(firewall_rules)} firewall rules, recommending removal of {len(firewall_rules) - 30} excess rules"
        
        # Analyze port profiles
        port_profiles = analysis.get("port_profiles", [])
        if len(port_profiles) > 5:
            recommendations["port_profiles"]["candidates"] = [
                {
                    "id": p.get("_id"),
                    "name": p.get("name"),
                    "reason": "Excessive port profiles - may conflict with new zone-based profiles"
                }
                for p in port_profiles[5:]  # Keep first 5, remove rest
            ]
            recommendations["port_profiles"]["reason"] = f"Found {len(port_profiles)} port profiles, recommending removal of {len(port_profiles) - 5} excess profiles"
        
        return recommendations
    
    def _assess_cleanup_impact(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the impact of cleanup operations"""
        impact = {
            "overall_risk": "low",
            "affected_devices": 0,
            "affected_clients": 0,
            "network_disruption": "minimal",
            "rollback_complexity": "low",
            "recommendations": []
        }
        
        # Count affected objects
        total_objects = (
            len(analysis.get("networks", [])) +
            len(analysis.get("firewall_groups", [])) +
            len(analysis.get("firewall_rules", [])) +
            len(analysis.get("port_profiles", [])) +
            len(analysis.get("wifi_networks", []))
        )
        
        if total_objects > 50:
            impact["overall_risk"] = "high"
            impact["network_disruption"] = "significant"
            impact["rollback_complexity"] = "high"
            impact["recommendations"].append("Consider staged cleanup to minimize disruption")
        elif total_objects > 20:
            impact["overall_risk"] = "medium"
            impact["network_disruption"] = "moderate"
            impact["rollback_complexity"] = "medium"
            impact["recommendations"].append("Backup configuration before cleanup")
        else:
            impact["overall_risk"] = "low"
            impact["network_disruption"] = "minimal"
            impact["rollback_complexity"] = "low"
            impact["recommendations"].append("Cleanup can proceed safely")
        
        return impact
    
    def present_cleanup_options(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Present cleanup options to user for approval"""
        recommendations = analysis.get("cleanup_recommendations", {})
        impact = analysis.get("impact_assessment", {})
        
        print(f"\n{'='*80}")
        print("NETWORK CLEANUP ANALYSIS")
        print(f"{'='*80}")
        print(f"Overall Risk Level: {impact.get('overall_risk', 'Unknown').upper()}")
        print(f"Network Disruption: {impact.get('network_disruption', 'Unknown')}")
        print(f"Rollback Complexity: {impact.get('rollback_complexity', 'Unknown')}")
        print(f"{'='*80}\n")
        
        cleanup_approvals = {}
        
        for object_type, rec in recommendations.items():
            if rec.get("candidates"):
                print(f"\n{object_type.upper().replace('_', ' ')} CLEANUP")
                print(f"{'='*50}")
                print(f"Reason: {rec.get('reason', 'N/A')}")
                print(f"Impact: {rec.get('impact', 'Unknown')}")
                print(f"Objects to remove: {len(rec['candidates'])}")
                print("\nObjects to be removed:")
                
                for i, obj in enumerate(rec['candidates'][:10], 1):  # Show first 10
                    print(f"  {i}. {obj.get('name', 'Unknown')} ({obj.get('reason', 'N/A')})")
                
                if len(rec['candidates']) > 10:
                    print(f"  ... and {len(rec['candidates']) - 10} more")
                
                print(f"\nOptions:")
                print(f"  1. Remove all {len(rec['candidates'])} {object_type}")
                print(f"  2. Remove specific {object_type} (interactive selection)")
                print(f"  3. Skip {object_type} cleanup")
                print(f"  4. View detailed list")
                
                while True:
                    choice = input(f"\nSelect option for {object_type} cleanup (1-4): ").strip()
                    
                    if choice == "1":
                        cleanup_approvals[object_type] = {
                            "action": "remove_all",
                            "objects": rec['candidates'],
                            "approved": True
                        }
                        print(f"✅ Approved removal of all {len(rec['candidates'])} {object_type}")
                        break
                    elif choice == "2":
                        selected_objects = self._interactive_object_selection(rec['candidates'], object_type)
                        if selected_objects:
                            cleanup_approvals[object_type] = {
                                "action": "remove_selected",
                                "objects": selected_objects,
                                "approved": True
                            }
                            print(f"✅ Approved removal of {len(selected_objects)} selected {object_type}")
                        else:
                            print(f"❌ No {object_type} selected for removal")
                        break
                    elif choice == "3":
                        cleanup_approvals[object_type] = {
                            "action": "skip",
                            "objects": [],
                            "approved": False
                        }
                        print(f"⏭️ Skipped {object_type} cleanup")
                        break
                    elif choice == "4":
                        self._display_detailed_list(rec['candidates'], object_type)
                    else:
                        print("Invalid choice. Please select 1-4.")
            else:
                print(f"\n{object_type.upper().replace('_', ' ')} CLEANUP")
                print(f"{'='*50}")
                print("✅ No cleanup needed - within acceptable limits")
                cleanup_approvals[object_type] = {
                    "action": "skip",
                    "objects": [],
                    "approved": False
                }
        
        return cleanup_approvals
    
    def _interactive_object_selection(self, candidates: List[Dict], object_type: str) -> List[Dict]:
        """Interactive selection of objects to remove"""
        print(f"\nSelect {object_type} to remove (enter numbers separated by commas, or 'all' for all):")
        
        for i, obj in enumerate(candidates, 1):
            print(f"  {i}. {obj.get('name', 'Unknown')} - {obj.get('reason', 'N/A')}")
        
        while True:
            selection = input(f"\nEnter selection for {object_type}: ").strip()
            
            if selection.lower() == 'all':
                return candidates
            elif selection.lower() == 'none':
                return []
            else:
                try:
                    indices = [int(x.strip()) - 1 for x in selection.split(',')]
                    selected = [candidates[i] for i in indices if 0 <= i < len(candidates)]
                    if selected:
                        return selected
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter numbers separated by commas.")
    
    def _display_detailed_list(self, candidates: List[Dict], object_type: str):
        """Display detailed list of objects"""
        print(f"\nDetailed list of {object_type} to remove:")
        print(f"{'='*60}")
        
        for i, obj in enumerate(candidates, 1):
            print(f"\n{i}. {obj.get('name', 'Unknown')}")
            print(f"   ID: {obj.get('id', 'N/A')}")
            print(f"   Reason: {obj.get('reason', 'N/A')}")
            if 'purpose' in obj:
                print(f"   Purpose: {obj.get('purpose', 'N/A')}")
            if 'vlan' in obj:
                print(f"   VLAN: {obj.get('vlan', 'N/A')}")
            if 'group_type' in obj:
                print(f"   Type: {obj.get('group_type', 'N/A')}")
            if 'ruleset' in obj:
                print(f"   Ruleset: {obj.get('ruleset', 'N/A')}")
            if 'action' in obj:
                print(f"   Action: {obj.get('action', 'N/A')}")
    
    def execute_cleanup(self, cleanup_approvals: Dict[str, Any]) -> bool:
        """Execute approved cleanup operations"""
        logger.info("Starting cleanup execution...")
        
        if not self.authenticate():
            logger.error("Failed to authenticate for cleanup")
            return False
        
        success_count = 0
        total_operations = 0
        
        for object_type, approval in cleanup_approvals.items():
            if not approval.get("approved", False):
                continue
            
            objects_to_remove = approval.get("objects", [])
            if not objects_to_remove:
                continue
            
            total_operations += len(objects_to_remove)
            
            for obj in objects_to_remove:
                if self._remove_object(object_type, obj):
                    success_count += 1
                    self.cleanup_log.append(f"Removed {object_type}: {obj.get('name', 'Unknown')}")
                else:
                    logger.error(f"Failed to remove {object_type}: {obj.get('name', 'Unknown')}")
                
                time.sleep(0.5)  # Rate limiting
        
        # Generate cleanup report
        self._generate_cleanup_report(success_count, total_operations)
        
        logger.info(f"Cleanup completed: {success_count}/{total_operations} objects removed")
        return success_count > 0
    
    def _remove_object(self, object_type: str, obj: Dict[str, Any]) -> bool:
        """Remove a specific object"""
        try:
            obj_id = obj.get('id')
            if not obj_id:
                logger.error(f"No ID found for {object_type}: {obj.get('name', 'Unknown')}")
                return False
            
            # Map object types to API endpoints
            endpoints = {
                "networks": f"/proxy/network/api/s/{self.site}/rest/networkconf/{obj_id}",
                "firewall_groups": f"/proxy/network/api/s/{self.site}/rest/firewallgroup/{obj_id}",
                "firewall_rules": f"/proxy/network/api/s/{self.site}/rest/firewallrule/{obj_id}",
                "port_profiles": f"/proxy/network/api/s/{self.site}/rest/portconf/{obj_id}",
                "wifi_networks": f"/proxy/network/api/s/{self.site}/rest/wlanconf/{obj_id}"
            }
            
            endpoint = endpoints.get(object_type)
            if not endpoint:
                logger.error(f"Unknown object type: {object_type}")
                return False
            
            response = self.session.delete(f"https://{self.controller_host}{endpoint}")
            
            if response.status_code == 200:
                logger.info(f"Successfully removed {object_type}: {obj.get('name', 'Unknown')}")
                return True
            else:
                logger.error(f"Failed to remove {object_type}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing {object_type}: {str(e)}")
            return False
    
    def _generate_cleanup_report(self, success_count: int, total_operations: int):
        """Generate cleanup report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "cleanup_summary": {
                "successful_removals": success_count,
                "total_attempted": total_operations,
                "success_rate": f"{(success_count/total_operations)*100:.1f}%" if total_operations > 0 else "0%"
            },
            "cleanup_log": self.cleanup_log,
            "controller": self.controller_host
        }
        
        filename = f"cleanup_report_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Cleanup report saved to {filename}")

def main():
    """Main function for network cleanup management"""
    print(f"\n{'='*80}")
    print("Network Cleanup Manager")
    print(f"{'='*80}")
    print("This tool analyzes your existing network configuration and")
    print("provides options to clean up conflicting objects before")
    print("implementing the new Zone-Based architecture.")
    print(f"{'='*80}\n")
    
    # Initialize cleanup manager
    manager = NetworkCleanupManager()
    
    # Analyze existing objects
    analysis = manager.analyze_existing_objects()
    
    if not analysis:
        print("❌ Failed to analyze existing objects")
        return False
    
    # Present cleanup options
    cleanup_approvals = manager.present_cleanup_options(analysis)
    
    # Ask for final confirmation
    print(f"\n{'='*80}")
    print("CLEANUP SUMMARY")
    print(f"{'='*80}")
    
    total_to_remove = sum(len(approval.get("objects", [])) for approval in cleanup_approvals.values() if approval.get("approved"))
    
    if total_to_remove > 0:
        print(f"Total objects to be removed: {total_to_remove}")
        print("\nThis action cannot be undone. Make sure you have:")
        print("  ✓ Backed up your current configuration")
        print("  ✓ Verified the objects to be removed")
        print("  ✓ Planned for any potential network disruption")
        
        confirm = input(f"\nProceed with cleanup of {total_to_remove} objects? [y/N]: ").strip()
        
        if confirm.lower() == 'y':
            success = manager.execute_cleanup(cleanup_approvals)
            if success:
                print(f"\n✅ Cleanup completed successfully!")
                print("Check cleanup_report_*.json for detailed results")
            else:
                print(f"\n❌ Cleanup encountered errors")
                print("Check network_cleanup.log for details")
        else:
            print("❌ Cleanup cancelled by user")
    else:
        print("✅ No cleanup needed - your network is ready for enhancement!")
    
    return True

if __name__ == "__main__":
    main()
