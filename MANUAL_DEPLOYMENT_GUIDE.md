# UniFi UCG-Fiber Manual Deployment Guide

## 📋 Overview

This guide provides step-by-step instructions to manually implement the comprehensive network policy framework through the UniFi Network Application web interface at `https://mars.int.bozza.au`.

**⚠️ Important**: These policies implement enterprise-grade security and will significantly change your network structure. Ensure you have administrative access and understand the implications before proceeding.

## 🎯 Deployment Summary

**What will be implemented:**
- 10 VLANs with role-based network segmentation  
- Zero-trust firewall architecture with Object Policy
- 8-tier QoS hierarchy with bandwidth management
- Automatic device classification and VLAN assignment
- Advanced security features and comprehensive logging

## 📶 Phase 1: Network/VLAN Creation

Navigate to **Settings > Networks** and create the following VLANs:

### VLAN 1 - Management Infrastructure
- **Name**: `MGMT_Infrastructure`
- **VLAN ID**: `1` (Default/Native)
- **Gateway/Subnet**: `192.168.1.1/24`
- **DHCP Range**: `192.168.1.10 - 192.168.1.50`
- **Purpose**: Network infrastructure devices (UCG-Fiber, switches, APs)

### VLAN 10 - Corporate Servers  
- **Name**: `Corporate_Servers`
- **VLAN ID**: `10`
- **Gateway/Subnet**: `192.168.10.1/24`
- **DHCP Range**: `192.168.10.10 - 192.168.10.254`
- **DNS**: `192.168.1.1, 1.1.1.1`
- **Purpose**: Internal servers and admin workstations

### VLAN 20 - User Devices
- **Name**: `User_Devices`
- **VLAN ID**: `20`
- **Gateway/Subnet**: `192.168.20.1/24`
- **DHCP Range**: `192.168.20.10 - 192.168.20.254`
- **DNS**: `192.168.1.1, 1.1.1.1`
- **Purpose**: Mac computers, iPhones, personal devices

### VLAN 30 - Apple IoT
- **Name**: `Apple_IoT`
- **VLAN ID**: `30`
- **Gateway/Subnet**: `192.168.30.1/24`
- **DHCP Range**: `192.168.30.10 - 192.168.30.254`
- **DNS**: `192.168.1.1, 1.1.1.1`
- **Purpose**: Apple TV, HomePods, Apple Watch

### VLAN 40 - General IoT
- **Name**: `General_IoT`
- **VLAN ID**: `40`
- **Gateway/Subnet**: `192.168.40.1/24`
- **DHCP Range**: `192.168.40.10 - 192.168.40.254`
- **DNS**: `192.168.1.1, 1.1.1.1`
- **Purpose**: Tuya devices, smart home equipment

### VLAN 50 - Security Cameras
- **Name**: `Security_Cameras`
- **VLAN ID**: `50`
- **Gateway/Subnet**: `192.168.50.1/24`
- **DHCP Range**: `192.168.50.10 - 192.168.50.254`
- **DNS**: `192.168.1.1, 1.1.1.1`
- **Purpose**: IP cameras, NVR systems

### VLAN 60 - Automotive
- **Name**: `Automotive`
- **VLAN ID**: `60`
- **Gateway/Subnet**: `192.168.60.1/24`
- **DHCP Range**: `192.168.60.10 - 192.168.60.254`
- **DNS**: `192.168.1.1, 1.1.1.1`
- **Purpose**: Tesla vehicles, car chargers

### VLAN 70 - Print Services
- **Name**: `Print_Services`
- **VLAN ID**: `70`
- **Gateway/Subnet**: `192.168.70.1/24`
- **DHCP Range**: `192.168.70.10 - 192.168.70.254`
- **DNS**: `192.168.1.1, 1.1.1.1`
- **Purpose**: Printers, scanners, print servers

