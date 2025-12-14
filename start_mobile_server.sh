#!/bin/bash
# Mobile Testing Server Startup Script (Bash version)
# This script finds your IP address and starts the Django server for mobile testing

echo ""
echo "=== Mobile Testing Server Setup ==="
echo ""

# Find IP address
echo "Finding your IP address..."

# Try to get IP address (works on Windows with WSL/Git Bash)
if command -v ipconfig &> /dev/null; then
    # Windows ipconfig method
    IP=$(ipconfig | grep -i "IPv4" | head -n 1 | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | grep -v "127.0.0.1" | head -n 1)
elif command -v hostname &> /dev/null; then
    # Linux/WSL method
    IP=$(hostname -I | awk '{print $1}')
elif command -v ip &> /dev/null; then
    # Modern Linux ip command
    IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')
else
    IP=""
fi

if [ -n "$IP" ] && [ "$IP" != "127.0.0.1" ]; then
    echo "✓ Your IP address: $IP"
    echo ""
    echo "📱 Access from your mobile phone:"
    echo "   http://$IP:8000"
    echo ""
    echo "⚠️  Make sure:"
    echo "   1. Your phone is on the SAME Wi-Fi network"
    echo "   2. Windows Firewall allows Python (if connection fails)"
    echo ""
    echo "Starting Django server..."
    echo "Press Ctrl+C to stop the server"
    echo ""
    echo "=================================================="
    echo ""
    
    # Start the server
    python manage.py runserver 0.0.0.0:8000
else
    echo "✗ Could not find your IP address automatically"
    echo ""
    echo "Please find your IP address manually:"
    echo ""
    echo "On Windows (in PowerShell or CMD):"
    echo "  ipconfig"
    echo ""
    echo "Look for 'IPv4 Address' under your Wi-Fi or Ethernet adapter"
    echo "Then run:"
    echo "  python manage.py runserver 0.0.0.0:8000"
    echo ""
    echo "Or use the PowerShell script:"
    echo "  powershell -ExecutionPolicy Bypass -File start_mobile_server.ps1"
fi
