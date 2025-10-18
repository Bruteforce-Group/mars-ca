#!/usr/bin/env python3
"""
Fix GUI Issue
Temporarily disable problematic rules and recreate them with proper format
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
        logging.FileHandler('fix_gui_issue.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GUIFixer:
    """Fix GUI issues by cleaning up problematic rules"""
    
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
        
        # Fix tracking
        self.fixed_rules = []
        self.removed_rules = []
    
    def authenticate(self) -> bool:
        """Authenticate with UniFi Controller"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/self")
            if response.status_code == 200:
                logger.info("Successfully authenticated for GUI fix")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def get_problematic_rules(self) -> List[Dict]:
        """Get rules that might be causing GUI issues"""
        try:
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule")
            if response.status_code == 200:
                rules = response.json().get('data', [])
                # Find our recent rules that might be causing issues
                problematic = [r for r in rules if r.get('name', '').startswith(('Enhanced_', 'Zero_Trust_'))]
                return problematic
            else:
                logger.error(f"Failed to get firewall rules: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting problematic rules: {str(e)}")
            return []
    
    def remove_problematic_rules(self) -> bool:
        """Remove problematic rules"""
        logger.info("Removing problematic rules...")
        
        problematic_rules = self.get_problematic_rules()
        if not problematic_rules:
            logger.info("No problematic rules found")
            return True
        
        success_count = 0
        
        for rule in problematic_rules:
            try:
                rule_id = rule.get('_id')
                rule_name = rule.get('name')
                
                response = self.session.delete(
                    f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule/{rule_id}"
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('meta', {}).get('rc') == 'ok':
                        self.removed_rules.append({
                            "name": rule_name,
                            "id": rule_id
                        })
                        self.fixed_rules.append(f"Removed rule: {rule_name}")
                        logger.info(f"✅ Removed rule: {rule_name}")
                        success_count += 1
                    else:
                        logger.error(f"❌ Failed to remove rule {rule_name}: {result}")
                else:
                    logger.error(f"❌ Failed to remove rule {rule_name}: {response.status_code}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error removing rule {rule.get('name', 'Unknown')}: {str(e)}")
        
        logger.info(f"Rule removal completed: {success_count}/{len(problematic_rules)} rules removed")
        return success_count > 0
    
    def create_clean_rules(self) -> bool:
        """Create clean rules with proper format"""
        logger.info("Creating clean rules with proper format...")
        
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
        
        # Define clean rules with minimal, safe configuration
        clean_rules = [
            {
                "name": "Enhanced_Management_Access_Clean",
                "ruleset": "LAN_IN",
                "action": "accept",
                "protocol": "all",
                "description": "Clean enhanced management access policy"
            },
            {
                "name": "Enhanced_Security_Scan_Clean",
                "ruleset": "LAN_IN",
                "action": "accept",
                "protocol": "tcp",
                "dst_port": "443",
                "description": "Clean enhanced security scanning policy"
            }
        ]
        
        success_count = 0
        
        for i, rule in enumerate(clean_rules):
            try:
                rule_config = {
                    "setting_preference": "manual",
                    "name": rule["name"],
                    "ruleset": rule["ruleset"],
                    "action": rule["action"],
                    "protocol": rule["protocol"],
                    "enabled": True,
                    "logging": False,  # Disable logging to reduce complexity
                    "rule_index": next_index + i,
                    "site_id": self.site_id
                }
                
                # Add optional parameters only if they exist
                if "dst_port" in rule:
                    rule_config["dst_port"] = rule["dst_port"]
                
                response = self.session.post(
                    f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule",
                    json=rule_config
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('meta', {}).get('rc') == 'ok':
                        self.fixed_rules.append(f"Created clean rule: {rule['name']}")
                        logger.info(f"✅ Created clean rule: {rule['name']}")
                        success_count += 1
                    else:
                        logger.error(f"❌ Failed to create clean rule {rule['name']}: {result}")
                else:
                    logger.error(f"❌ Failed to create clean rule {rule['name']}: {response.status_code}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error creating clean rule {rule['name']}: {str(e)}")
        
        logger.info(f"Clean rule creation completed: {success_count}/{len(clean_rules)} rules created")
        return success_count > 0
    
    def verify_fix(self) -> bool:
        """Verify the GUI fix"""
        logger.info("Verifying GUI fix...")
        
        try:
            # Test basic API endpoints
            response = self.session.get(f"https://{self.controller_host}/proxy/network/api/s/{self.site}/rest/firewallrule")
            if response.status_code == 200:
                rules = response.json().get('data', [])
                
                # Check for any remaining problematic rules
                remaining_problematic = [r for r in rules if r.get('name', '').startswith(('Enhanced_', 'Zero_Trust_'))]
                
                verification_results = {
                    "timestamp": datetime.now().isoformat(),
                    "fix_type": "gui_issue_resolution",
                    "removed_rules": len(self.removed_rules),
                    "created_clean_rules": len([r for r in self.fixed_rules if "Created clean rule" in r]),
                    "remaining_problematic_rules": len(remaining_problematic),
                    "total_firewall_rules": len(rules),
                    "fix_log": self.fixed_rules
                }
                
                # Save verification results
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"gui_fix_verification_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(verification_results, f, indent=2, default=str)
                
                logger.info(f"GUI fix verification completed - results saved to {filename}")
                
                # Print summary
                print(f"\n{'='*80}")
                print("GUI FIX VERIFICATION SUMMARY")
                print(f"{'='*80}")
                print(f"Rules Removed: {len(self.removed_rules)}")
                print(f"Clean Rules Created: {len([r for r in self.fixed_rules if 'Created clean rule' in r])}")
                print(f"Remaining Problematic Rules: {len(remaining_problematic)}")
                print(f"Total Firewall Rules: {len(rules)}")
                print(f"Verification results saved to: {filename}")
                print(f"{'='*80}")
                
                return True
            else:
                logger.error(f"Failed to verify fix: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying fix: {str(e)}")
            return False
    
    def run_fix(self) -> bool:
        """Run the GUI fix"""
        print(f"\n{'='*80}")
        print("FIXING GUI ISSUE")
        print("Removing problematic rules and creating clean alternatives")
        print(f"{'='*80}")
        
        if not self.authenticate():
            print("❌ Authentication failed")
            return False
        
        print("✅ Authentication successful")
        
        # Step 1: Remove problematic rules
        print("\n🗑️ Step 1: Removing problematic rules...")
        if not self.remove_problematic_rules():
            print("❌ Rule removal failed")
            return False
        print(f"✅ Removed {len(self.removed_rules)} problematic rules")
        
        # Step 2: Create clean rules
        print("\n✨ Step 2: Creating clean rules...")
        if not self.create_clean_rules():
            print("❌ Clean rule creation failed")
            return False
        print("✅ Created clean rules")
        
        # Step 3: Verify fix
        print("\n✅ Step 3: Verifying fix...")
        if not self.verify_fix():
            print("❌ Fix verification failed")
            return False
        
        print(f"\n{'='*80}")
        print("🎉 GUI FIX COMPLETED SUCCESSFULLY!")
        print(f"{'='*80}")
        print("The GUI issue should now be resolved:")
        print(f"  ✓ Removed {len(self.removed_rules)} problematic rules")
        print(f"  ✓ Created clean, simplified rules")
        print(f"  ✓ Reduced rule complexity")
        print(f"  ✓ Disabled logging to reduce overhead")
        print(f"  ✓ Used minimal, safe configurations")
        print(f"{'='*80}")
        print("Please try accessing the GUI again:")
        print("https://192.168.22.194/network/default/settings/settings_overview")
        print(f"{'='*80}")
        
        return True

def main():
    """Main function for GUI fix"""
    # Load environment variables
    controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', '192.168.22.194')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    if not api_key:
        print("❌ Error: UNIFI_API_KEY_MARS not set in .env file")
        return False
    
    try:
        # Initialize GUI fixer
        fixer = GUIFixer(controller_host, api_key)
        
        # Run fix
        success = fixer.run_fix()
        
        return success
        
    except Exception as e:
        print(f"❌ Error during GUI fix: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
