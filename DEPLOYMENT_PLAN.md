# UniFi Network Policy Framework - Deployment Plan

## 🎯 **Deployment Overview**

**Objective**: Transform single flat network into enterprise-grade 10-VLAN zero-trust architecture
**Timeline**: Phased deployment over multiple sessions
**Risk Level**: HIGH - Fundamental network architecture change

---

## 📊 **Current State Analysis**

### **Existing Configuration**
- **Controller**: UCG-Fiber (mars.int.bozza.au) - UniFi OS 9.5.12
- **Network**: Single "Default" corporate network (flat topology)
- **Devices**: 5 network devices (2x USW switches, 2x UAP, 1x UDM)
- **Clients**: 8 connected devices (no current classification)
- **Security**: 45 WAN-focused firewall rules, 1 firewall group
- **QoS**: None configured

### **Target Architecture**
- **10 VLANs** with role-based segmentation
- **Zero-trust firewall** with default-deny policies
- **8-tier QoS hierarchy** with DSCP marking
- **Automated device classification** and VLAN assignment
- **Time-based policy enforcement**
- **Advanced threat detection** and monitoring

---

## 🚦 **Risk Assessment Matrix**

| Phase | Risk Level | Impact | Rollback Time | Dependencies |
|-------|------------|--------|---------------|--------------|
| **Phase 1** | 🟡 LOW | Network expansion only | 5 minutes | None |
| **Phase 2** | 🟠 MEDIUM | Device grouping | 10 minutes | Phase 1 |
| **Phase 3** | 🔴 HIGH | Traffic flow changes | 15 minutes | Phases 1-2 |
| **Phase 4** | 🟢 LOW | Performance optimization | 5 minutes | Phases 1-3 |

---

## 📋 **Phase-by-Phase Deployment Plan**

### **PHASE 1: Network Foundation** 🟡 LOW RISK

**Objective**: Create VLAN infrastructure without affecting current traffic

#### **What Will Happen:**
1. ✅ Create 10 new VLAN networks alongside existing "Default" network
2. ✅ Configure DHCP scopes for each VLAN
3. ✅ Set up inter-VLAN routing (initially permissive)
4. ✅ **NO devices will be moved** - all remain on current network

#### **Networks to Create:**
```
VLAN 1  - Management (192.168.1.0/24)    - Infrastructure devices
VLAN 10 - Corporate (192.168.10.0/24)    - Servers & admin
VLAN 20 - User Devices (192.168.20.0/24) - Macs, iPhones  
VLAN 30 - Apple IoT (192.168.30.0/24)    - Apple TV, HomePods
VLAN 40 - General IoT (192.168.40.0/24)  - Smart home devices
VLAN 50 - Security (192.168.50.0/24)     - IP cameras, NVR
VLAN 60 - Automotive (192.168.60.0/24)   - Tesla, chargers
VLAN 70 - Print (192.168.70.0/24)        - Printers, scanners
VLAN 80 - Guest (192.168.80.0/24)        - Visitor access
VLAN 90 - Quarantine (192.168.90.0/24)   - Suspicious devices
```

#### **Impact Assessment:**
- ✅ **Zero downtime** - existing devices remain unchanged
- ✅ **Zero traffic disruption** - current network flows continue
- ✅ **Reversible** - new networks can be deleted without impact
- ⚠️ **Resource usage** - additional DHCP pools and routing tables

#### **Rollback Procedure:**
```bash
# If issues occur, delete newly created networks:
1. Access UniFi Console → Settings → Networks
2. Delete each VLAN network (1, 10, 20, 30, 40, 50, 60, 70, 80, 90)
3. Keep "Default" network unchanged
4. System returns to original state
```

---

### **PHASE 2: Device Classification** 🟠 MEDIUM RISK

**Objective**: Set up device groups and classification rules

#### **What Will Happen:**
1. Create firewall groups for each device type
2. Configure device fingerprinting and MAC OUI matching
3. Set up automatic classification rules
4. **Devices still remain on current network** but get classified

#### **Device Groups to Create:**
- Management Devices (UCG-Fiber, switches, APs)
- Corporate Servers (internal services)
- Mac Computers (macOS devices)
- iPhone Devices (iOS devices)
- Apple IoT (Apple TV, HomePods)
- General IoT (Tuya, smart home)
- Security Cameras (IP cameras, NVR)
- Automotive (Tesla, chargers)
- Printers (printers, scanners)
- Guest Devices (visitor devices)
- Quarantine (suspicious devices)

#### **Impact Assessment:**
- ✅ **No traffic changes** - classification only
- ⚠️ **Preparation for Phase 3** - rules are ready but not active
- ✅ **Easily reversible** - delete firewall groups

#### **Rollback Procedure:**
```bash
# Delete firewall groups if needed:
1. Access UniFi Console → Settings → Security → Firewall
2. Delete all newly created device groups
3. Classification stops but no network impact
```

---

### **PHASE 3: Zero-Trust Security** 🔴 HIGH RISK

**Objective**: Activate device VLAN assignment and inter-VLAN firewall rules

⚠️ **CRITICAL PHASE - MOST DISRUPTIVE**

#### **What Will Happen:**
1. **Devices will be automatically moved** to appropriate VLANs
2. **Inter-VLAN firewall rules activated** (default-deny)
3. **Explicit allow rules** for required communications
4. **Advanced threat protection enabled**

