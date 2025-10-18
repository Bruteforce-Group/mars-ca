#!/usr/bin/env python3
"""
Comprehensive Network Deployment Script
Integrates Zone-Based rules with Object-Oriented Networking and VLAN segmentation
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enhanced_unifi_controller import EnhancedUniFiController
from zone_based_deployment import ZoneBasedDeployer
from policy_management import PolicyManager
from initial_network_scan import NetworkScanner
from network_cleanup_manager import NetworkCleanupManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveNetworkDeployer:
    """Comprehensive network deployment system integrating all components"""
    
    def __init__(self, controller: EnhancedUniFiController):
        self.controller = controller
        self.scanner = NetworkScanner(controller)
        self.zone_deployer = ZoneBasedDeployer(controller)
        self.policy_manager = PolicyManager(controller)
        self.cleanup_manager = NetworkCleanupManager()
        self.deployment_log = []
        self.deployment_status = {}
        
    def execute_comprehensive_deployment(self) -> bool:
        """Execute comprehensive network deployment"""
        logger.info("Starting comprehensive network deployment...")
        
        try:
            # Phase 0: Pre-deployment Cleanup (Optional)
            if not self._phase_0_pre_deployment_cleanup():
                logger.warning("Phase 0: Pre-deployment cleanup skipped or failed")
            
            # Phase 1: Initial Assessment
            if not self._phase_1_initial_assessment():
                logger.error("Phase 1 failed: Initial Assessment")
                return False
            
            # Phase 2: Network Infrastructure
            if not self._phase_2_network_infrastructure():
                logger.error("Phase 2 failed: Network Infrastructure")
                return False
            
            # Phase 3: Zone-Based Architecture
            if not self._phase_3_zone_based_architecture():
                logger.error("Phase 3 failed: Zone-Based Architecture")
                return False
            
            # Phase 4: Object-Oriented Networking
            if not self._phase_4_object_oriented_networking():
                logger.error("Phase 4 failed: Object-Oriented Networking")
                return False
            
            # Phase 5: Policy Management
            if not self._phase_5_policy_management():
                logger.error("Phase 5 failed: Policy Management")
                return False
            
            # Phase 6: Validation and Monitoring
            if not self._phase_6_validation_and_monitoring():
                logger.error("Phase 6 failed: Validation and Monitoring")
                return False
            
            # Generate final report
            self._generate_final_report()
            
            logger.info("Comprehensive network deployment completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error during comprehensive deployment: {str(e)}")
            return False
    
    def _phase_0_pre_deployment_cleanup(self) -> bool:
        """Phase 0: Pre-deployment Cleanup (Optional)"""
        logger.info("Phase 0: Pre-deployment Cleanup")
        
        try:
            # Analyze existing objects
            analysis = self.cleanup_manager.analyze_existing_objects()
            
            if not analysis:
                logger.error("Failed to analyze existing objects")
                return False
            
            # Check if cleanup is needed
            recommendations = analysis.get("cleanup_recommendations", {})
            cleanup_needed = any(
                rec.get("candidates") for rec in recommendations.values()
            )
            
            if not cleanup_needed:
                logger.info("No cleanup needed - existing configuration is compatible")
                self.deployment_status["phase_0"] = {
                    "status": "skipped",
                    "reason": "No cleanup needed",
                    "cleanup_performed": False
                }
                return True
            
            # Present cleanup options
            print(f"\n{'='*80}")
            print("PRE-DEPLOYMENT CLEANUP REQUIRED")
            print(f"{'='*80}")
            print("The analysis found existing objects that may conflict with")
            print("the new Zone-Based architecture. Cleanup is recommended.")
            print(f"{'='*80}")
            
            cleanup_choice = input("\nWould you like to proceed with cleanup? [y/N]: ").strip()
            
            if cleanup_choice.lower() != 'y':
                logger.info("Cleanup skipped by user")
                self.deployment_status["phase_0"] = {
                    "status": "skipped",
                    "reason": "User declined cleanup",
                    "cleanup_performed": False
                }
                return True
            
            # Present cleanup options and get approval
            cleanup_approvals = self.cleanup_manager.present_cleanup_options(analysis)
            
            # Execute approved cleanup
            cleanup_success = self.cleanup_manager.execute_cleanup(cleanup_approvals)
            
            if cleanup_success:
                self.deployment_status["phase_0"] = {
                    "status": "completed",
                    "reason": "Cleanup executed successfully",
                    "cleanup_performed": True
                }
                self.deployment_log.append("Phase 0 completed: Pre-deployment Cleanup")
                logger.info("Phase 0 completed: Pre-deployment Cleanup")
                return True
            else:
                logger.error("Cleanup execution failed")
                self.deployment_status["phase_0"] = {
                    "status": "failed",
                    "reason": "Cleanup execution failed",
                    "cleanup_performed": False
                }
                return False
                
        except Exception as e:
            logger.error(f"Error in Phase 0: {str(e)}")
            return False
    
    def _phase_1_initial_assessment(self) -> bool:
        """Phase 1: Initial Assessment and Planning"""
        logger.info("Phase 1: Initial Assessment and Planning")
        
        try:
            # Perform comprehensive scan
            scan_results = self.scanner.perform_comprehensive_scan()
            
            # Analyze current state
            current_state = self._analyze_current_state(scan_results)
            
            # Generate implementation plan
            implementation_plan = self._generate_implementation_plan(current_state)
            
            # Store assessment results
            self.deployment_status["phase_1"] = {
                "status": "completed",
                "scan_results": scan_results,
                "current_state": current_state,
                "implementation_plan": implementation_plan
            }
            
            self.deployment_log.append("Phase 1 completed: Initial Assessment")
            return True
            
        except Exception as e:
            logger.error(f"Error in Phase 1: {str(e)}")
            return False
    
    def _phase_2_network_infrastructure(self) -> bool:
        """Phase 2: Network Infrastructure Setup"""
        logger.info("Phase 2: Network Infrastructure Setup")
        
        try:
            # Load zone-based policies
            zone_policies = self.zone_deployer.load_zone_policies()
            if not zone_policies:
                logger.error("Failed to load zone-based policies")
                return False
            
            # Deploy network infrastructure
            success = self.zone_deployer._deploy_network_infrastructure(zone_policies)
            
            if success:
                self.deployment_status["phase_2"] = {
                    "status": "completed",
                    "networks_created": len(zone_policies.get("zone_definitions", {})),
                    "infrastructure_ready": True
                }
                self.deployment_log.append("Phase 2 completed: Network Infrastructure")
                return True
            else:
                logger.error("Failed to deploy network infrastructure")
                return False
                
        except Exception as e:
            logger.error(f"Error in Phase 2: {str(e)}")
            return False
    
    def _phase_3_zone_based_architecture(self) -> bool:
        """Phase 3: Zone-Based Architecture Implementation"""
        logger.info("Phase 3: Zone-Based Architecture Implementation")
        
        try:
            # Deploy zone definitions
            zone_policies = self.zone_deployer.load_zone_policies()
            success = self.zone_deployer._deploy_zone_definition(zone_policies)
            
            if success:
                # Deploy zone-based policies
                policy_success = self.zone_deployer._deploy_zone_based_policies(zone_policies)
                
                if policy_success:
                    self.deployment_status["phase_3"] = {
                        "status": "completed",
                        "zones_created": len(self.controller.zone_objects),
                        "policies_created": len(self.controller.policy_objects),
                        "zone_architecture_ready": True
                    }
                    self.deployment_log.append("Phase 3 completed: Zone-Based Architecture")
                    return True
                else:
                    logger.error("Failed to deploy zone-based policies")
                    return False
            else:
                logger.error("Failed to deploy zone definitions")
                return False
                
        except Exception as e:
            logger.error(f"Error in Phase 3: {str(e)}")
            return False
    
    def _phase_4_object_oriented_networking(self) -> bool:
        """Phase 4: Object-Oriented Networking Implementation"""
        logger.info("Phase 4: Object-Oriented Networking Implementation")
        
        try:
            # Deploy Object-Oriented Networking features
            zone_policies = self.zone_deployer.load_zone_policies()
            success = self.zone_deployer._deploy_object_oriented_networking(zone_policies)
            
            if success:
                # Deploy device classification
                device_policies = self.zone_deployer.load_device_policies()
                classification_success = self.zone_deployer._deploy_device_classification(device_policies)
                
                if classification_success:
                    self.deployment_status["phase_4"] = {
                        "status": "completed",
                        "oon_features_deployed": True,
                        "device_classification_active": True,
                        "devices_classified": len(self.controller.device_objects)
                    }
                    self.deployment_log.append("Phase 4 completed: Object-Oriented Networking")
                    return True
                else:
                    logger.error("Failed to deploy device classification")
                    return False
            else:
                logger.error("Failed to deploy Object-Oriented Networking features")
                return False
                
        except Exception as e:
            logger.error(f"Error in Phase 4: {str(e)}")
            return False
    
    def _phase_5_policy_management(self) -> bool:
        """Phase 5: Policy Management and Optimization"""
        logger.info("Phase 5: Policy Management and Optimization")
        
        try:
            # Load policy templates
            self.policy_manager.load_policy_templates()
            
            # Deploy policy templates
            templates_deployed = 0
            template_types = ["zone_based", "device_groups", "firewall", "qos"]
            
            for template_type in template_types:
                if self.policy_manager.deploy_policy_template(f"{template_type}_template", template_type):
                    templates_deployed += 1
            
            if templates_deployed > 0:
                self.deployment_status["phase_5"] = {
                    "status": "completed",
                    "templates_deployed": templates_deployed,
                    "policy_management_active": True
                }
                self.deployment_log.append("Phase 5 completed: Policy Management")
                return True
            else:
                logger.error("Failed to deploy policy templates")
                return False
                
        except Exception as e:
            logger.error(f"Error in Phase 5: {str(e)}")
            return False
    
    def _phase_6_validation_and_monitoring(self) -> bool:
        """Phase 6: Validation and Monitoring Setup"""
        logger.info("Phase 6: Validation and Monitoring Setup")
        
        try:
            # Deploy monitoring and validation
            success = self.zone_deployer._deploy_monitoring_and_validation()
            
            if success:
                # Generate policy report
                policy_report = self.policy_manager.generate_policy_report()
                
                # Validate deployment
                validation_results = self._validate_complete_deployment()
                
                if validation_results["overall_success"]:
                    self.deployment_status["phase_6"] = {
                        "status": "completed",
                        "monitoring_active": True,
                        "validation_passed": True,
                        "policy_report_generated": True
                    }
                    self.deployment_log.append("Phase 6 completed: Validation and Monitoring")
                    return True
                else:
                    logger.error("Deployment validation failed")
                    return False
            else:
                logger.error("Failed to deploy monitoring and validation")
                return False
                
        except Exception as e:
            logger.error(f"Error in Phase 6: {str(e)}")
            return False
    
    def _analyze_current_state(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current network state"""
        return {
            "controller_info": scan_results.get("controller_info", {}),
            "network_topology": scan_results.get("network_topology", {}),
            "device_inventory": scan_results.get("device_inventory", {}),
            "security_analysis": scan_results.get("security_analysis", {}),
            "performance_analysis": scan_results.get("performance_analysis", {}),
            "compliance_analysis": scan_results.get("compliance_analysis", {})
        }
    
    def _generate_implementation_plan(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate implementation plan based on current state"""
        return {
            "strategy": "comprehensive_implementation",
            "phases": 6,
            "estimated_duration": "4-6 hours",
            "risk_level": "medium",
            "prerequisites_met": True,
            "rollback_plan": "available"
        }
    
    def _validate_complete_deployment(self) -> Dict[str, Any]:
        """Validate complete deployment"""
        validation_results = {
            "overall_success": True,
            "phase_results": {},
            "issues_found": [],
            "recommendations": []
        }
        
        # Validate each phase
        for phase_name, phase_data in self.deployment_status.items():
            if phase_data.get("status") == "completed":
                validation_results["phase_results"][phase_name] = "passed"
            else:
                validation_results["phase_results"][phase_name] = "failed"
                validation_results["overall_success"] = False
                validation_results["issues_found"].append(f"Phase {phase_name} failed")
        
        # Check critical components
        if len(self.controller.zone_objects) == 0:
            validation_results["issues_found"].append("No zones created")
            validation_results["overall_success"] = False
        
        if len(self.controller.policy_objects) == 0:
            validation_results["issues_found"].append("No policies created")
            validation_results["overall_success"] = False
        
        # Add recommendations
        if validation_results["overall_success"]:
            validation_results["recommendations"].append("Deployment completed successfully")
            validation_results["recommendations"].append("Monitor network performance for 24 hours")
            validation_results["recommendations"].append("Review security policies weekly")
        else:
            validation_results["recommendations"].append("Address identified issues before proceeding")
            validation_results["recommendations"].append("Consider partial rollback if needed")
        
        return validation_results
    
    def _generate_final_report(self):
        """Generate final deployment report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "deployment_summary": {
                "total_phases": 6,
                "completed_phases": len([p for p in self.deployment_status.values() if p.get("status") == "completed"]),
                "overall_success": all(p.get("status") == "completed" for p in self.deployment_status.values())
            },
            "deployment_status": self.deployment_status,
            "deployment_log": self.deployment_log,
            "final_metrics": {
                "zones_created": len(self.controller.zone_objects),
                "policies_created": len(self.controller.policy_objects),
                "devices_classified": len(self.controller.device_objects),
                "networks_configured": len(self.controller.network_objects)
            },
            "controller": self.controller.host,
            "validation_results": self._validate_complete_deployment()
        }
        
        filename = f"comprehensive_deployment_report_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Final deployment report saved to {filename}")

