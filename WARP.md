# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a comprehensive **UniFi Network Policy Framework** designed for UCG-Fiber deployments. The project implements enterprise-grade network segmentation, security policies, and automation for UniFi networks using Python scripts and JSON configuration files.

### Core Architecture

The framework implements a **zero-trust network architecture** with 10 VLANs providing role-based network segmentation:
- **Management (VLAN 1)**: Infrastructure devices (UCG-Fiber, switches, APs) 
- **Corporate (VLAN 10)**: Servers and admin workstations
- **User Devices (VLAN 20)**: Mac computers, iPhones, personal devices
- **Apple IoT (VLAN 30)**: Apple TV, HomePods, Apple Watch
- **General IoT (VLAN 40)**: Tuya smart home devices
- **Security (VLAN 50)**: IP cameras, NVR systems  
- **Automotive (VLAN 60)**: Tesla vehicles, car chargers
- **Print Services (VLAN 70)**: Printers, scanners
- **Guest (VLAN 80)**: Visitor device access
- **Quarantine (VLAN 90)**: Isolated suspicious devices

## Development Commands

### Environment Setup
```bash
# Activate the Python virtual environment and set credentials
source activate.sh

# Alternative: Manual virtual environment setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Main Operations
```bash
# Deploy all network policies to UniFi controller
python3 deploy_unifi_policies.py

# Monitor and validate deployed policies  
python3 monitor_unifi_policies.py

# Test authentication and connectivity
python3 test_unifi_auth.py
```

### Configuration Validation
```bash
# Validate JSON policy files syntax
python3 -m json.tool device-groups-policies.json
python3 -m json.tool firewall-traffic-policies.json
python3 -m json.tool qos-bandwidth-policies.json
python3 -m json.tool scheduling-policies.json
python3 -m json.tool monitoring-logging-policies.json

# Test controller connectivity
ping mars.int.bozza.au

# Check environment variables
echo $UNIFI_CONTROLLER_HOSTNAME_MARS
echo $UNIFI_USERNAME_MARS
```

### Debugging and Troubleshooting  
```bash
# View deployment logs
tail -f unifi_deployment.log

# View monitoring logs
tail -f unifi_monitoring.log

# Check device classification
python3 monitor_unifi_policies.py | grep -A 10 "Device Distribution"

# Re-create virtual environment if corrupted
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Architecture Details

### Key Python Components

#### `deploy_unifi_policies.py`
- Main deployment orchestrator
- Handles authentication to UniFi controller (API key or username/password)
- Creates VLANs, firewall groups, firewall rules, and QoS policies
- Supports multiple controller types (UDM/UDM Pro on port 443, Classic on 8443)
- Comprehensive error handling and logging
- Generates deployment history logs

#### `monitor_unifi_policies.py` 
- Policy validation and health monitoring
- Device classification accuracy checking
- Network performance monitoring
- Security alert aggregation  
- Generates formatted status reports using tabulate

#### `test_unifi_auth.py`
- Diagnostic tool for authentication issues
- Tests multiple controller endpoints and ports
- Validates API keys and username/password combinations
- Provides detailed troubleshooting guidance

#### `UniFiController` Class
- Central API client for UniFi Network Application
- Handles multiple authentication methods
- Auto-detects controller type (UDM vs Classic)
- Manages CSRF tokens and session state
- Comprehensive retry logic for network failures

### Configuration Architecture

#### Policy Definition System
The framework uses JSON files to define policies in a structured, hierarchical approach:

- **`device-groups-policies.json`**: Device classification rules using fingerprinting, MAC OUIs, hostname patterns, and DHCP options
- **`firewall-traffic-policies.json`**: Zero-trust firewall rules with Object Policy groups
- **`qos-bandwidth-policies.json`**: 8-tier QoS hierarchy with DSCP marking
- **`scheduling-policies.json`**: Time-based policy enforcement (business hours, sleep time, maintenance windows)
- **`monitoring-logging-policies.json`**: Security monitoring, alerting, and compliance logging

#### Device Classification Engine
Sophisticated device identification using multiple criteria:
- Device fingerprinting (OS detection, user agents)
- MAC address OUI patterns
- DHCP vendor class identifiers  
- Hostname pattern matching
- Port usage analysis
- DNS query patterns
- Manufacturer identification