#### **Expected Device Movement:**
Based on current 8 connected devices, expected classification:
- **Infrastructure devices** → VLAN 1 (Management)
- **Mac computers** → VLAN 20 (User Devices)  
- **iPhones/iOS devices** → VLAN 20 (User Devices)
- **Smart home devices** → VLAN 40 (General IoT)
- **Any cameras** → VLAN 50 (Security)
- **Printers** → VLAN 70 (Print Services)

#### **Traffic Flow Changes:**
- **Before**: All devices can communicate freely
- **After**: Communication restricted by firewall rules
  - Management can access all VLANs
  - User devices can access servers and printers
  - IoT devices have limited internet access
  - Cross-IoT communication blocked

#### **Impact Assessment:**
- 🔴 **HIGH IMPACT** - Fundamental communication changes
- ⚠️ **Potential connectivity issues** if classification is wrong
- ⚠️ **Applications may break** if they depend on current topology
- ✅ **Security significantly enhanced**

#### **Rollback Procedure:**
```bash
# EMERGENCY ROLLBACK (if connectivity issues):
1. Access UniFi Console → Settings → Security → Firewall
2. DISABLE all newly created firewall rules
3. Move all devices back to "Default" network manually
4. Delete VLAN assignments
5. Network returns to flat topology
```

---

### **PHASE 4: Performance Optimization** 🟢 LOW RISK

**Objective**: Enable QoS, bandwidth management, and time-based policies

#### **What Will Happen:**
1. Deploy 8-tier QoS profiles with DSCP marking
2. Configure bandwidth limits per device type
3. Enable time-based policy adjustments
4. Activate advanced monitoring and alerting

#### **QoS Classes:**
```
1. Critical (EF)       - Network management (20% guaranteed)
2. Real-time (AF41)    - VoIP, video calls (15% guaranteed)
3. Business (AF31)     - Office apps, databases (25% guaranteed)
4. Standard (AF21)     - Web browsing, email (20% guaranteed)
5. Multimedia (AF22)   - Streaming services (10% guaranteed)
6. IoT (AF11)          - IoT communications (5% guaranteed)
7. Bulk (AF12)         - File transfers, backups (5% guaranteed)
8. Default (BE)        - Unclassified traffic (best effort)
```

#### **Impact Assessment:**
- ✅ **Positive impact** - Better performance prioritization
- ✅ **No connectivity changes** - Only traffic prioritization
- ✅ **Easily adjustable** - Policies can be tuned
- ✅ **Fully reversible** - Disable QoS if needed

---

## 🛡️ **Comprehensive Rollback Procedures**

### **Emergency Rollback (Full System Restore)**
If major issues occur at any phase:

```bash
# 1. IMMEDIATE ACCESS RESTORATION
- Connect directly to UCG-Fiber management interface
- Use emergency admin account if primary account locked

# 2. DISABLE ALL NEW FIREWALL RULES
Settings → Security → Firewall → Disable all new rules

# 3. RESTORE NETWORK TOPOLOGY
Settings → Networks → Delete all new VLANs
Move all devices back to "Default" network

# 4. REMOVE DEVICE GROUPS
Settings → Security → Firewall → Delete all device groups

# 5. DISABLE QOS
Settings → Network → Disable all QoS profiles

# 6. VERIFY CONNECTIVITY
Test all devices can communicate as before
```

### **Partial Rollback Options**
- **Phase 1 only**: Keep VLANs but don't use them
- **Phase 2 only**: Keep classification but don't enforce
- **Phase 3 only**: Disable firewall rules, keep VLANs
- **Phase 4 only**: Disable QoS, keep security rules

---

## ⏱️ **Implementation Timeline**

### **Recommended Schedule:**
- **Phase 1**: Today (30 minutes, no downtime)
- **Phase 2**: Today + 1 hour (prepare classification)
- **Phase 3**: Schedule during low-usage window (HIGH RISK)
- **Phase 4**: After Phase 3 validation (low risk enhancement)

### **Testing Between Phases:**
- Verify all existing functionality works
- Test critical applications and services
- Validate network connectivity
- Check device accessibility

---

## 📞 **Emergency Contacts & Recovery**

### **If Issues Occur:**
1. **Document the problem** (screenshots, error messages)
2. **Try partial rollback** first (disable new rules)
3. **Use emergency access** methods if needed
4. **Full system restore** as last resort

### **Recovery Tools Available:**
- UniFi Console web interface
- SSH access to UCG-Fiber (if enabled)
- Physical console access
- UniFi mobile app for basic management

---

## ✅ **Pre-Deployment Checklist**

- [ ] **Backup current configuration** (automated)
- [ ] **Verify administrative access** (working credentials)
- [ ] **Test rollback procedures** (practice on test environment if available)
- [ ] **Identify critical services** that must remain operational
- [ ] **Plan implementation window** (low usage period)
- [ ] **Prepare monitoring tools** (network connectivity tests)
- [ ] **Document current device IPs** for troubleshooting

---

## 🎯 **Success Criteria**

### **Phase 1 Success:**
- 10 VLANs created successfully
- DHCP pools active and functional
- No impact on existing connectivity
- Rollback tested and confirmed working

### **Overall Success:**
- All devices properly classified and segmented
- Zero-trust security policies active
- Network performance improved with QoS
- No critical service disruptions
- Enhanced security posture achieved

---

**Ready to proceed with Phase 1 when you confirm approval.**