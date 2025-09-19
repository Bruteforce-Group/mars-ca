# UniFi Network Policy Framework for UCG-Fiber

## Overview

This repository contains a comprehensive network policy framework designed specifically for UniFi UCG-Fiber deployments using the Object Policy system. The framework implements enterprise-grade security, performance optimization, and monitoring best practices.

## Features

- **Zero Trust Network Architecture**: Default-deny policies with explicit allow rules
- **Advanced Device Classification**: Automatic device grouping and VLAN assignment
- **Comprehensive QoS Management**: Bandwidth prioritization and traffic shaping
- **Time-based Scheduling**: Dynamic policy enforcement based on time and usage patterns
- **Extensive Monitoring**: Real-time performance and security monitoring
- **Automated Deployment**: Python scripts for policy deployment and validation

## Architecture Components

### Network Segmentation
- **10 VLANs** with role-based segregation
- **Zero Trust** micro-segmentation
- **Automatic device classification** and assignment

### Security Framework
- **Multi-layer firewall rules** with Object Policy
- **Threat detection and response** automation
- **Content filtering** and geo-blocking
- **Intrusion prevention** system integration

### Performance Optimization
- **8-tier QoS hierarchy** with DSCP marking
- **Adaptive bandwidth management** with time-based adjustments
- **WAN load balancing** and failover
- **Application-aware traffic prioritization**

## File Structure

```
mars-ca/
├── README.md                           # This file
├── network-segmentation-strategy.md    # Network architecture documentation
├── device-groups-policies.json         # Device classification and grouping
├── firewall-traffic-policies.json      # Firewall rules and traffic policies
├── qos-bandwidth-policies.json         # QoS and bandwidth management
├── scheduling-policies.json            # Time-based policy schedules
├── monitoring-logging-policies.json    # Monitoring and alerting configuration
├── deploy_unifi_policies.py           # Deployment automation script
├── monitor_unifi_policies.py          # Monitoring and validation script
└── requirements.txt                    # Python dependencies
```

## Prerequisites

### Hardware Requirements
- UniFi UCG-Fiber gateway
- UniFi Network Application (controller)
- Compatible UniFi switches and access points

### Software Requirements
- Python 3.8+
- UniFi Network Application 7.5+
- Required Python packages (see requirements.txt)

### Network Requirements
- Access to UniFi controller (mars.int.bozza.au)
- Valid API credentials or username/password
- Administrative privileges on the network

## Installation

### 1. Environment Setup

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

### 2. Create Requirements File

```bash
cat > requirements.txt << EOF
requests>=2.31.0
urllib3>=1.26.0
python-dotenv>=0.19.0
tabulate>=0.9.0
EOF
```

### 3. Verify Controller Access

```bash
# Test connectivity to the controller
ping mars.int.bozza.au

# Test API access (optional)
python3 -c "
import requests
import os
requests.packages.urllib3.disable_warnings()
response = requests.get('https://mars.int.bozza.au/api/self', 
                       headers={'X-API-Key': os.getenv('UNIFI_API_KEY_MARS')}, 
                       verify=False)
print(f'Status: {response.status_code}')
"
```

## Deployment

### Phase 1: Pre-deployment Validation

```bash
# Review the network segmentation strategy
less network-segmentation-strategy.md

# Validate policy configurations
python3 -c "
import json
for file in ['device-groups-policies.json', 'firewall-traffic-policies.json', 'qos-bandwidth-policies.json']:
    with open(file) as f:
        data = json.load(f)
        print(f'{file}: ✓ Valid JSON')
"
```

### Phase 2: Staged Deployment

```bash
# Deploy all policies (interactive)
python3 deploy_unifi_policies.py

# Or deploy with confirmation bypass (advanced users)
echo "y" | python3 deploy_unifi_policies.py
```

The deployment script will:
1. Authenticate with the controller
2. Create VLAN networks and subnets
3. Configure firewall groups
4. Deploy firewall rules
5. Set up QoS profiles
6. Generate deployment logs

### Phase 3: Validation and Monitoring

```bash
# Run policy validation
python3 monitor_unifi_policies.py

# Schedule regular monitoring (optional)
crontab -e
# Add: 0 */6 * * * cd /path/to/mars-ca && python3 monitor_unifi_policies.py
```

## Network Design

### VLAN Architecture

| VLAN | Network | Purpose | Security Level |
|------|---------|---------|----------------|
| 1 | 192.168.1.0/24 | Management Infrastructure | HIGH |
| 10 | 192.168.10.0/24 | Corporate Servers | HIGH |
| 20 | 192.168.20.0/24 | User Devices | MEDIUM-HIGH |
| 30 | 192.168.30.0/24 | IoT Trusted (Apple) | MEDIUM |
| 40 | 192.168.40.0/24 | IoT General (Tuya) | MEDIUM |
| 50 | 192.168.50.0/24 | Security Cameras | MEDIUM |
| 60 | 192.168.60.0/24 | Automotive (Tesla) | MEDIUM |
| 70 | 192.168.70.0/24 | Print Services | MEDIUM |
| 80 | 192.168.80.0/24 | Guest Access | LOW |
| 90 | 192.168.90.0/24 | Quarantine | ISOLATED |