### VLAN 80 - Guest Network
- **Name**: `Guest_Network`
- **VLAN ID**: `80`
- **Gateway/Subnet**: `192.168.80.1/24`
- **DHCP Range**: `192.168.80.10 - 192.168.80.100`
- **DNS**: `1.1.1.1, 8.8.8.8`
- **Guest Policy**: Enabled
- **Internet Only**: Yes
- **Purpose**: Visitor device access

### VLAN 90 - Quarantine
- **Name**: `Quarantine_Zone`
- **VLAN ID**: `90`
- **Gateway/Subnet**: `192.168.90.1/24`
- **DHCP Range**: `192.168.90.10 - 192.168.90.50`
- **Internet Access**: Blocked
- **Purpose**: Isolated suspicious devices

## 🔥 Phase 2: Firewall Configuration

Navigate to **Settings > Security > Firewall**

### Internet Access Rules (WAN OUT)

#### 1. Management Full Access
- **Name**: `MGMT_Full_Internet`
- **Action**: Accept
- **Source**: Network Group `MGMT_Infrastructure`
- **Destination**: Internet
- **Protocol**: All
- **Logging**: Enabled

#### 2. Corporate Full Access  
- **Name**: `Corporate_Full_Internet`
- **Action**: Accept
- **Source**: Network Group `Corporate_Servers`, `User_Devices`
- **Destination**: Internet
- **Protocol**: All
- **Ports**: All
- **Logging**: Connections

#### 3. IoT Restricted Access
- **Name**: `IoT_Restricted_Internet`
- **Action**: Accept
- **Source**: Network Group `Apple_IoT`, `Security_Cameras`
- **Destination**: Internet
- **Protocol**: TCP/UDP
- **Ports**: 80, 443, 53, 123
- **Logging**: All Connections

#### 4. IoT Limited Access
- **Name**: `IoT_Limited_Internet`
- **Action**: Accept  
- **Source**: Network Group `General_IoT`, `Automotive`, `Print_Services`
- **Destination**: Internet
- **Protocol**: TCP/UDP
- **Ports**: 80, 443, 53, 123
- **Logging**: All Connections

#### 5. Guest Internet Access
- **Name**: `Guest_Internet_Access`
- **Action**: Accept
- **Source**: Network Group `Guest_Network`
- **Destination**: Internet
- **Protocol**: TCP/UDP
- **Ports**: 80, 443, 53
- **Logging**: All Connections
- **Content Filtering**: Strict

#### 6. Block Quarantine Internet
- **Name**: `Block_Quarantine_Internet`
- **Action**: Drop
- **Source**: Network Group `Quarantine_Zone`
- **Destination**: Internet
- **Protocol**: All
- **Logging**: All Attempts

### Inter-VLAN Rules (LAN LOCAL)

#### 1. Management Access All
- **Name**: `MGMT_Access_All_VLANs`
- **Action**: Accept
- **Source**: Network Group `MGMT_Infrastructure`
- **Destination**: All Networks
- **Protocol**: All
- **Logging**: Connections

#### 2. Server-User Communication
- **Name**: `Server_User_Access`
- **Action**: Accept
- **Source**: Network Group `Corporate_Servers`
- **Destination**: Network Group `User_Devices`
- **Protocol**: TCP/UDP
- **Ports**: 80, 443, 22, 5000-5100, 8000-8100
- **Logging**: Connections

#### 3. User-Server Communication
- **Name**: `User_Server_Access`
- **Action**: Accept
- **Source**: Network Group `User_Devices`
- **Destination**: Network Group `Corporate_Servers`
- **Protocol**: TCP/UDP  
- **Ports**: 80, 443, 22, 3389, 5900, 5000-5100
- **Logging**: Connections

#### 4. User-Printer Access
- **Name**: `User_Printer_Access`
- **Action**: Accept
- **Source**: Network Group `User_Devices`
- **Destination**: Network Group `Print_Services`
- **Protocol**: TCP/UDP
- **Ports**: 515, 631, 9100
- **Logging**: Connections

