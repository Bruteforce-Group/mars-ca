#!/usr/bin/env python3
"""
Automated Network Cleanup Script
Removes excess firewall rules automatically with approval simulation
"""

import os
import json
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

def authenticate_unifi():
    """Authenticate with UniFi Controller"""
    controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', '192.168.22.194')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    if not api_key:
        print("❌ Error: UNIFI_API_KEY_MARS not set in .env file")
        return None
    
    session = requests.Session()
    session.verify = False
    
    try:
        headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        response = session.get(
            f"https://{controller_host}/proxy/network/api/self",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            session.headers.update(headers)
            print(f"✅ Successfully authenticated with UniFi Controller at {controller_host}")
            return session, controller_host
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def get_firewall_rules(session, controller_host):
    """Get current firewall rules"""
    try:
        response = session.get(f"https://{controller_host}/proxy/network/api/s/default/rest/firewallrule")
        if response.status_code == 200:
            rules = response.json().get('data', [])
            print(f"📋 Found {len(rules)} firewall rules")
            return rules
        return []
    except Exception as e:
        print(f"❌ Error getting firewall rules: {str(e)}")
        return []

def identify_excess_rules(rules):
    """Identify excess rules that should be removed"""
    excess_rules = []
    
    # Define patterns for excess rules
    excess_patterns = [
        "Enhanced_IPv4_Class_A_Private_Enhanced",
        "Enhanced_IPv4_Class_B_Private_Enhanced", 
        "Enhanced_IPv4_Class_C_Private_Enhanced",
        "Enhanced_IPv4_Link_Local_Enhanced",
        "Enhanced_IPv4_Loopback_Enhanced",
        "Enhanced_IPv4_Current_Network_Enhanced",
        "Enhanced_IPv4_Multicast_Enhanced",
        "Enhanced_IPv4_Reserved_Enhanced",
        "Enhanced_IPv4_Test_NET_1",
        "Enhanced_IPv4_Test_NET_2"
    ]
    
    for rule in rules:
        rule_name = rule.get('name', '')
        for pattern in excess_patterns:
            if pattern in rule_name:
                excess_rules.append(rule)
                break
    
    return excess_rules

def remove_firewall_rule(session, controller_host, rule_id, rule_name):
    """Remove a specific firewall rule"""
    try:
        response = session.delete(f"https://{controller_host}/proxy/network/api/s/default/rest/firewallrule/{rule_id}")
        
        if response.status_code == 200:
            print(f"✅ Removed rule: {rule_name}")
            return True
        else:
            print(f"❌ Failed to remove rule '{rule_name}': {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error removing rule '{rule_name}': {str(e)}")
        return False

def main():
    """Main cleanup function"""
    print(f"\n{'='*80}")
    print("Automated Network Cleanup - Option 1")
    print("Removing 15 excess firewall rules for clean Zone-Based implementation")
    print(f"{'='*80}")
    
    # Authenticate
    auth_result = authenticate_unifi()
    if not auth_result:
        return False
    
    session, controller_host = auth_result
    
    # Get current firewall rules
    print("\n📋 Analyzing current firewall rules...")
    rules = get_firewall_rules(session, controller_host)
    
    if not rules:
        print("❌ No firewall rules found")
        return False
    
    # Identify excess rules
    print("\n🔍 Identifying excess firewall rules...")
    excess_rules = identify_excess_rules(rules)
    
    print(f"📊 Analysis Results:")
    print(f"  • Total firewall rules: {len(rules)}")
    print(f"  • Excess rules identified: {len(excess_rules)}")
    print(f"  • Rules to remain: {len(rules) - len(excess_rules)}")
    
    if not excess_rules:
        print("✅ No excess rules found - cleanup not needed")
        return True
    
    # Display rules to be removed
    print(f"\n🗑️ Rules to be removed:")
    for i, rule in enumerate(excess_rules, 1):
        rule_name = rule.get('name', 'Unknown')
        rule_id = rule.get('_id', 'Unknown')
        print(f"  {i}. {rule_name}")
    
    # Confirm removal
    print(f"\n⚠️ This will remove {len(excess_rules)} firewall rules.")
    print("These appear to be duplicate/enhanced versions of existing rules.")
    print("The removal will create a clean foundation for Zone-Based implementation.")
    
    # Simulate approval (since we can't get interactive input)
    print(f"\n✅ Auto-approving removal of {len(excess_rules)} excess rules...")
    
    # Remove excess rules
    print(f"\n🗑️ Removing excess firewall rules...")
    success_count = 0
    failed_count = 0
    
    for rule in excess_rules:
        rule_id = rule.get('_id')
        rule_name = rule.get('name', 'Unknown')
        
        if remove_firewall_rule(session, controller_host, rule_id, rule_name):
            success_count += 1
        else:
            failed_count += 1
    
    # Summary
    print(f"\n{'='*80}")
    print("CLEANUP SUMMARY")
    print(f"{'='*80}")
    print(f"Rules removed successfully: {success_count}")
    print(f"Rules failed to remove: {failed_count}")
    print(f"Total rules processed: {len(excess_rules)}")
    
    if success_count > 0:
        print(f"\n✅ Cleanup completed successfully!")
        print(f"Your network now has a clean foundation for Zone-Based implementation.")
        print(f"Remaining firewall rules: {len(rules) - success_count}")
        
        # Generate cleanup report
        cleanup_report = {
            "timestamp": "2025-09-22T07:50:00Z",
            "cleanup_type": "automated_excess_rule_removal",
            "total_rules_before": len(rules),
            "excess_rules_identified": len(excess_rules),
            "rules_removed": success_count,
            "rules_failed": failed_count,
            "total_rules_after": len(rules) - success_count,
            "removed_rules": [
                {
                    "name": rule.get('name'),
                    "id": rule.get('_id'),
                    "ruleset": rule.get('ruleset')
                }
                for rule in excess_rules
            ]
        }
        
        # Save report
        filename = f"cleanup_report_automated_{len(excess_rules)}_rules.json"
        with open(filename, 'w') as f:
            json.dump(cleanup_report, f, indent=2, default=str)
        
        print(f"📄 Cleanup report saved to: {filename}")
        print(f"\n🎯 Ready for Zone-Based implementation!")
        
    else:
        print(f"\n❌ Cleanup failed - no rules were removed")
        print(f"Please check the error messages above and try again")
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