### Traffic Policies

#### Internet Access Hierarchy
1. **Full Internet**: Management, Servers, User Devices
2. **Restricted Internet**: iPhones, Apple IoT, Cameras
3. **Limited Internet**: General IoT, Tesla, Printers
4. **Guest Internet**: Isolated guest access
5. **No Internet**: Quarantine zone

#### Inter-VLAN Rules
- Management → All VLANs (monitoring/management)
- Corporate ↔ User Devices (file sharing)
- User Devices → Print Services (printing)
- All VLANs → Corporate (DNS, NTP, updates)
- Security → Corporate (video storage)
- **Blocked**: Direct IoT-to-IoT communication

### QoS Classes

| Priority | Class | DSCP | Bandwidth | Applications |
|----------|-------|------|-----------|--------------|
| 1 | Critical | EF | 20% guaranteed | Network management |
| 2 | Real-time | AF41 | 15% guaranteed | VoIP, video conferencing |
| 3 | Business Critical | AF31 | 25% guaranteed | Office apps, databases |
| 4 | Standard | AF21 | 20% guaranteed | Web browsing, email |
| 5 | Multimedia | AF22 | 10% guaranteed | Streaming services |
| 6 | IoT Services | AF11 | 5% guaranteed | IoT communications |
| 7 | Bulk Transfer | AF12 | 5% guaranteed | File transfers, backups |
| 8 | Default | BE | Best effort | Unclassified traffic |

## Security Features

### Threat Detection
- **Signature-based IDS/IPS**
- **Behavioral anomaly detection**
- **Geo-IP blocking** (China, Russia, North Korea)
- **Reputation filtering**
- **Automatic quarantine** for threats

### Content Filtering
- **Family Safe**: Blocks adult, gambling, violence, drugs
- **IoT Security**: Allows only vendor updates and time servers
- **Strict**: Blocks social media, streaming, gaming

### Compliance
- **ISO 27001** controls implementation
- **NIST Cybersecurity Framework** alignment
- **Australian Privacy Principles** adherence
- **Comprehensive audit logging**

## Monitoring and Alerting

### Key Metrics
- **Bandwidth utilization** per VLAN and device
- **Latency and jitter** measurements
- **Security event detection**
- **Device classification accuracy**
- **Policy compliance status**

### Alert Channels
- **Email notifications** to admin@bozza.au
- **Syslog integration** to 192.168.10.100
- **SNMP traps** for network management
- **Webhook alerts** to monitoring.bozza.au

### Reporting
- **Weekly security summary**
- **Monthly performance report**
- **Daily device health report**
- **Real-time dashboards**

## Time-based Policies

### Business Hours (Mon-Fri 08:00-18:00)
- Enhanced bandwidth for corporate devices
- Relaxed content filtering for business use
- Priority elevation for productivity apps

### After Hours & Weekends
- Family-safe content filtering
- Bandwidth optimization for streaming
- Reduced limits for non-essential traffic

### Sleep Time (22:00-06:00)
- Strict content filtering
- Social media blocking
- Minimal bandwidth allocation

### Maintenance Windows
- **IoT updates**: Sunday 02:00-04:00
- **Security scans**: Sunday 01:00-05:00
- **System backups**: Daily 01:00-06:00

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

#### Policy Deployment Failures
```bash
# Check deployment logs
tail -f unifi_deployment.log

# Validate JSON configuration
python3 -m json.tool device-groups-policies.json

# Re-run specific deployment phase
python3 -c "
from deploy_unifi_policies import *
# Add debugging code here
"
```

#### Device Classification Issues
```bash
# Run device validation
python3 monitor_unifi_policies.py | grep -A 10 "Device Distribution"

# Check unclassified devices
python3 -c "
from monitor_unifi_policies import *
# Add device inspection code here
"
```

### Log Locations
- **Deployment logs**: `unifi_deployment.log`
- **Monitoring logs**: `unifi_monitoring.log`
- **Validation reports**: `policy_validation_report_*.json`
- **Deployment history**: `deployment_log_*.json`

## Best Practices

### Security
- **Regularly update** threat intelligence feeds
- **Review quarantined devices** weekly
- **Monitor failed authentication** attempts
- **Audit firewall logs** for anomalies

### Performance
- **Monitor bandwidth utilization** trends
- **Adjust QoS policies** based on usage patterns
- **Review device classification** accuracy monthly
- **Optimize VLAN assignments** as needed

### Maintenance
- **Backup configurations** before changes
- **Test policy changes** in staging environment
- **Document all modifications**
- **Schedule regular policy reviews**

## Support and Documentation

### Resources
- **UniFi Documentation**: [help.ui.com](https://help.ui.com)
- **UCG-Fiber Guide**: UniFi console documentation
- **Object Policy Reference**: UniFi Network Application help

### Contact Information
- **Network Administrator**: admin@bozza.au
- **Security Team**: security@bozza.au
- **Technical Support**: Based on your internal procedures

## License and Compliance

This configuration framework is designed for the specific environment and requirements of the Mars network infrastructure. Modifications should be reviewed for security and compliance implications.

---

**Last Updated**: September 2024  
**Version**: 1.0  
**Environment**: Mars UCG-Fiber Production Network