#### 5. Camera-Server Access
- **Name**: `Camera_Server_Access`
- **Action**: Accept
- **Source**: Network Group `Security_Cameras`
- **Destination**: Network Group `Corporate_Servers`
- **Protocol**: TCP/UDP
- **Ports**: 80, 443, 554, 8080
- **Logging**: Connections

#### 6. DNS Access for All
- **Name**: `Universal_DNS_Access`
- **Action**: Accept
- **Source**: All Networks
- **Destination**: Network Group `Corporate_Servers`, `MGMT_Infrastructure`
- **Protocol**: TCP/UDP
- **Ports**: 53
- **Logging**: None

#### 7. NTP Access for All
- **Name**: `Universal_NTP_Access`
- **Action**: Accept
- **Source**: All Networks  
- **Destination**: Network Group `Corporate_Servers`, `MGMT_Infrastructure`
- **Protocol**: UDP
- **Ports**: 123
- **Logging**: None

#### 8. Block IoT Cross-Communication
- **Name**: `Block_IoT_Cross_Talk`
- **Action**: Drop
- **Source**: Network Group `Apple_IoT`, `General_IoT`, `Security_Cameras`, `Automotive`, `Print_Services`
- **Destination**: Network Group `Apple_IoT`, `General_IoT`, `Security_Cameras`, `Automotive`, `Print_Services`
- **Protocol**: All
- **Logging**: All Attempts

#### 9. Quarantine Isolation
- **Name**: `Quarantine_Total_Isolation`
- **Action**: Drop
- **Source**: Network Group `Quarantine_Zone`
- **Destination**: All Networks (except `MGMT_Infrastructure`)
- **Protocol**: All
- **Logging**: All Attempts

## ⚡ Phase 3: Traffic Management (QoS)

Navigate to **Settings > Traffic Management**

### Traffic Identification Rules

#### 1. Critical Network Traffic
- **Name**: `Critical_Network_Management`
- **Categories**: Network Management, Routing Protocols
- **DSCP**: EF (46)
- **Bandwidth**: 20% guaranteed
- **Networks**: `MGMT_Infrastructure`

#### 2. Real-time Communications  
- **Name**: `Real_Time_Communications`
- **Categories**: VoIP, Video Conferencing
- **Applications**: Zoom, Teams, WebEx, Skype, FaceTime
- **DSCP**: AF41 (34)
- **Bandwidth**: 15% guaranteed
- **Networks**: `User_Devices`

#### 3. Business Critical Applications
- **Name**: `Business_Critical_Apps`
- **Categories**: Productivity, Database
- **Applications**: Office365, Google Workspace, Salesforce
- **DSCP**: AF31 (26)
- **Bandwidth**: 25% guaranteed
- **Networks**: `Corporate_Servers`, `User_Devices`

#### 4. Standard Web Traffic
- **Name**: `Standard_Web_Traffic`
- **Categories**: Web Browsing, Email
- **Applications**: HTTP, HTTPS, IMAP, SMTP
- **DSCP**: AF21 (18)
- **Bandwidth**: 20% guaranteed
- **Networks**: `User_Devices`

#### 5. Multimedia Streaming
- **Name**: `Multimedia_Streaming`
- **Categories**: Streaming Media
- **Applications**: Netflix, YouTube, Spotify, Apple Music
- **DSCP**: AF22 (20)
- **Bandwidth**: 10% guaranteed
- **Networks**: `User_Devices`, `Apple_IoT`

#### 6. IoT Communications
- **Name**: `IoT_Device_Traffic`
- **Categories**: IoT, Sensor Data
- **DSCP**: AF11 (10)
- **Bandwidth**: 5% guaranteed
- **Networks**: `Apple_IoT`, `General_IoT`, `Security_Cameras`, `Automotive`

#### 7. Bulk Transfer
- **Name**: `Bulk_Data_Transfer`
- **Categories**: File Transfer, Backup
- **Applications**: FTP, Rsync, Cloud Sync
- **DSCP**: AF12 (12)
- **Bandwidth**: 5% guaranteed
- **Networks**: `Corporate_Servers`, `User_Devices`

