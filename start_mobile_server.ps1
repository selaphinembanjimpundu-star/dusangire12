# Mobile Testing Server Startup Script
# This script finds your IP address and starts the Django server for mobile testing

Write-Host "`n=== Mobile Testing Server Setup ===" -ForegroundColor Cyan
Write-Host ""

# Find IP address
Write-Host "Finding your IP address..." -ForegroundColor Yellow
$ip = $null

# Try to get Wi-Fi IP first
$wifiIP = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | 
    Where-Object {$_.InterfaceAlias -like "*Wi-Fi*" -and $_.IPAddress -notlike "169.254.*"} | 
    Select-Object -First 1 -ExpandProperty IPAddress

# If no Wi-Fi, try Ethernet
if (-not $wifiIP) {
    $ethernetIP = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | 
        Where-Object {$_.InterfaceAlias -like "*Ethernet*" -and $_.IPAddress -notlike "169.254.*"} | 
        Select-Object -First 1 -ExpandProperty IPAddress
    $ip = $ethernetIP
} else {
    $ip = $wifiIP
}

# Fallback to ipconfig method
if (-not $ip) {
    Write-Host "Using alternative method to find IP..." -ForegroundColor Yellow
    $ipconfig = ipconfig | Select-String -Pattern "IPv4" | Select-Object -First 1
    if ($ipconfig) {
        $ip = ($ipconfig -split ":")[1].Trim()
    }
}

if ($ip) {
    Write-Host "✓ Your IP address: " -NoNewline -ForegroundColor Green
    Write-Host "$ip" -ForegroundColor White -BackgroundColor DarkGreen
    Write-Host ""
    Write-Host "📱 Access from your mobile phone:" -ForegroundColor Cyan
    Write-Host "   http://$ip:8000" -ForegroundColor Yellow -BackgroundColor Black
    Write-Host ""
    Write-Host "⚠️  Make sure:" -ForegroundColor Yellow
    Write-Host "   1. Your phone is on the SAME Wi-Fi network" -ForegroundColor White
    Write-Host "   2. Windows Firewall allows Python (if connection fails)" -ForegroundColor White
    Write-Host ""
    Write-Host "Starting Django server..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
    Write-Host ""
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host ""
    
    # Start the server
    python manage.py runserver 0.0.0.0:8000
} else {
    Write-Host "✗ Could not find your IP address automatically" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run this command manually:" -ForegroundColor Yellow
    Write-Host "  ipconfig" -ForegroundColor White
    Write-Host ""
    Write-Host "Look for 'IPv4 Address' under your Wi-Fi or Ethernet adapter" -ForegroundColor White
    Write-Host "Then run:" -ForegroundColor Yellow
    Write-Host "  python manage.py runserver 0.0.0.0:8000" -ForegroundColor White
}
