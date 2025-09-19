# DNS Setup Guide for mars.bozza.au

## Overview
Set up split-horizon DNS so mars.bozza.au resolves differently for internal vs external clients:
- **Internal clients**: mars.bozza.au → 192.168.22.1 (UCG-Fiber/router)
- **External clients**: mars.bozza.au → 124.187.49.228 (Telstra public IP)

## Step 1: External DNS (Cloudflare)

### Option A: Cloudflare Dashboard
1. **Log into Cloudflare**
   - Go to your bozza.au domain
   
2. **Add A Record**
   - Type: A
   - Name: mars
   - IPv4 address: 124.187.49.228
   - Proxy status: DNS only (grey cloud)
   - TTL: Auto

### Option B: Cloudflare API
```bash
# Set your Cloudflare credentials
export CF_Token="your_cloudflare_api_token"
export ZONE_ID="your_zone_id_for_bozza_au"

# Create A record for mars.bozza.au
curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
  -H "Authorization: Bearer ${CF_Token}" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "A",
    "name": "mars",
    "content": "124.187.49.228",
    "ttl": 300,
    "proxied": false
  }'
```

## Step 2: Internal DNS Setup

You need to override mars.bozza.au internally. Choose the best option for your network:

### Option A: UniFi Router (Recommended)
1. **Log into UniFi Controller**
   - Navigate to Settings → Networks → LAN

2. **Configure Custom DNS**
   - Settings → Internet → WAN Networks → Primary (WAN1)
   - DNS Server: Manual
   - Add custom DNS entries

3. **Add DNS Override**
   - Go to Settings → Routing & Firewall → DNS
   - Add DNS record:
     - Record Type: A
     - Hostname: mars.bozza.au
     - IP Address: 192.168.22.1

### Option B: Pi-hole (If you have one)
1. **Add Local DNS Record**
   ```bash
   # SSH to Pi-hole
   echo "192.168.22.1 mars.bozza.au" >> /etc/pihole/custom.list
   pihole restartdns
   ```

### Option C: Router DNS Override (Generic)
Most routers support DNS overrides:
1. Log into router web interface
2. Look for "DNS Settings" or "Local DNS"
3. Add entry: mars.bozza.au → 192.168.22.1

### Option D: Individual Device DNS (/etc/hosts)
**macOS/Linux:**
```bash
sudo echo "192.168.22.1 mars.bozza.au" >> /etc/hosts
```

**Windows:** Add to `C:\Windows\System32\drivers\etc\hosts`
```
192.168.22.1 mars.bozza.au
```

## Step 3: Router Port Forwarding (Optional)

If you want external access to work, configure port forwarding:

### UniFi Router Port Forwarding
1. **Navigate to Port Forwarding**
   - Settings → Routing & Firewall → Port Forwarding

2. **Add Rules**
   ```
   Rule 1 - HTTPS:
   - Name: mars-https
   - From: WAN
   - Port: 443
   - Forward IP: 192.168.22.1
   - Forward Port: 443
   - Protocol: TCP
   
   Rule 2 - HTTP (optional):
   - Name: mars-http
   - From: WAN
   - Port: 80
   - Forward IP: 192.168.22.1
   - Forward Port: 80
   - Protocol: TCP
   ```

## Step 4: Testing

### Test External DNS
```bash
# From external network or using external DNS
dig @8.8.8.8 mars.bozza.au
# Should return: 124.187.49.228
```

### Test Internal DNS
```bash
# From internal network
dig mars.bozza.au
# Should return: 192.168.22.1

# Test HTTPS
curl -I https://mars.bozza.au
# Should connect to your router/UCG-Fiber
```

### Test Certificate
```bash
# Check certificate from internal network
openssl s_client -connect mars.bozza.au:443 -servername mars.bozza.au < /dev/null
# Should show Let's Encrypt certificate
```

## Step 5: Configure UCG-Fiber

1. **Install Certificate**
   - Upload mars.bozza.au.p12 to UCG-Fiber
   - Configure for HTTPS service on port 443

2. **TLS Decryption Rules**
   - Create rules for mars.bozza.au traffic
   - Apply certificate for decryption

## Troubleshooting

### DNS Cache Issues
```bash
# macOS - Clear DNS cache
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# Linux - Clear DNS cache
sudo systemctl restart systemd-resolved
```

### Certificate Issues
- Ensure certificate covers mars.bozza.au (not mars.int.bozza.au)
- Check certificate is properly installed on UCG-Fiber
- Verify internal DNS is resolving correctly

### Split-Horizon Not Working
- Check router DNS override is configured correctly
- Verify internal clients are using router as DNS server
- Test with different DNS resolution methods

## Security Notes

- External DNS record exposes your public IP
- Internal DNS override keeps traffic local
- Port forwarding creates external access point
- Consider firewall rules for external access
- Monitor UCG-Fiber logs for TLS decryption activity

## Network Flow

```
External Client:
mars.bozza.au → DNS lookup → 124.187.49.228 → Telstra → Router → UCG-Fiber

Internal Client:
mars.bozza.au → DNS lookup → 192.168.22.1 → UCG-Fiber (direct)
```

This setup enables:
- ✅ Publicly trusted certificate
- ✅ Internal traffic stays local
- ✅ UCG-Fiber TLS decryption
- ✅ External access (if port forwarding enabled)