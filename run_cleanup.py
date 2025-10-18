#!/usr/bin/env python3
"""
Standalone Network Cleanup Script
Run this to analyze and clean up existing network objects before deployment
"""

import os
import sys
from network_cleanup_manager import NetworkCleanupManager

def main():
    """Main function for standalone cleanup"""
    print(f"\n{'='*80}")
    print("Standalone Network Cleanup Tool")
    print(f"{'='*80}")
    print("This tool will analyze your existing UniFi network configuration")
    print("and provide options to clean up objects that may conflict with")
    print("the new Zone-Based architecture and Object-Oriented Networking.")
    print(f"{'='*80}")
    print("IMPORTANT SAFETY NOTES:")
    print("  • This tool can remove VLANs, firewall groups, and rules")
    print("  • Always backup your configuration before proceeding")
    print("  • You will be asked to approve each removal")
    print("  • The tool will show you exactly what will be removed")
    print("  • You can skip any cleanup if you prefer")
    print(f"{'='*80}\n")
    
    # Check if we're in the right directory
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found")
        print("Please run this script from the project directory")
        return False
    
    # Check if credentials are set
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS')
        api_key = os.getenv('UNIFI_API_KEY_MARS')
        
        if not controller_host or not api_key:
            print("❌ Error: Missing credentials in .env file")
            print("Please ensure UNIFI_CONTROLLER_HOSTNAME_MARS and UNIFI_API_KEY_MARS are set")
            return False
            
    except ImportError:
        print("❌ Error: python-dotenv not installed")
        print("Please run: pip install python-dotenv")
        return False
    
    print(f"Controller: {controller_host}")
    print(f"API Key: {'✓ Set' if api_key else '❌ Missing'}")
    print()
    
    # Initialize cleanup manager
    manager = NetworkCleanupManager()
    
    # Run cleanup analysis and execution
    try:
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
        
        total_to_remove = sum(
            len(approval.get("objects", [])) 
            for approval in cleanup_approvals.values() 
            if approval.get("approved")
        )
        
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
                    print("\nYour network is now ready for Zone-Based deployment!")
                else:
                    print(f"\n❌ Cleanup encountered errors")
                    print("Check network_cleanup.log for details")
            else:
                print("❌ Cleanup cancelled by user")
                print("You can run the deployment without cleanup, but conflicts may occur")
        else:
            print("✅ No cleanup needed - your network is ready for enhancement!")
            print("You can proceed directly to the comprehensive deployment")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n❌ Cleanup cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
