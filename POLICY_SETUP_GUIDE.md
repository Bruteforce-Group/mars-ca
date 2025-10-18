# 🛡️ UniFi Zero-Trust Policy Setup Guide

## 📋 Overview

Use these exact policy configurations in your UniFi interface to establish zero-trust security.

## 🎯 Step 1: Firewall Policies

### **Policy 1: Management Infrastructure Access**
```
Type: Firewall
Source: 
  - List → MGMT_Infrastructure_Devices
Destination: Any
Protocol: All
Action: Accept
```

### **Policy 2: Management Ports Protection**
```
Type: Firewall
Source: Any
Destination: 
  - List → Management_Ports
Protocol: TCP/UDP
Action: Drop (except from MGMT_Infrastructure_Devices)
```

### **Policy 3: Corporate Server Access**
```
Type: Firewall
Source: 
  - List → Corporate_Server_Devices
  - List → Corporate_Servers
Destination:
  - List → Web_Services_Ports
Protocol: TCP/UDP
Action: Accept
```

### **Policy 4: User Workstation Access**
```
Type: Firewall
Source:
  - List → Mac_Computer_Devices
Destination:
  - List → Corporate_Servers
  - List → Apple_IoT_Devices
Protocol: All
Action: Accept
```

### **Policy 5: Apple IoT Segmentation**
```
Type: Firewall
Source:
  - List → Apple_IoT_Devices
Destination:
  - List → IoT_Basic_Ports
Protocol: TCP/UDP
Action: Accept
```

## 🎯 Step 2: QoS Policies

### **Policy 1: Management Priority**
```
Type: QoS
Source:
  - List → MGMT_Infrastructure_Devices
QoS Behavior: Prioritize
Interface: All
```

### **Policy 2: Server Bandwidth**
```
Type: QoS
Source:
  - List → Corporate_Server_Devices
QoS Behavior: Limit
Download Limit: 500 Mbps
Upload Limit: 500 Mbps
```

### **Policy 3: IoT Rate Limiting**
```
Type: QoS
Source:
  - List → Apple_IoT_Devices
  - List → General_IoT_Devices
QoS Behavior: Limit
Download Limit: 100 Mbps
Upload Limit: 50 Mbps
```

## 🎯 Step 3: NAT Policies

### **Policy 1: IoT NAT Isolation**
```
Type: NAT
Type: Masquerade
Source:
  - List → Apple_IoT_Devices
  - List → General_IoT_Devices
Interface/VPN Tunnel: Telstra 1000/400 FTTP v1
IP Version: IPv4
Protocol: All
```

### **Policy 2: Management Direct Access**
```
Type: NAT
Type: Masquerade
Source:
  - List → MGMT_Infrastructure_Devices
Interface/VPN Tunnel: Telstra 1000/400 FTTP v1
IP Version: IPv4
Protocol: All
```

## 🔒 Final Security Policies

### **Default Drop Policy (LAST)**
```
Type: Firewall
Source: Any
Destination: Any
Protocol: All
Action: Drop
Notes: "Zero-trust default deny"
```

## 📝 Device Group Assignments

For these policies to work, assign devices to groups:

### **Management Infrastructure:**
- upstairs---study
- lounge-room
- backup
- g5-pro
- driveway

### **Corporate Servers:**
- truenas
- ringring (Fing Network Agent)

### **User Workstations:**
- Boz-MBP-M3-Max

### **Apple IoT:**
- ControlAppleTV2

## 🔍 Verification Steps

1. **Check Device Groups**
   - Settings → Objects → Devices tab
   - Ensure all devices are assigned to correct groups

2. **Verify Policies**
   - Settings → Objects → Check all policies are active
   - Settings → Firewall → Verify rules are generated

3. **Test Connectivity**
   - Management devices can access everything
   - User workstation can access servers and Apple IoT
   - IoT devices have limited internet only
   - Everything else is blocked by default

## ⚠️ Important Notes

1. **Order Matters**: Create policies in the order listed
2. **Default Deny**: Always add the default drop policy last
3. **Group Assignment**: Must be done before policies take effect
4. **Testing**: Test each policy as you create it
5. **Backup**: Make a backup before starting

## 🛟 Emergency Recovery

If you lose access:
1. Connect directly to UniFi console
2. Navigate to Settings → Objects
3. Disable the blocking policies
4. Re-enable one by one after fixing