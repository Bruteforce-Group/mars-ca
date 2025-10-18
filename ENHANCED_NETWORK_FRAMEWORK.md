# Enhanced UniFi Network Framework with Zone-Based Rules and Object-Oriented Networking

## Overview

This enhanced framework extends the existing UniFi Network Policy Framework with advanced Zone-Based rules and Object-Oriented Networking (OON) capabilities. It provides comprehensive network segmentation, security policies, and automation specifically designed for UniFi UCG-Fiber deployments.

## Key Features

### 🏗️ Zone-Based Architecture
- **Trust Zones**: Management, Corporate, User Devices
- **Semi-Trust Zones**: IoT Trusted, Security, Automotive, Print Services
- **Untrust Zones**: IoT General, Guest, Quarantine
- **Zone-Based Firewall Rules**: Inter-zone and internet access policies

### 🔧 Object-Oriented Networking
- **Network Objects**: VLANs, Firewall Groups, Devices as objects
- **Policy Objects**: Firewall Rules, QoS Policies with inheritance
- **Device Objects**: Automated classification and zone assignment
- **Inheritance Hierarchy**: Base classes with specialized implementations

### 🛡️ Enhanced Security
- **Zero Trust Architecture**: Default-deny with explicit allow rules
- **Advanced Device Classification**: Multi-criteria device identification
- **Comprehensive Monitoring**: Real-time security and performance monitoring
- **Automated Policy Management**: Create, update, delete, rename policies via API

## Architecture Components

### Core Files

#### Enhanced Controller (`enhanced_unifi_controller.py`)
- **UniFiController**: Enhanced API client with OON capabilities
- **NetworkObject**: Base class for all network objects
- **DeviceObject**: Device classification and management
- **PolicyObject**: Policy enforcement and validation
- **ZoneObject**: Zone-based firewall management

#### Zone-Based Policies (`zone_based_policies.json`)
- **Zone Definitions**: Trust levels and security zones
- **Zone-Based Rules**: Inter-zone and internet access policies
- **Object-Oriented Networking**: Network objects and inheritance hierarchy

#### Deployment Scripts
- **`zone_based_deployment.py`**: Zone-based architecture deployment
- **`policy_management.py`**: Comprehensive policy management
- **`initial_network_scan.py`**: Network assessment and template generation
- **`comprehensive_network_deployment.py`**: Complete deployment orchestrator

## Installation and Setup

### Prerequisites
- Python 3.8+
- UniFi Network Application 7.5+
- Administrative access to UniFi controller
- Required Python packages (see requirements.txt)

### Environment Setup
```bash
# Clone or download the repository
cd /path/to/mars-ca

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
export UNIFI_CONTROLLER_HOSTNAME_MARS="mars.int.bozza.au"
export UNIFI_USERNAME_MARS="root"
export UNIFI_PASSWORD_MARS="your_password"
export UNIFI_API_KEY_MARS="your_api_key"
```

### Required Files
Ensure these files are present in the project directory:
- `zone_based_policies.json` - Zone-based policy configuration
- `device-groups-policies.json` - Device classification rules
- `firewall-traffic-policies.json` - Firewall policy definitions
- `qos-bandwidth-policies.json` - QoS configuration
- `monitoring-logging-policies.json` - Monitoring setup

## Usage

### 1. Initial Network Assessment
```bash
# Perform comprehensive network scan
python3 initial_network_scan.py

# This will:
# - Analyze current network configuration
# - Identify security gaps and requirements
# - Generate implementation template
# - Create deployment recommendations
```

### 2. Zone-Based Deployment
```bash
# Deploy zone-based architecture
python3 zone_based_deployment.py

# This will:
# - Create VLAN networks and zones
# - Deploy zone-based firewall rules
# - Implement device classification
# - Set up Object-Oriented Networking
```

### 3. Policy Management
```bash
# Interactive policy management
python3 policy_management.py

# Available operations:
# - List all policies
# - Create new policies
# - Update existing policies
# - Delete policies
# - Rename policies
# - Deploy policy templates
```

### 4. Comprehensive Deployment
```bash
# Complete deployment with all features
python3 comprehensive_network_deployment.py

# This will:
# - Perform initial assessment
# - Deploy network infrastructure
# - Implement zone-based architecture
# - Set up Object-Oriented Networking
# - Configure policy management
# - Enable monitoring and validation
```

## Zone-Based Architecture

### Trust Zones (High Security)
- **Management Zone (VLAN 1)**: Network infrastructure devices
- **Corporate Zone (VLAN 10)**: Servers and admin workstations
- **User Zone (VLAN 20)**: Mac computers, iPhones, personal devices

### Semi-Trust Zones (Medium Security)
- **IoT Trusted Zone (VLAN 30)**: Apple TV, HomePods, Apple Watch
- **Security Zone (VLAN 50)**: IP cameras, NVR systems
- **Automotive Zone (VLAN 60)**: Tesla vehicles, car chargers
- **Print Zone (VLAN 70)**: Printers, scanners

### Untrust Zones (Low/Isolated Security)
- **IoT General Zone (VLAN 40)**: Tuya smart home devices
- **Guest Zone (VLAN 80)**: Visitor device access
- **Quarantine Zone (VLAN 90)**: Isolated suspicious devices

## Object-Oriented Networking

### Network Objects
```python
# Device Object
device = DeviceObject(
    name="iPhone_12",
    mac_address="aa:bb:cc:dd:ee:ff",
    device_type="mobile",
    trust_level="medium_high"
)

# Policy Object
policy = PolicyObject(
    name="Internet_Access_Users",
    action="allow",
    source_zones=["user_zone"],
    destination="internet"
)

# Zone Object
zone = ZoneObject(
    name="User Zone",
    security_level="medium_high",
    trust_score=80,
    vlan_ids=[20]
)
```

### Inheritance Hierarchy
- **BaseNetwork**: Common network object attributes
- **BaseDevice**: Device-specific attributes and methods
- **BasePolicy**: Policy-specific attributes and methods
- **Specialized Classes**: Inherit from base classes with specific implementations

## Policy Management

### Supported Policy Types
- **Firewall Rules**: Traditional and zone-based firewall rules
- **Firewall Groups**: Address and port groups
- **Zone Policies**: Zone-based security policies
- **QoS Policies**: Quality of Service configurations
- **Device Groups**: Device classification groups

### Policy Operations
```python
# Create policy
manager.create_policy("firewall_rule", "Block_SSH", {
    "action": "deny",
    "protocol": "tcp",
    "ports": ["22"],
    "source": "any",
    "destination": "any"
})

# Update policy
manager.update_policy("firewall_rule", "Block_SSH", {
    "action": "allow",
    "logging": True
})

# Delete policy
manager.delete_policy("firewall_rule", "Block_SSH")

# Rename policy
manager.rename_policy("firewall_rule", "Block_SSH", "Allow_SSH")
```

## Monitoring and Validation

### Real-time Monitoring
- **Network Performance**: Bandwidth, latency, jitter monitoring
- **Security Events**: Threat detection and response
- **Device Health**: Device status and performance metrics
- **Policy Compliance**: Policy enforcement validation

### Reporting
- **Deployment Reports**: Detailed deployment status and results
- **Policy Reports**: Comprehensive policy inventory and status
- **Security Reports**: Security posture and threat analysis
- **Performance Reports**: Network performance and optimization recommendations

## Configuration Files

### Zone-Based Policies (`zone_based_policies.json`)
```json
{
  "zone_definitions": {
    "trust_zones": {
      "management_zone": {
        "name": "Management Zone",
        "vlan_ids": [1],
        "security_level": "high",
        "trust_score": 100
      }
    }
  },
  "zone_based_rules": {
    "inter_zone_policies": {
      "trust_to_trust": {
        "source_zones": ["management_zone", "corporate_zone"],
        "destination_zones": ["user_zone"],
        "action": "allow"
      }
    }
  }
}
```