#### 8. Default Best Effort
- **Name**: `Default_Traffic`
- **Categories**: Unclassified
- **DSCP**: BE (0)
- **Bandwidth**: Best effort
- **Networks**: `Guest_Network`, `Quarantine_Zone`

### Bandwidth Profiles

#### Create the following profiles in **Traffic Management > Bandwidth Profiles**:

1. **Management_Unlimited**: Unlimited/Unlimited
2. **Server_High**: 500 Mbps down / 500 Mbps up
3. **User_Premium**: 100 Mbps down / 20 Mbps up  
4. **Mobile_Standard**: 50 Mbps down / 10 Mbps up
5. **Apple_IoT_Limited**: 30 Mbps down / 5 Mbps up
6. **General_IoT_Basic**: 5 Mbps down / 1 Mbps up
7. **Camera_Medium**: 20 Mbps down / 5 Mbps up
8. **Tesla_Automotive**: 10 Mbps down / 2 Mbps up
9. **Printer_Basic**: 5 Mbps down / 1 Mbps up
10. **Guest_Restricted**: 25 Mbps down / 5 Mbps up
11. **Quarantine_Minimal**: 1 Mbps down / 1 Mbps up

## 🎯 Phase 4: Device Classification

Navigate to **Clients > Device Classification**

### Automatic Classification Rules

Configure automatic VLAN assignment based on:

#### Device Fingerprinting
- **iPhones**: Auto-assign to `User_Devices` (VLAN 20)
- **macOS devices**: Auto-assign to `User_Devices` (VLAN 20)  
- **Apple TV, HomePod**: Auto-assign to `Apple_IoT` (VLAN 30)
- **IP Cameras**: Auto-assign to `Security_Cameras` (VLAN 50)
- **Tesla**: Auto-assign to `Automotive` (VLAN 60)
- **Printers**: Auto-assign to `Print_Services` (VLAN 70)

#### MAC OUI Rules
- **Apple devices (28:37:37, BC:52:B7, 9C:04:EB)**: 
  - iPhones/iPads → VLAN 20
  - Apple TV/HomePod → VLAN 30
- **UniFi devices (24:5A:4C)**: → VLAN 1

#### Manual Assignment
For devices that can't be automatically classified, manually assign to appropriate VLANs based on their purpose.

## 🛡️ Phase 5: Security Features

### Content Filtering
Navigate to **Security > Content Filtering**

#### Family Safe Filter (for User Devices)
- **Block**: Adult content, gambling, violence, drugs, malware
- **Allow**: Business, education, entertainment, social media
- **Apply to**: `User_Devices` network

#### IoT Security Filter (for IoT devices)  
- **Block**: All categories except vendor updates
- **Allow**: Device manufacturer domains, time servers
- **Apply to**: `Apple_IoT`, `General_IoT`, `Security_Cameras`, `Automotive`, `Print_Services`

#### Strict Filter (for Guests)
- **Block**: Social media, streaming, gaming, P2P
- **Allow**: Basic web, email, productivity sites
- **Apply to**: `Guest_Network`

### Intrusion Detection/Prevention
Navigate to **Security > IDS/IPS**

#### Enable IDS/IPS with:
- **Signature-based detection**: Enabled
- **Behavioral analysis**: Enabled  
- **Geo-IP blocking**: Enable blocking for China, Russia, North Korea
- **Automatic quarantine**: Move suspicious devices to VLAN 90
- **Alert notifications**: Email to admin@bozza.au

### Threat Management
Navigate to **Security > Threat Management**

#### Configure:
- **Malware blocking**: Enabled
- **Command & control blocking**: Enabled
- **Reputation filtering**: Enabled
- **DNS filtering**: Enabled for malicious domains
- **Auto-quarantine threshold**: 3 suspicious events

## 📊 Phase 6: Monitoring & Logging

### Statistics Collection
Navigate to **Settings > System > Advanced**

