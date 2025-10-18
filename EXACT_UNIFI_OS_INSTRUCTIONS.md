# Exact UniFi OS 9.5.12 Device Movement Instructions

**✅ Confirmed for your system:** UCG-Fiber running UniFi OS 9.5.12

---

## 🌐 **Step 1: Access Your Controller**

1. **Open browser:** https://mars.int.bozza.au
2. **Login:** 
   - Username: `itsme@bozza.au`
   - Password: [your password]

---

## 📱 **Step 2: Navigate to Clients (UniFi OS 9.5.12)**

**In the UniFi OS Console:**

### **Option A: From Main Dashboard**
- Look for **"Clients"** tab at the top of the main screen
- Click **"Clients"** to see all connected devices

### **Option B: From Left Navigation**
- Click **"Network"** in the left sidebar
- Then click **"Clients"** or **"Client Devices"**

### **Option C: From Device Overview**
- Look for a **"Devices"** or **"Connected Devices"** section
- This shows all your currently connected devices

**You should see a list showing all 10 devices currently connected to "Default" network**

---

## 🔧 **Step 3: Move Each Device (Exact Process)**

### **For Each Device, Follow This Exact Process:**

1. **Find the device** in the clients list
2. **Click on the device name or row** - this opens the device details panel
3. **Look for one of these settings:** (may vary slightly)
   - **"Network"** dropdown
   - **"Network Assignment"** 
   - **"Override Network"** toggle + dropdown
   - **"Configuration"** → "Network"
4. **Current setting will show:** "Default"
5. **Click the dropdown** and select the new network
6. **Click "Apply" or "Apply Changes"**
7. **Wait 30-60 seconds** for device to reconnect

---

## 📋 **Exact Device Assignments (Confirmed Network Names)**

### **🏢 Management Infrastructure → "MGMT_Infrastructure"**
Move these UniFi devices:
- **`upstairs---study`** (192.168.22.251)
- **`lounge-room`** (192.168.22.205)
- **`backup`** (192.168.22.213)  
- **`g5-pro`** (192.168.22.249)
- **`driveway`** (192.168.22.224)

### **🖥️ User Devices → "User_Devices"**  
Move your Mac:
- **`Boz-MBP-M3-Max`** (192.168.22.241)
- **`Boz-MBP-M3-Max`** (Unknown IP - wireless connection)

### **📊 Corporate Servers → "Corporate_Servers"**
Move your server:
- **`truenas`** (Unknown IP)

### **🍎 Apple IoT → "Apple_IoT"**
Move Apple device:
- **`ControlAppleTV2`** (192.168.22.212)

### **📹 Security → "Security_Cameras"** 
Move camera:
- **`ringring`** (192.168.22.253)

---

## 🎯 **Example: Moving Your Mac Computer (Step-by-Step)**

1. **Find device:** Scroll through client list, find `Boz-MBP-M3-Max`
2. **Click device:** Click on the device name/row
3. **Device panel opens:** Shows device details on the right or in overlay
4. **Find Network setting:** Look for "Network" dropdown (currently showing "Default")
5. **Click Network dropdown:** Opens list of available networks
6. **Select:** Click **"User_Devices"** from the dropdown list
7. **Apply:** Click **"Apply"** or **"Apply Changes"** button
8. **Wait:** Device will disconnect briefly and reconnect
9. **Verify:** Device should show new IP in 192.168.20.x range
10. **Test:** Verify internet and local access still work

---

## 📊 **Expected Results After Movement**

**Your devices will get new IPs in these ranges:**

- **MGMT_Infrastructure (VLAN 5):** 192.168.5.10 - 192.168.5.50
- **Corporate_Servers (VLAN 10):** 192.168.10.10 - 192.168.10.254
- **User_Devices (VLAN 20):** 192.168.20.10 - 192.168.20.254  
- **Apple_IoT (VLAN 30):** 192.168.30.10 - 192.168.30.254
- **Security_Cameras (VLAN 50):** 192.168.50.10 - 192.168.50.254

---

## ⚠️ **Important Notes for UniFi OS 9.5.12**

### **Device Reconnection**
- **Brief disconnection** is normal (30-60 seconds)
- **New DHCP lease** will be issued from new VLAN
- **Some devices** may need to be power cycled if they don't auto-reconnect

### **Interface Variations**
In UniFi OS 9.5.12, the network assignment might be under:
- **Settings tab** within device details
- **Configuration section**  
- **Network Override** toggle (enable first, then select)
- **Advanced settings**

### **If You Don't See Network Dropdown**
1. Look for **"Override Network"** toggle - turn it ON first
2. Then the network dropdown should appear
3. Or look in **"Settings"** or **"Configuration"** tabs

---

## 🔍 **Monitoring Your Progress**

**Run this to check status:**
```bash
source activate.sh
python3 check_device_status.py
```

**Live monitoring (updates every 10 seconds):**
```bash
source activate.sh
python3 check_device_status.py --monitor
```

---

## 🚨 **Troubleshooting UniFi OS 9.5.12**

### **Can't Find Network Dropdown:**
1. **Check device details tabs:** Settings, Configuration, Advanced
2. **Look for "Override" toggle** - enable it first
3. **Try refreshing** the page and trying again

### **Device Won't Move:**
1. **Try "Forget" then "Adopt"** the device
2. **Power cycle** the device after assignment
3. **Check DHCP** is enabled on target VLAN

### **Lost Connection:**
1. **Physical access** to UCG-Fiber may be needed
2. **Direct ethernet connection** to UCG-Fiber
3. **Factory reset** device if completely unreachable

---

## 🎯 **Recommended Order**

**Start with lowest-impact devices:**

1. **Ring camera** (`ringring`) → `Security_Cameras`
2. **Apple TV** (`ControlAppleTV2`) → `Apple_IoT`  
3. **TrueNAS** (`truenas`) → `Corporate_Servers`
4. **UniFi infrastructure** → `MGMT_Infrastructure` (may briefly interrupt WiFi)
5. **Your Mac** (`Boz-MBP-M3-Max`) → `User_Devices` (keep this last for management access)

---

## 🛡️ **Emergency Rollback**

**If anything goes wrong:**
```bash
source activate.sh
python3 emergency_rollback.py
```

**This will move all devices back to "Default" network and restore original configuration.**

---

## ✅ **Success Verification**

**After moving all devices, you should see:**
- ✅ All devices online with new IP addresses
- ✅ Internet access works from your Mac
- ✅ Can access TrueNAS from your Mac
- ✅ Apple TV streams content normally
- ✅ UniFi controller still accessible
- ✅ Network performance maintained or improved

**🎉 Enterprise zero-trust network segmentation achieved!**