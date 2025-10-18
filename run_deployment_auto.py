#!/usr/bin/env python3
"""
Automated Network Deployment Script
Runs the comprehensive deployment with automatic approval for cleanup
"""

import os
import sys
import json
from comprehensive_network_deployment import ComprehensiveNetworkDeployer
from enhanced_unifi_controller import EnhancedUniFiController

def main():
    """Main function for automated deployment"""
    print(f"\n{'='*80}")
    print("Automated Network Deployment")
    print(f"{'='*80}")
    print("This will run the comprehensive deployment with automatic")
    print("approval for cleanup of conflicting objects.")
    print(f"{'='*80}\n")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("❌ Error: python-dotenv not installed")
        return False
    
    # Get credentials
    controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', '192.168.22.194')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    username = os.getenv('UNIFI_USERNAME_MARS', 'root')
    password = os.getenv('UNIFI_PASSWORD_MARS')
    
    if not api_key:
        print("❌ Error: UNIFI_API_KEY_MARS not set in .env file")
        return False
    
    print(f"Controller: {controller_host}")
    print(f"API Key: {'✓ Set' if api_key else '❌ Missing'}")
    print()
    
    try:
        # Initialize controller
        print("Initializing UniFi Controller...")
        controller = EnhancedUniFiController()
        
        if not controller.authenticate():
            print("❌ Failed to authenticate with UniFi Controller")
            return False
        
        print("✅ Successfully authenticated with UniFi Controller")
        
        # Initialize deployer
        print("Initializing Comprehensive Deployer...")
        deployer = ComprehensiveNetworkDeployer(controller)
        
        # Run deployment
        print("\nStarting comprehensive deployment...")
        print("This includes:")
        print("  • Phase 0: Pre-deployment Cleanup (with auto-approval)")
        print("  • Phase 1: Initial Assessment")
        print("  • Phase 2: Network Infrastructure")
        print("  • Phase 3: Zone-Based Security")
        print("  • Phase 4: Object-Oriented Networking")
        print("  • Phase 5: Policy Management")
        print("  • Phase 6: Monitoring and Validation")
        print()
        
        success = deployer.execute_comprehensive_deployment()
        
        if success:
            print(f"\n{'='*80}")
            print("✅ DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print(f"{'='*80}")
            print("Your network has been enhanced with:")
            print("  ✓ Zone-Based Firewall Rules")
            print("  ✓ Object-Oriented Networking")
            print("  ✓ Enhanced VLAN Segmentation")
            print("  ✓ Advanced Device Classification")
            print("  ✓ Comprehensive Policy Management")
            print("  ✓ Monitoring and Validation")
            print(f"{'='*80}")
            print("Check the deployment logs for detailed information.")
            print("Your network is now ready for production use!")
        else:
            print(f"\n{'='*80}")
            print("❌ DEPLOYMENT FAILED")
            print(f"{'='*80}")
            print("Please check the logs for error details.")
            print("You may need to run cleanup manually or check connectivity.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