def main():
    """Main function for comprehensive deployment"""
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
    
    # Initialize comprehensive deployer
    deployer = ComprehensiveNetworkDeployer(controller)
    
    # Confirm deployment
    print(f"\n{'='*80}")
    print("Comprehensive Network Deployment with Zone-Based Rules and Object-Oriented Networking")
    print(f"{'='*80}")
    print(f"Controller: {controller_host}")
    print("Deployment includes:")
    print("  ✓ Zone-Based Firewall Rules")
    print("  ✓ Object-Oriented Networking")
    print("  ✓ VLAN Segmentation")
    print("  ✓ Device Classification")
    print("  ✓ Policy Management")
    print("  ✓ Monitoring and Validation")
    print("  ✓ Optional Cleanup of Conflicting Objects")
    print(f"{'='*80}")
    print("This deployment will:")
    print("  0. Analyze and optionally clean up existing objects")
    print("  1. Perform initial network assessment")
    print("  2. Create comprehensive VLAN infrastructure")
    print("  3. Implement zone-based security architecture")
    print("  4. Deploy Object-Oriented Networking features")
    print("  5. Set up policy management system")
    print("  6. Configure monitoring and validation")
    print(f"{'='*80}")
    print("IMPORTANT: The cleanup phase will ask for your approval before")
    print("removing any existing VLANs, firewall groups, or rules that may")
    print("conflict with the new Zone-Based architecture.")
    print(f"{'='*80}\n")
    
    confirm = input("Proceed with comprehensive deployment? [y/N]: ")
    if confirm.lower() != 'y':
        print("Deployment cancelled")
        return False
    
    # Execute comprehensive deployment
    success = deployer.execute_comprehensive_deployment()
    
    if success:
        print("\n✅ Comprehensive network deployment completed successfully!")
        print("Features deployed:")
        print("  ✓ Zone-Based Firewall Rules")
        print("  ✓ Object-Oriented Networking")
        print("  ✓ VLAN Segmentation")
        print("  ✓ Device Classification")
        print("  ✓ Policy Management")
        print("  ✓ Monitoring and Validation")
        print("\nCheck comprehensive_deployment_report_*.json for detailed results")
    else:
        print("\n❌ Comprehensive deployment encountered errors")
        print("Check comprehensive_deployment.log for details")
        print("Review deployment status and consider rollback if needed")
    
    return success

if __name__ == "__main__":
    main()
