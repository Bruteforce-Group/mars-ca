#!/bin/bash
# UniFi Policy Framework Environment Setup
# Source this file to activate the virtual environment and set environment variables

# Activate virtual environment
source venv/bin/activate

# Set UniFi Controller credentials from your Warp environment variables
export UNIFI_CONTROLLER_HOSTNAME_MARS="${UNIFI_CONTROLLER_HOSTNAME_MARS:-mars.int.bozza.au}"
export UNIFI_USERNAME_MARS="${UNIFI_USERNAME_MARS:-root}"
export UNIFI_PASSWORD_MARS="${UNIFI_PASSWORD_MARS}"
export UNIFI_API_KEY_MARS="${UNIFI_API_KEY_MARS}"

echo "🚀 UniFi Policy Framework Environment Activated"
echo "📡 Controller: ${UNIFI_CONTROLLER_HOSTNAME_MARS}"
echo "👤 Username: ${UNIFI_USERNAME_MARS}"
echo "🔑 API Key: $(if [ -n "$UNIFI_API_KEY_MARS" ]; then echo "configured"; else echo "not set"; fi)"
echo "🔒 Password: $(if [ -n "$UNIFI_PASSWORD_MARS" ]; then echo "configured"; else echo "not set"; fi)"
echo ""
echo "📁 Current directory: $(pwd)"
echo "🐍 Python: $(python3 --version)"
echo ""
echo "Available commands:"
echo "  python3 deploy_unifi_policies.py   # Deploy network policies"
echo "  python3 monitor_unifi_policies.py  # Monitor and validate policies"
echo ""
echo "💡 Use 'deactivate' to exit the virtual environment"