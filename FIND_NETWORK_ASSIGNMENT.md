# 🔍 Finding Network/VLAN Assignment in UniFi OS 9.5.12

## Current Status
✅ **Device Groups**: Available in client details (as you showed)
❓ **Network Assignment**: Location unclear in interface

## Possible Locations for Network/VLAN Assignment

### **Option 1: Client Details - Different Tab**
In the device popup you showed:
- Look for additional tabs beyond the **Settings** tab (⚙️)
- Check for **Network**, **Configuration**, or **Advanced** tabs

### **Option 2: Network Section**
Navigate to: **Network** → **WiFi** or **Network** → **Settings**
- Look for **Client Device Assignment** or **VLAN Assignment** section
- Some versions have network assignment under WiFi settings

### **Option 3: UniFi Network Application**
The assignment might require the **UniFi Network Application** (not just device interface):
- Look for **Network** section in main navigation
- Check **Profiles** → **Network** for assignment options

### **Option 4: Advanced Features**
Network assignment might be under:
- **Advanced Features** (if available)
- **VLAN** specific section
- **Traffic Rules** or **Firewall Rules**

### **Option 5: Different Approach - WiFi Networks**
Instead of per-device assignment, you might need to:
1. **Create separate WiFi networks** for each VLAN
2. **Connect devices to appropriate WiFi network**
3. **Use network-based segmentation**

## What We Can Verify

Let me check what networks are actually created and available: