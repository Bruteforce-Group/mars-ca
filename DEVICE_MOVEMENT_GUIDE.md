# Device Movement Guide - UniFi Network Segmentation

## 🎯 **Objective**
Move your 10 connected devices from the "Default" network to appropriate VLANs for zero-trust security.

---

## 🌐 **Step 1: Access UniFi Controller**

1. **Open your web browser**
2. **Navigate to:** https://mars.int.bozza.au
3. **Login with your credentials:**
   - Username: `itsme@bozza.au`
   - Password: [your password]

---

## 📱 **Step 2: Navigate to Client Devices**

1. **In the UniFi Controller interface:**
   - Click on **"Network"** in the left sidebar
   - OR click on **"Clients"** in the main dashboard
   - OR look for **"Client Devices"** section

2. **You should see a list of all connected devices**
   - This will show your 10 devices currently on "Default" network

---

## 🔧 **Step 3: Move Each Device to Appropriate VLAN**

For **each device listed below**, follow this process:

### **Device Movement Process:**

1. **Find the device** in the client list
2. **Click on the device name** (this opens device details)
3. **Look for "Network" or "VLAN Assignment" setting**
4. **Change from "Default" to the target network**
5. **Click "Apply" or "Save"**

---

## 📋 **Device Assignment Plan**

### **🏢 Management Infrastructure (VLAN 5)**
**Target Network:** `MGMT_Infrastructure`

Move these **UniFi devices:**
- **`upstairs---study`** (UniFi AP - 192.168.22.251)
- **`lounge-room`** (UniFi AP - 192.168.22.205)  
- **`backup`** (UniFi device - 192.168.22.213)
- **`g5-pro`** (UniFi camera - 192.168.22.249)
- **`driveway`** (UniFi device - 192.168.22.224)

### **🖥️ User Devices (VLAN 20)**
**Target Network:** `User_Devices`

Move these **personal devices:**
- **`Boz-MBP-M3-Max`** (Mac computer - 192.168.22.241)
- **`Boz-MBP-M3-Max`** (Mac wireless connection - no IP shown)

### **🏢 Corporate Servers (VLAN 10)**  
**Target Network:** `Corporate_Servers`

Move this **server:**
- **`truenas`** (TrueNAS storage server - no IP shown)

### **🍎 Apple IoT (VLAN 30)**
**Target Network:** `Apple_IoT`

Move this **Apple device:**
- **`ControlAppleTV2`** (Apple TV - 192.168.22.212)

### **📹 Security Cameras (VLAN 50)**
**Target Network:** `Security_Cameras`

Move this **camera:**
- **`ringring`** (Ring camera - 192.168.22.253)

---

## 🖱️ **Detailed Click-by-Click Instructions**

### **Example: Moving Your Mac Computer**

1. **Find device:** Look for `Boz-MBP-M3-Max` in the client list
2. **Click on device:** Click the device name or row
3. **Device details open:** You'll see device information panel
4. **Find Network setting:** Look for:
   - "Network Assignment" 
   - "VLAN" 
   - "Network" dropdown
   - "Override Network" option
5. **Change network:** Click dropdown showing "Default"
6. **Select:** Choose `User_Devices` from the dropdown
7. **Save:** Click "Apply", "Save", or "Update" button
8. **Wait:** Device will reconnect (may take 30-60 seconds)
9. **Verify:** Check device has new IP in 192.168.20.x range

### **Expected IP Ranges After Movement:**

- **Management VLAN (5):** 192.168.5.10 - 192.168.5.50
- **Corporate VLAN (10):** 192.168.10.10 - 192.168.10.254  
- **User VLAN (20):** 192.168.20.10 - 192.168.20.254
- **Apple IoT VLAN (30):** 192.168.30.10 - 192.168.30.254
- **Security VLAN (50):** 192.168.50.10 - 192.168.50.254

---

## ⚠️ **Important Notes**

### **🔄 Device Reconnection**
- **Each device will briefly disconnect** when moved
- **New IP address** will be assigned from new VLAN
- **Wait 30-60 seconds** for reconnection
- **Some devices may need manual reconnect** (rare)

### **📱 Test Connectivity After Each Move**
After moving each device:
1. **Verify device reconnects** with new IP
2. **Test basic connectivity** (internet, local services)
3. **If issues occur:** Move back to "Default" network

### **🚨 Emergency Rollback**
If any device becomes unreachable:
1. **Move it back** to "Default" network immediately
2. **OR run emergency rollback script:**
   ```bash
   python3 emergency_rollback.py
   ```

---

## 🎯 **Suggested Movement Order**

**Start with non-critical devices:**

1. **Start with cameras** (`ringring`) - least impact
2. **Move Apple TV** (`ControlAppleTV2`) - easy to test
3. **Move TrueNAS** (`truenas`) - test file access
4. **Move UniFi infrastructure** (APs, etc.) - may cause brief WiFi interruption
5. **Move your Mac LAST** (`Boz-MBP-M3-Max`) - keep management access

---

## 🔍 **Verification Steps**

After moving each device, verify:

### **✅ Device Connectivity Checklist:**
- [ ] Device appears online with new IP
- [ ] Internet access works (if applicable)
- [ ] Local network access works
- [ ] Device-specific functions work (streaming, file access, etc.)

### **🖥️ Your Mac (Most Important):**
After moving to User_Devices VLAN:
- [ ] Internet browsing works
- [ ] Can access TrueNAS server
- [ ] Can reach UniFi controller (https://mars.int.bozza.au)
- [ ] SSH/remote access works if needed

### **📺 Apple TV:**
After moving to Apple_IoT VLAN:
- [ ] Can stream from internet services
- [ ] AirPlay works from your Mac
- [ ] Apps load and function normally

### **📊 TrueNAS Server:**
After moving to Corporate_Servers VLAN:
- [ ] Web interface accessible from your Mac
- [ ] File shares accessible
- [ ] Services running normally

---

## 🚨 **Troubleshooting**

### **Device Won't Move/Connect:**
1. **Try moving back to Default** network first
2. **Wait 2-3 minutes** for full reconnection
3. **Try moving to target VLAN again**
4. **Check DHCP is enabled** on target VLAN

### **Can't Access Device After Move:**
1. **Check new IP range** (device should get new IP)
2. **Try accessing by hostname** instead of IP
3. **Wait longer** (up to 5 minutes for some devices)
4. **Move back to Default** if still unreachable

### **Lost Access to Controller:**
1. **Physical access to UCG-Fiber** may be needed
2. **Connect laptop directly** to UCG-Fiber ethernet port
3. **Access via 192.168.1.1** (management interface)
4. **Reset network assignments** if needed

---

## 🎉 **Success Indicators**

**You'll know it's working when:**
- ✅ All devices show **new IP addresses** in correct ranges
- ✅ **Internet access** works from your Mac
- ✅ **Inter-device communication** works as expected
- ✅ **Apple TV streams** content normally
- ✅ **TrueNAS accessible** from your Mac
- ✅ **UniFi controller accessible** for management

**After all devices are moved successfully, you'll have achieved enterprise-grade network segmentation with zero-trust architecture!**

---

## 📞 **Need Help?**

If you encounter issues:
1. **Document what happened** (device names, error messages)
2. **Use emergency rollback** if needed: `python3 emergency_rollback.py`
3. **Take screenshots** of any error messages
4. **Test one device at a time** to isolate issues