### Security Framework

#### Zero Trust Implementation
- Default-deny firewall policies
- Explicit allow rules for required communications
- Automatic device quarantine for security threats
- Geographic IP blocking (China, Russia, North Korea)
- Content filtering by device category

#### Compliance Features
- ISO 27001 controls implementation
- NIST Cybersecurity Framework alignment
- Australian Privacy Principles adherence
- Comprehensive audit logging to syslog (192.168.10.100)

## Environment Configuration

### Required Environment Variables
```bash
UNIFI_CONTROLLER_HOSTNAME_MARS=mars.int.bozza.au
UNIFI_USERNAME_MARS=root
UNIFI_PASSWORD_MARS=your_password_here
UNIFI_API_KEY_MARS=your_api_key_here
```

### Authentication Methods
1. **API Key** (recommended for automation): Generate in UniFi Network Controller under Settings > Admins
2. **Username/Password**: Traditional login method with session management

## Common Development Patterns

### Policy Deployment Workflow
1. Load and validate JSON configuration files
2. Authenticate with UniFi controller using multiple fallback methods
3. Create network VLANs with proper subnets and DHCP ranges
4. Deploy firewall groups for device classification
5. Configure firewall rules using Object Policy system
6. Set up QoS profiles with bandwidth limits and DSCP marking
7. Generate comprehensive deployment logs

### Monitoring and Validation
1. Connect to controller and gather system information  
2. Validate deployed networks, firewall groups, and rules
3. Check device classification accuracy against policy definitions
4. Monitor traffic statistics and bandwidth utilization
5. Aggregate security alerts and compliance status
6. Generate formatted reports for administrators

### Error Handling Strategy
- Multiple authentication method fallbacks
- Automatic controller type detection
- Graceful degradation for partial failures
- Comprehensive logging to both file and console
- Detailed error messages with troubleshooting guidance

## Log Files and Monitoring

- `unifi_deployment.log`: Deployment progress, errors, and configuration changes
- `unifi_monitoring.log`: Policy validation, device monitoring, and performance metrics  
- `deployment_log_*.json`: Detailed deployment history with timestamps
- `policy_validation_report_*.json`: Structured validation reports

## Time-based Operations

### Maintenance Windows
- **IoT updates**: Sunday 02:00-04:00
- **Security scans**: Sunday 01:00-05:00  
- **System backups**: Daily 01:00-06:00

### Policy Schedules
- **Business hours** (Mon-Fri 08:00-18:00): Enhanced bandwidth, relaxed filtering
- **After hours & weekends**: Family-safe filtering, streaming optimization
- **Sleep time** (22:00-06:00): Strict filtering, minimal bandwidth

## Network Architecture Considerations

### VLAN Design Philosophy
Each VLAN serves a specific security zone with tailored policies:
- **High-trust zones** (Management, Corporate): Full internet, unlimited bandwidth
- **Medium-trust zones** (User Devices, Apple IoT): Controlled access, moderate bandwidth  
- **Low-trust zones** (General IoT, Automotive): Limited internet, minimal bandwidth
- **Isolated zones** (Guest, Quarantine): Restricted or no cross-VLAN communication

### QoS Implementation
8-tier traffic prioritization with DSCP marking:
1. **Critical** (EF): Network management - 20% guaranteed
2. **Real-time** (AF41): VoIP, video conferencing - 15% guaranteed  
3. **Business Critical** (AF31): Office apps, databases - 25% guaranteed
4. **Standard** (AF21): Web browsing, email - 20% guaranteed
5. **Multimedia** (AF22): Streaming services - 10% guaranteed
6. **IoT Services** (AF11): IoT communications - 5% guaranteed
7. **Bulk Transfer** (AF12): File transfers, backups - 5% guaranteed  
8. **Default** (BE): Unclassified traffic - Best effort

### Security Monitoring Integration
- Email notifications to admin@bozza.au
- Syslog integration to 192.168.10.100  
- SNMP traps for network management systems
- Webhook alerts to monitoring.bozza.au

This framework provides enterprise-grade network management with comprehensive automation, security, and monitoring capabilities specifically designed for UniFi UCG-Fiber deployments.