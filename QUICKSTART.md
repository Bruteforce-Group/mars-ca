# UniFi Policy Framework - Quick Start

## ✅ Installation Complete

All Python requirements have been successfully installed using a virtual environment approach to comply with macOS's externally managed Python environment (PEP 668).

### 📦 Installed Packages
- **requests 2.32.5** - HTTP library for UniFi API calls
- **urllib3 2.5.0** - HTTP client with SSL support
- **python-dotenv 1.1.1** - Environment variable management
- **tabulate 0.9.0** - Table formatting for reports

### 🗂️ Project Structure
```
mars-ca/
├── venv/                               # Python virtual environment
├── activate.sh                         # Environment activation script
├── deploy_unifi_policies.py           # Main deployment script
├── monitor_unifi_policies.py          # Monitoring and validation
├── requirements.txt                    # Python dependencies
├── README.md                          # Full documentation
└── [policy files...]                  # JSON/MD policy configurations
```

## 🚀 Quick Start Commands

### 1. Activate Environment
```bash
source activate.sh
```
This will:
- Activate the Python virtual environment
- Set up UniFi controller credentials
- Display current configuration status

### 2. Deploy Network Policies
```bash
python3 deploy_unifi_policies.py
```
This will:
- Connect to mars.int.bozza.au controller
- Create 10 VLANs with proper subnets
- Configure device groups and classification
- Deploy firewall rules using Object Policy
- Set up QoS and bandwidth management
- Generate deployment logs

### 3. Monitor and Validate
```bash
python3 monitor_unifi_policies.py
```
This will:
- Validate deployed policies
- Check device classification accuracy
- Monitor network performance
- Generate status reports
- Save detailed validation logs

## 🔧 Environment Variables

The following credentials are configured from your Warp environment:
- `UNIFI_CONTROLLER_HOSTNAME_MARS=mars.int.bozza.au`
- `UNIFI_USERNAME_MARS=root`
- `UNIFI_PASSWORD_MARS=[configured]`
- `UNIFI_API_KEY_MARS=[configured]`

## 📊 What Gets Deployed

### Network Segmentation (10 VLANs)
- **VLAN 1**: Management (UCG-Fiber, switches, APs)
- **VLAN 10**: Corporate servers and admin workstations
- **VLAN 20**: User devices (iPhones, Macs)
- **VLAN 30**: Apple IoT (Apple TV, HomePods)
- **VLAN 40**: General IoT (Tuya devices)
- **VLAN 50**: Security cameras and NVR
- **VLAN 60**: Tesla vehicles and chargers
- **VLAN 70**: Printers and scanners
- **VLAN 80**: Guest network access
- **VLAN 90**: Quarantine zone

### Security Features
- Zero-trust architecture with default-deny
- Advanced threat detection and quarantine
- Geo-IP blocking for high-risk countries
- Content filtering by device category
- Comprehensive security logging

### QoS Management
- 8-tier traffic prioritization
- DSCP marking for all traffic classes
- Time-based bandwidth adjustments
- Application-aware traffic shaping
- WAN load balancing and failover

### Time-based Policies
- Business hours bandwidth optimization
- Family-safe content filtering
- Sleep time restrictions
- Automated maintenance windows
- Dynamic policy adjustments

## 🛠️ Troubleshooting

### Virtual Environment Issues
```bash
# Recreate if needed
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Connection Issues
```bash
# Test controller connectivity
ping mars.int.bozza.au

# Check credentials
echo $UNIFI_API_KEY_MARS
echo $UNIFI_USERNAME_MARS
```

### Policy Validation
```bash
# Check JSON syntax
python3 -m json.tool device-groups-policies.json
python3 -m json.tool firewall-traffic-policies.json
```

## 📝 Log Files
- `unifi_deployment.log` - Deployment progress and errors
- `unifi_monitoring.log` - Monitoring and validation logs
- `deployment_log_*.json` - Detailed deployment history
- `policy_validation_report_*.json` - Validation reports

## 🔄 Regular Operations

### Daily
- Monitor device classification accuracy
- Check for security alerts and quarantined devices

### Weekly  
- Review bandwidth utilization trends
- Validate firewall rule effectiveness
- Check system performance metrics

### Monthly
- Update threat intelligence feeds
- Review and optimize QoS policies
- Audit security compliance status

## 📞 Support

For issues or questions:
1. Check the logs in the respective .log files
2. Review the comprehensive README.md
3. Validate network connectivity to mars.int.bozza.au
4. Ensure all JSON policy files are valid

---

**Ready to deploy!** Run `source activate.sh` to get started.