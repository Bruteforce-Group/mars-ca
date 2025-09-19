# SimpleMDM Certificate Deployment Guide

## PKCS #12 Files Available

### 1. mars.bozza.au.p12 (RECOMMENDED)
- **Type**: Publicly trusted certificate (Let's Encrypt)
- **Size**: 4.0K
- **Coverage**: mars.bozza.au only  
- **Trust**: Automatic (trusted by all devices)
- **Best for**: General use, no CA installation needed

### 2. mars-private-ca.p12
- **Type**: Private CA certificate 
- **Size**: 8.0K
- **Coverage**: mars.int.bozza.au, mars, 192.168.22.1, 124.187.49.228
- **Trust**: Requires CA installation (see bozza-root-ca.p12)
- **Best for**: Complete internal coverage

### 3. bozza-root-ca.p12  
- **Type**: Root CA certificate only
- **Size**: 1.7K
- **Purpose**: Install trust for private CA certificates
- **Deploy first**: Before mars-private-ca.p12

## SimpleMDM Deployment Steps

### Option A: Publicly Trusted Certificate (Recommended)

1. **Log into SimpleMDM**
   - Go to Device Groups or All Devices
   
2. **Create Certificate Configuration Profile**
   - Apps & Configs → Configuration Profiles → New
   - Add "Certificate" payload
   
3. **Upload Certificate**
   - Upload file: `mars.bozza.au.p12`
   - Password: (leave blank - no password)
   - Certificate name: "mars.bozza.au Certificate"
   - ✅ **Block private key extraction**: YES (security)
   - ✅ **Allow all apps access**: YES (compatibility)
   
4. **Deploy**
   - Assign to device groups
   - Install immediately or schedule

### Option B: Private CA Certificate (Complete Coverage)

1. **First - Deploy Root CA**
   - Create new Configuration Profile
   - Add "Certificate" payload
   - Upload: `bozza-root-ca.p12`
   - Password: (blank)
   - Certificate name: "Bozza Networks Root CA"
   - **Deploy to all devices FIRST**

2. **Second - Deploy Private Certificate**  
   - Create new Configuration Profile
   - Add "Certificate" payload
   - Upload: `mars-private-ca.p12`
   - Password: (blank)
   - Certificate name: "Mars Private Certificate"
   - ✅ **Block private key extraction**: YES (security)
   - ✅ **Allow all apps access**: YES (compatibility)
   - Deploy after CA is installed

## SimpleMDM API Deployment (Optional)

```bash
# Set your API key
export SIMPLEMDM_API_KEY="your_api_key_here"

# Upload certificate via API
curl -X POST https://a.simplemdm.com/api/v1/certificates \
  -u ${SIMPLEMDM_API_KEY}: \
  -F "certificate=@mars.bozza.au.p12" \
  -F "name=mars.bozza.au Certificate"
```

## Verification

After deployment, devices should:
1. Have certificates installed in keychain
2. Trust the certificate chain
3. Be able to access https://mars.bozza.au (if using public cert)
4. Allow TLS decryption by UCG-Fiber

## Security Notes

- All PKCS #12 files created with NO PASSWORD
- Private keys are included in client certificates
- Root CA should be installed before private certificates
- Consider using publicly trusted certificate to avoid CA distribution

### SimpleMDM Security Settings

**Block private key extraction** (RECOMMENDED: YES)
- Prevents users from exporting private keys from keychain
- Private key remains usable by apps but cannot be stolen
- Essential for corporate security compliance
- UCG-Fiber can still decrypt TLS traffic

**Allow all apps access** (RECOMMENDED: YES)
- Enables any application to use the certificate
- Required for web browsers, UCG-Fiber, etc.
- Can be disabled if you want to restrict to specific apps
- Improves compatibility across different services

## File Locations

All files are in: `/Users/danielborrowman/mars-ca/`
- mars.bozza.au.p12
- mars-private-ca.p12  
- bozza-root-ca.p12