#### Enable:
- **Deep Packet Inspection (DPI)**: Enabled
- **Store DPI statistics**: 90 days
- **Traffic identification**: Enabled
- **Application statistics**: Enabled

### Logging Configuration  
Navigate to **Settings > System > Logging**

#### Configure logging levels:
- **Firewall**: Info level (blocked connections)
- **Wireless**: Warning level
- **System**: Warning level
- **Guest control**: Info level
- **IDS events**: All levels

#### Remote Logging:
- **Syslog server**: 192.168.10.100 (if available)
- **Facility**: Local0
- **Severity mapping**: Critical=Alert, High=Error, Medium=Warning

### Alerting
Navigate to **Settings > Alerts**

#### Configure alerts for:
- **Intrusion attempts**: Immediate email alert
- **Device quarantine**: Immediate email alert
- **High bandwidth usage**: Alert at 80% utilization
- **VPN connection failures**: Email alert
- **Firmware updates available**: Weekly email digest

## 📈 Phase 7: Time-Based Policies (Optional)

Navigate to **Settings > Profiles > Schedules**

### Create time-based bandwidth adjustments:

#### Business Hours (Mon-Fri 8AM-6PM)  
- **User devices**: Boost to 200 Mbps down / 50 Mbps up
- **Priority**: Increase business app priority by +1

#### Evening Hours (6PM-11PM)
- **Streaming**: Enable full bandwidth for multimedia
- **Gaming**: Standard priority
- **IoT**: Standard limits

#### Sleep Hours (11PM-6AM)
- **User devices**: Reduce to 50 Mbps down / 10 Mbps up
- **IoT updates**: Allow full bandwidth for firmware updates
- **Content filtering**: Stricter rules active

#### Weekend Schedule
- **Family time**: Prioritize multimedia streaming
- **IoT maintenance**: Sunday 2AM-4AM full bandwidth for updates

## ✅ Phase 8: Testing & Validation

### Post-Deployment Checklist

1. **VLAN Connectivity**:
   - Test device connectivity within each VLAN
   - Verify inter-VLAN rules work as expected
   - Test internet access per VLAN restrictions

2. **Device Classification**:
   - Connect test devices and verify auto-assignment
   - Check unclassified devices and manually assign
   - Validate bandwidth profiles are applied

3. **Firewall Rules**:
   - Test blocked traffic is actually blocked
   - Verify allowed traffic flows correctly  
   - Test quarantine functionality

4. **QoS Performance**:
   - Run bandwidth tests per device type
   - Test video conferencing quality
   - Verify traffic prioritization works

5. **Security Features**:
   - Test content filtering on different VLANs
   - Verify geo-IP blocking
   - Test IDS/IPS detection and quarantine

## 🔧 Troubleshooting

### Common Issues

#### Devices Not Getting Expected VLAN
- Check device fingerprinting rules
- Verify MAC OUI classification
- Manually assign problematic devices

#### Firewall Rules Not Working
- Check rule order (more specific rules first)
- Verify network group memberships
- Test with logging enabled to see rule hits

#### QoS Not Effective
- Ensure DPI is enabled for application identification
- Check bandwidth profile assignments
- Verify upstream/downstream settings match ISP speeds

#### Performance Issues  
- Monitor VLAN utilization in Statistics
- Check for broadcast storms between VLANs
- Verify hardware capacity isn't exceeded

## 📞 Support Resources

- **UniFi Documentation**: https://help.ui.com/
- **UCG-Fiber Specific**: Check UniFi Console documentation
- **Community Forums**: https://community.ui.com/

---

**⚠️ Important Notes:**
- This deployment will significantly change your network structure
- Test in phases rather than implementing everything at once
- Keep a backup of current configuration before starting
- Have a rollback plan if issues occur
- Monitor network performance closely after deployment

**Estimated Implementation Time**: 4-6 hours for full deployment
**Recommended Approach**: Phase-by-phase implementation with testing between each phase