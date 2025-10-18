# Device Group Assignment & VLAN Movement Guide

## Current Status ✅
- **Phase 1**: VLANs created and configured
- **Phase 2**: Firewall groups deployed  
- **Phase 3**: Device groups configured
- **Next**: Manual device assignment and VLAN movement

## Device Assignment Plan

### 📱 Device → Group → VLAN Mapping

| Device Name | Current Network | Target Group | Target VLAN | New IP Range |
|-------------|-----------------|--------------|-------------|---------------|
| **Boz-MBP-M3-Max** | Default | User_Workstations | User_Devices (VLAN 20) | 192.168.20.x |
| **truenas** | Default | Corporate_Servers | Corporate_Servers (VLAN 10) | 192.168.10.x |
| **ControlAppleTV2** | Default | Apple_Ecosystem | Apple_IoT (VLAN 30) | 192.168.30.x |
| **ringring** | Default | Security_Systems | Security_Cameras (VLAN 50) | 192.168.50.x |
| **upstairs---study** | Default | Management_Infrastructure | MGMT_Infrastructure (VLAN 5) | 192.168.5.x |
| **lounge-room** | Default | Management_Infrastructure | MGMT_Infrastructure (VLAN 5) | 192.168.5.x |
| **backup** | Default | Management_Infrastructure | MGMT_Infrastructure (VLAN 5) | 192.168.5.x |
| **g5-pro** | Default | Management_Infrastructure | MGMT_Infrastructure (VLAN 5) | 192.168.5.x |
| **driveway** | Default | Management_Infrastructure | MGMT_Infrastructure (VLAN 5) | 192.168.5.x |

## Step-by-Step Process

### Step 1: Access UniFi Console
```
🌐 URL: https://mars.int.bozza.au
🔐 Login with your credentials
```

### Step 2: Navigate to Clients
```
📍 Path: Network → Clients
or
📍 Direct: Click "Clients" tab in main navigation
```

### Step 3: Assign Devices to Groups (FIRST)

**For each device:**

1. **Click on the device name**
2. **Look for "Groups" or "Device Groups" section**
3. **Add device to appropriate group from table above**
4. **Save/Apply changes**

⚠️ **IMPORTANT**: Complete ALL group assignments before moving to VLAN assignment

### Step 4: Move Devices to VLANs (SECOND)

**For each device (in this order):**

#### 🖥️ **Start with Non-Critical Devices First:**

1. **ControlAppleTV2** → Apple_IoT (VLAN 30)
2. **ringring** → Security_Cameras (VLAN 50)  
3. **truenas** → Corporate_Servers (VLAN 10)
4. **Infrastructure devices** → MGMT_Infrastructure (VLAN 5)
5. **Boz-MBP-M3-Max** → User_Devices (VLAN 20) ⚠️ **LAST**

#### 🔄 **VLAN Assignment Process:**
1. Click on device
2. Find **"Network"** dropdown/section
3. Change from **"Default"** to target network:
   - `Apple_IoT` for Apple devices
   - `Security_Cameras` for cameras
   - `Corporate_Servers` for servers
   - `MGMT_Infrastructure` for UniFi devices
   - `User_Devices` for computers
4. Click **Apply** or **Save**
5. **Wait for device to reconnect** (30-60 seconds)
6. **Verify new IP address** in correct range

### Step 5: Test Connectivity

After each device move:

```bash
# Test basic connectivity
ping [new_device_ip]

# Test internet access from device
# (if you have shell access to the device)
```

**Expected Results:**
- Device gets new IP in correct VLAN range
- Device maintains internet connectivity
- Device can communicate with allowed devices

## Troubleshooting

### ❌ Device Not Getting New IP
```
Solution:
1. Wait 2-3 minutes for DHCP lease
2. Restart the device if possible
3. Check DHCP scope isn't full
4. Verify VLAN configuration
```

### ❌ Device Loses Connectivity  
```
Solution:
1. Move device back to "Default" network
2. Wait for reconnection
3. Check firewall rules
4. Try different target VLAN
```

### ❌ Cannot Access UniFi Console
```
Solution:
1. Check if you moved your management device
2. Connect via different network
3. Use mobile hotspot if needed
4. Access via direct IP if available
```

## Safety Measures

### 🛡️ **Backup Plan:**
If issues occur, run:
```bash
python3 emergency_rollback.py
```

### 📱 **Keep Backup Access:**
- Keep a mobile device on Default network
- Have backup internet connection ready
- Know direct IP addresses for critical services

### 🕐 **Timing:**
- Do this during low-usage hours
- Allow 15-30 minutes for the process
- Test one device at a time

## Post-Completion Verification

Once all devices are moved:

```bash
# Check all devices are assigned correctly
python3 check_device_status.py --monitor

# Verify network segmentation is working
python3 monitor_unifi_policies.py
```

## Expected Final State

### 📊 **Network Distribution:**
- **VLAN 5 (Management)**: 5 devices (UniFi infrastructure)
- **VLAN 10 (Corporate)**: 1 device (truenas)
- **VLAN 20 (User Devices)**: 2 devices (your Macs)
- **VLAN 30 (Apple IoT)**: 1 device (Apple TV)
- **VLAN 50 (Security)**: 1 device (Ring camera)
- **Default Network**: 0 devices (empty)

### 🎯 **Success Criteria:**
✅ All devices have appropriate IP ranges
✅ Internet connectivity maintained
✅ Device groups properly assigned
✅ Network segmentation active
✅ Zero-trust policies enforced

---

**🚨 IMPORTANT REMINDER:**
Move your main computer (Boz-MBP-M3-Max) LAST to maintain console access throughout the process!