### Object-Oriented Networking
```json
{
  "object_oriented_networking": {
    "network_objects": {
      "device_objects": {
        "management_device": {
          "class": "NetworkDevice",
          "inheritance": "base_device",
          "attributes": {
            "device_type": "infrastructure",
            "trust_level": "high"
          }
        }
      }
    }
  }
}
```

## Deployment Phases

### Phase 1: Initial Assessment
- Network topology analysis
- Device inventory and classification
- Security configuration review
- Implementation template generation

### Phase 2: Network Infrastructure
- VLAN network creation
- DHCP scope configuration
- Inter-VLAN routing setup
- Network connectivity testing

### Phase 3: Zone-Based Architecture
- Zone definition and assignment
- Zone-based firewall rules
- Inter-zone policy implementation
- Internet access policies

### Phase 4: Object-Oriented Networking
- Network object creation
- Device classification system
- Policy object implementation
- Inheritance hierarchy setup

### Phase 5: Policy Management
- Policy template deployment
- Automated policy management
- Policy optimization
- Compliance validation

### Phase 6: Monitoring and Validation
- Monitoring system setup
- Performance validation
- Security testing
- Final compliance report

## Troubleshooting

### Common Issues

#### Authentication Failures
```bash
# Check credentials
echo $UNIFI_API_KEY_MARS
echo $UNIFI_PASSWORD_MARS

# Test controller connectivity
curl -k https://mars.int.bozza.au/api/self \
  -H "X-API-Key: $UNIFI_API_KEY_MARS"
```

#### Policy Deployment Issues
```bash
# Check deployment logs
tail -f zone_based_deployment.log

# Validate configuration files
python3 -m json.tool zone_based_policies.json

# Re-run specific deployment phase
python3 zone_based_deployment.py --phase 3
```

#### Device Classification Issues
```bash
# Check device classification
python3 policy_management.py
# Select option 1 to list all policies

# Re-classify devices
python3 initial_network_scan.py
```

### Log Files
- `enhanced_unifi_deployment.log`: Enhanced controller operations
- `zone_based_deployment.log`: Zone-based deployment progress
- `policy_management.log`: Policy management operations
- `initial_network_scan.log`: Network scanning and analysis
- `comprehensive_deployment.log`: Complete deployment orchestration

## Best Practices

### Security
- **Regular Policy Review**: Weekly policy effectiveness review
- **Threat Intelligence**: Continuous threat feed updates
- **Access Control**: Regular access control validation
- **Incident Response**: Automated threat response procedures

### Performance
- **Bandwidth Monitoring**: Continuous bandwidth utilization tracking
- **QoS Optimization**: Regular QoS policy tuning
- **Device Classification**: Monthly device classification accuracy review
- **Policy Optimization**: Quarterly policy performance analysis

### Maintenance
- **Configuration Backups**: Daily configuration backups
- **Policy Updates**: Monthly policy template updates
- **Security Audits**: Quarterly security posture assessments
- **Documentation**: Continuous documentation updates

## Support and Documentation

### Resources
- **UniFi Documentation**: [help.ui.com](https://help.ui.com)
- **Zone-Based Firewall**: UniFi Network Application help
- **Object-Oriented Networking**: Framework documentation

### Contact Information
- **Network Administrator**: admin@bozza.au
- **Security Team**: security@bozza.au
- **Technical Support**: Based on internal procedures

## License and Compliance

This enhanced framework is designed for the specific environment and requirements of the Mars network infrastructure. It implements enterprise-grade security, performance optimization, and monitoring capabilities with comprehensive automation and Object-Oriented Networking principles.

---

**Last Updated**: January 2025  
**Version**: 2.0  
**Environment**: Mars UCG-Fiber Production Network with Enhanced Features
