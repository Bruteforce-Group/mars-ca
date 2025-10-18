#!/usr/bin/env python3
"""
Integrated Network Enhancements
Brings together all four major enhancements:
1. Object-Oriented Networking with inheritance and templating
2. Advanced policy management with dynamic updates
3. Enhanced monitoring with comprehensive logging and alerting
4. Zero-trust improvements with inter-zone security
"""

import os
import json
import time
import logging
import threading
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

# Import our enhancement modules
from object_oriented_networking import ObjectOrientedNetworkManager, NetworkObject, ZoneTemplate, DeviceTemplate, PolicyTemplate
from dynamic_policy_manager import DynamicPolicyManager, Policy, PolicyRule, PolicyType, PolicyStatus
from enhanced_monitoring_system import EnhancedMonitoringSystem, AlertLevel, AlertType
from zero_trust_security import ZeroTrustSecurityManager, TrustLevel, SecurityPolicy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integrated_enhancements.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegratedNetworkEnhancements:
    """Main class that integrates all four network enhancements"""
    
    def __init__(self, controller_host: str, api_key: str):
        self.controller_host = controller_host
        self.api_key = api_key
        
        # Initialize all enhancement systems
        print("Initializing integrated network enhancement systems...")
        
        # 1. Object-Oriented Networking
        print("  • Setting up Object-Oriented Networking...")
        self.oon_manager = ObjectOrientedNetworkManager(controller_host, api_key)
        
        # 2. Dynamic Policy Management
        print("  • Setting up Dynamic Policy Management...")
        self.policy_manager = DynamicPolicyManager(controller_host, api_key)
        
        # 3. Enhanced Monitoring
        print("  • Setting up Enhanced Monitoring...")
        self.monitoring_system = EnhancedMonitoringSystem(controller_host, api_key)
        
        # 4. Zero-Trust Security
        print("  • Setting up Zero-Trust Security...")
        self.security_manager = ZeroTrustSecurityManager(controller_host, api_key)
        
        # Integration state
        self.integration_enabled = False
        self.integration_thread = None
        
        # Setup cross-system integration
        self._setup_integration()
    
    def _setup_integration(self):
        """Setup integration between all systems"""
        try:
            # Register monitoring callbacks for policy changes
            self.monitoring_system.alert_manager.register_alert_callback(
                self._handle_security_alert
            )
            
            # Register policy change callbacks for OON updates
            self.policy_manager.change_detector.register_change_callback(
                self._handle_network_changes
            )
            
            # Setup security context updates from monitoring
            self.monitoring_system.log_manager.log(
                "INFO", "Integrated network enhancements initialized", "integration"
            )
            
            logger.info("Cross-system integration setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up integration: {str(e)}")
    
    def _handle_security_alert(self, alert):
        """Handle security alerts from monitoring system"""
        try:
            # Update security context based on alert
            if alert.alert_type == AlertType.SECURITY:
                # Find affected entities and update risk scores
                for entity_id, context in self.security_manager.zero_trust_engine.security_contexts.items():
                    if alert.source in context.entity_id or alert.source in context.attributes.get('name', ''):
                        # Increase risk score based on alert severity
                        risk_increase = {
                            AlertLevel.INFO: 0.1,
                            AlertLevel.WARNING: 0.3,
                            AlertLevel.ERROR: 0.5,
                            AlertLevel.CRITICAL: 0.8
                        }.get(alert.level, 0.2)
                        
                        new_risk_score = min(1.0, context.risk_score + risk_increase)
                        self.security_manager.zero_trust_engine.update_risk_score(
                            entity_id, new_risk_score, f"Security alert: {alert.title}"
                        )
            
            # Create policy update if needed
            if alert.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
                self._create_security_policy_update(alert)
                
        except Exception as e:
            logger.error(f"Error handling security alert: {str(e)}")
    
    def _handle_network_changes(self, changes):
        """Handle network changes from policy manager"""
        try:
            # Update OON objects based on network changes
            if changes.get("device_changes"):
                for change in changes["device_changes"]:
                    if change["action"] == "added":
                        device = change["device"]
                        # Create OON object for new device
                        device_obj = NetworkObject(
                            name=device.get("name", "unknown"),
                            description=f"Device discovered: {device.get('type', 'unknown')}",
                            attributes={
                                "object_type": "device",
                                "device_type": device.get("type", "unknown"),
                                "ip_address": device.get("ip", ""),
                                "status": device.get("status", "unknown")
                            }
                        )
                        self.oon_manager.create_object(device_obj, template_name="management_devices")
            
            # Update security contexts
            if changes.get("client_changes"):
                for change in changes["client_changes"]:
                    if change["action"] == "added":
                        client = change["client"]
                        # Create security context for new client
                        trust_level = TrustLevel.MEDIUM  # Default trust level
                        if "guest" in client.get("hostname", "").lower():
                            trust_level = TrustLevel.LOW
                        elif "admin" in client.get("hostname", "").lower():
                            trust_level = TrustLevel.HIGH
                        
                        self.security_manager.zero_trust_engine.create_security_context(
                            client.get("id", ""), "client", trust_level
                        )
            
            # Log the changes
            self.monitoring_system.log_manager.log(
                "INFO", f"Network changes detected: {len(changes)} change types", "integration"
            )
            
        except Exception as e:
            logger.error(f"Error handling network changes: {str(e)}")
    
    def _create_security_policy_update(self, alert):
        """Create security policy update based on alert"""
        try:
            # Create a new security policy rule
            security_rule = PolicyRule(
                rule_id=f"security_rule_{int(time.time())}",
                name=f"Security Response: {alert.title}",
                action="deny",
                source="*",
                destination="*",
                protocol="all",
                ports=[],
                conditions={"threat_level": alert.level.value}
            )
            
            # Create policy
            security_policy = Policy(
                policy_id=f"security_policy_{int(time.time())}",
                name=f"Security Response Policy: {alert.title}",
                description=f"Automatically created policy in response to security alert: {alert.description}",
                policy_type=PolicyType.SECURITY,
                version="1.0.0",
                rules=[security_rule],
                status=PolicyStatus.ACTIVE,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by="security_system",
                auto_deploy=True
            )
            
            # Create and deploy policy
            self.policy_manager.create_policy(security_policy)
            
            self.monitoring_system.log_manager.log(
                "INFO", f"Created security policy in response to alert: {alert.title}", "integration"
            )
            
        except Exception as e:
            logger.error(f"Error creating security policy update: {str(e)}")
    
    def start_integrated_systems(self):
        """Start all integrated systems"""
        try:
            print("\nStarting integrated network enhancement systems...")
            
            # Start monitoring system
            print("  • Starting enhanced monitoring...")
            self.monitoring_system.start_monitoring()
            
            # Start policy management auto-deployment
            print("  • Starting dynamic policy management...")
            self.policy_manager.start_auto_deployment()
            
            # Start zero-trust monitoring
            print("  • Starting zero-trust security monitoring...")
            self.security_manager.start_monitoring()
            
            # Start integration thread
            self.integration_enabled = True
            self.integration_thread = threading.Thread(target=self._integration_loop)
            self.integration_thread.daemon = True
            self.integration_thread.start()
            
            print("✅ All integrated systems started successfully!")
            
        except Exception as e:
            logger.error(f"Error starting integrated systems: {str(e)}")
            raise
    
    def stop_integrated_systems(self):
        """Stop all integrated systems"""
        try:
            print("\nStopping integrated network enhancement systems...")
            
            # Stop integration thread
            self.integration_enabled = False
            if self.integration_thread:
                self.integration_thread.join(timeout=5)
            
            # Stop all systems
            self.monitoring_system.stop_monitoring()
            self.policy_manager.stop_auto_deployment()
            self.security_manager.stop_monitoring()
            
            print("✅ All integrated systems stopped successfully!")
            
        except Exception as e:
            logger.error(f"Error stopping integrated systems: {str(e)}")
    
    def _integration_loop(self):
        """Main integration loop"""
        while self.integration_enabled:
            try:
                # Sync security contexts with OON objects
                self._sync_security_with_oon()
                
                # Update policies based on security context changes
                self._update_policies_from_security()
                
                # Generate integrated reports
                self._generate_integrated_reports()
                
                time.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in integration loop: {str(e)}")
                time.sleep(60)
    
    def _sync_security_with_oon(self):
        """Sync security contexts with OON objects"""
        try:
            # Update OON objects with security context information
            for entity_id, context in self.security_manager.zero_trust_engine.security_contexts.items():
                if entity_id in self.oon_manager.objects:
                    obj = self.oon_manager.objects[entity_id]
                    obj.trust_level = context.trust_level.value
                    obj.attributes.update({
                        "risk_score": context.risk_score,
                        "last_verified": context.last_verified.isoformat(),
                        "security_policies": [p.value for p in context.security_policies]
                    })
            
        except Exception as e:
            logger.error(f"Error syncing security with OON: {str(e)}")
    
    def _update_policies_from_security(self):
        """Update policies based on security context changes"""
        try:
            # Check for high-risk entities that need policy updates
            high_risk_entities = [
                c for c in self.security_manager.zero_trust_engine.security_contexts.values()
                if c.risk_score > 0.8
            ]
            
            if high_risk_entities:
                # Create quarantine policy for high-risk entities
                quarantine_rule = PolicyRule(
                    rule_id=f"quarantine_rule_{int(time.time())}",
                    name="Quarantine High-Risk Entities",
                    action="deny",
                    source="*",
                    destination="*",
                    protocol="all",
                    ports=[],
                    conditions={"risk_score": ">0.8"}
                )
                
                quarantine_policy = Policy(
                    policy_id=f"quarantine_policy_{int(time.time())}",
                    name="Quarantine High-Risk Entities",
                    description="Automatically created policy to quarantine high-risk entities",
                    policy_type=PolicyType.SECURITY,
                    version="1.0.0",
                    rules=[quarantine_rule],
                    status=PolicyStatus.ACTIVE,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    created_by="security_integration",
                    auto_deploy=True
                )
                
                self.policy_manager.create_policy(quarantine_policy)
                
        except Exception as e:
            logger.error(f"Error updating policies from security: {str(e)}")
    
    def _generate_integrated_reports(self):
        """Generate integrated reports from all systems"""
        try:
            # Get reports from all systems
            oon_report = self.oon_manager.generate_inheritance_report()
            policy_report = self.policy_manager.generate_policy_report()
            monitoring_dashboard = self.monitoring_system.get_monitoring_dashboard()
            security_dashboard = self.security_manager.get_security_dashboard()
            
            # Create integrated report
            integrated_report = {
                "timestamp": datetime.now().isoformat(),
                "integration_status": "active",
                "systems": {
                    "object_oriented_networking": {
                        "status": "active",
                        "total_objects": oon_report.get("total_objects", 0),
                        "total_templates": oon_report.get("total_templates", 0)
                    },
                    "dynamic_policy_management": {
                        "status": "active",
                        "total_policies": policy_report.get("total_policies", 0),
                        "active_policies": policy_report.get("active_policies", 0)
                    },
                    "enhanced_monitoring": {
                        "status": monitoring_dashboard.get("monitoring_enabled", False),
                        "total_alerts": monitoring_dashboard.get("alerts", {}).get("total", 0),
                        "active_alerts": monitoring_dashboard.get("alerts", {}).get("active", 0)
                    },
                    "zero_trust_security": {
                        "status": security_dashboard.get("monitoring_enabled", False),
                        "total_contexts": security_dashboard.get("total_contexts", 0),
                        "high_risk_entities": len(security_dashboard.get("high_risk_entities", []))
                    }
                },
                "integration_metrics": {
                    "cross_system_alerts": 0,  # Would track actual cross-system alerts
                    "policy_updates_from_security": 0,  # Would track actual updates
                    "oon_object_updates": 0  # Would track actual updates
                }
            }
            
            # Save integrated report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"integrated_network_report_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(integrated_report, f, indent=2, default=str)
            
            logger.info(f"Generated integrated report: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating integrated reports: {str(e)}")
    
    def get_integrated_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive integrated dashboard"""
        try:
            # Get individual dashboards
            monitoring_dashboard = self.monitoring_system.get_monitoring_dashboard()
            security_dashboard = self.security_manager.get_security_dashboard()
            policy_report = self.policy_manager.generate_policy_report()
            oon_report = self.oon_manager.generate_inheritance_report()
            
            # Create integrated dashboard
            dashboard = {
                "timestamp": datetime.now().isoformat(),
                "integration_status": "active" if self.integration_enabled else "inactive",
                "overall_health": self._calculate_overall_health(monitoring_dashboard, security_dashboard),
                "systems": {
                    "object_oriented_networking": {
                        "objects": oon_report.get("total_objects", 0),
                        "templates": oon_report.get("total_templates", 0),
                        "inheritance_chains": len(oon_report.get("inheritance_chains", {}))
                    },
                    "dynamic_policy_management": {
                        "policies": policy_report.get("total_policies", 0),
                        "active_policies": policy_report.get("active_policies", 0),
                        "auto_deploy": policy_report.get("auto_deploy_enabled", False)
                    },
                    "enhanced_monitoring": {
                        "monitoring_enabled": monitoring_dashboard.get("monitoring_enabled", False),
                        "alerts": monitoring_dashboard.get("alerts", {}),
                        "system_health": monitoring_dashboard.get("system_health", {})
                    },
                    "zero_trust_security": {
                        "monitoring_enabled": security_dashboard.get("monitoring_enabled", False),
                        "security_contexts": security_dashboard.get("total_contexts", 0),
                        "high_risk_entities": len(security_dashboard.get("high_risk_entities", []))
                    }
                },
                "recommendations": self._generate_recommendations(monitoring_dashboard, security_dashboard)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating integrated dashboard: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_overall_health(self, monitoring_dashboard: Dict, security_dashboard: Dict) -> Dict[str, Any]:
        """Calculate overall system health"""
        try:
            # Get health scores from individual systems
            monitoring_health = monitoring_dashboard.get("system_health", {}).get("health_score", 50)
            security_health = 100 - len(security_dashboard.get("high_risk_entities", [])) * 10
            
            # Calculate overall health
            overall_health = (monitoring_health + security_health) / 2
            
            # Determine status
            if overall_health >= 80:
                status = "excellent"
            elif overall_health >= 60:
                status = "good"
            elif overall_health >= 40:
                status = "fair"
            else:
                status = "poor"
            
            return {
                "overall_score": overall_health,
                "status": status,
                "monitoring_health": monitoring_health,
                "security_health": security_health
            }
            
        except Exception as e:
            logger.error(f"Error calculating overall health: {str(e)}")
            return {"overall_score": 0, "status": "unknown", "error": str(e)}
    
    def _generate_recommendations(self, monitoring_dashboard: Dict, security_dashboard: Dict) -> List[str]:
        """Generate recommendations based on system state"""
        recommendations = []
        
        try:
            # Monitoring recommendations
            if monitoring_dashboard.get("alerts", {}).get("active", 0) > 5:
                recommendations.append("High number of active alerts - review and resolve critical issues")
            
            if monitoring_dashboard.get("system_health", {}).get("health_score", 100) < 70:
                recommendations.append("System health is degraded - investigate performance issues")
            
            # Security recommendations
            high_risk_count = len(security_dashboard.get("high_risk_entities", []))
            if high_risk_count > 0:
                recommendations.append(f"{high_risk_count} high-risk entities detected - consider quarantine or investigation")
            
            # General recommendations
            if not recommendations:
                recommendations.append("All systems operating normally - continue monitoring")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Error generating recommendations"]

def main():
    """Main function for Integrated Network Enhancements demonstration"""
    print(f"\n{'='*80}")
    print("Integrated Network Enhancements")
    print("Object-Oriented Networking + Dynamic Policies + Enhanced Monitoring + Zero-Trust Security")
    print(f"{'='*80}")
    
    # Load environment variables
    controller_host = os.getenv('UNIFI_CONTROLLER_HOSTNAME_MARS', '192.168.22.194')
    api_key = os.getenv('UNIFI_API_KEY_MARS')
    
    if not api_key:
        print("❌ Error: UNIFI_API_KEY_MARS not set in .env file")
        return False
    
    try:
        # Initialize Integrated Network Enhancements
        print("Initializing Integrated Network Enhancement System...")
        integrated_system = IntegratedNetworkEnhancements(controller_host, api_key)
        
        # Start all integrated systems
        integrated_system.start_integrated_systems()
        
        # Wait for systems to collect data
        print("\nCollecting data from all systems (60 seconds)...")
        time.sleep(60)
        
        # Get integrated dashboard
        print("\nGenerating integrated dashboard...")
        dashboard = integrated_system.get_integrated_dashboard()
        
        # Save dashboard
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"integrated_dashboard_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(dashboard, f, indent=2, default=str)
        
        # Display results
        print(f"\n{'='*80}")
        print("✅ INTEGRATED NETWORK ENHANCEMENTS COMPLETED!")
        print(f"{'='*80}")
        print(f"Overall Health: {dashboard['overall_health']['status'].upper()} ({dashboard['overall_health']['overall_score']:.1f}/100)")
        print(f"Integration Status: {'Active' if dashboard['integration_status'] == 'active' else 'Inactive'}")
        print(f"\nSystem Status:")
        print(f"  • Object-Oriented Networking: {dashboard['systems']['object_oriented_networking']['objects']} objects")
        print(f"  • Dynamic Policy Management: {dashboard['systems']['dynamic_policy_management']['policies']} policies")
        print(f"  • Enhanced Monitoring: {dashboard['systems']['enhanced_monitoring']['alerts']['active']} active alerts")
        print(f"  • Zero-Trust Security: {dashboard['systems']['zero_trust_security']['security_contexts']} contexts")
        print(f"\nRecommendations:")
        for rec in dashboard['recommendations']:
            print(f"  • {rec}")
        print(f"\nDashboard saved to: {filename}")
        print(f"\n{'='*80}")
        print("KEY FEATURES DELIVERED:")
        print("  ✓ Object-Oriented Networking with inheritance and templating")
        print("  ✓ Dynamic policy management with real-time updates")
        print("  ✓ Enhanced monitoring with comprehensive alerting")
        print("  ✓ Zero-trust security with inter-zone protection")
        print("  ✓ Cross-system integration and automation")
        print("  ✓ Unified dashboard and reporting")
        print("  ✓ Automated threat response")
        print("  ✓ Intelligent policy updates")
        print("  ✓ Comprehensive security context management")
        print("  ✓ Real-time system health monitoring")
        print(f"{'='*80}")
        
        # Stop systems for demo
        print("\nStopping integrated systems...")
        integrated_system.stop_integrated_systems()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
