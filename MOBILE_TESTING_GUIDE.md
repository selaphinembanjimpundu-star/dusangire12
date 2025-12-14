# Mobile Testing Guide

This guide will help you test your Django application on a mobile phone.

## Prerequisites

1. Your computer and mobile phone must be on the **same Wi-Fi network**
2. Django development server must be running
3. Windows Firewall may need to allow Python through

## Step-by-Step Instructions

### Step 1: Find Your Computer's IP Address

**On Windows (PowerShell):**
```powershell
ipconfig
```

Look for your Wi-Fi adapter (usually "Wireless LAN adapter Wi-Fi" or similar) and find the **IPv4 Address**. It will look something like:
- `192.168.1.100`
- `192.168.0.50`
- `10.0.0.5`

**Alternative method:**
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like "*Wi-Fi*" -or $_.InterfaceAlias -like "*Ethernet*"} | Select-Object IPAddress
```

### Step 2: Configure Windows Firewall (if needed)

If you can't access the site from your phone, you may need to allow Python through Windows Firewall:

1. Open **Windows Defender Firewall**
2. Click **Allow an app or feature through Windows Defender Firewall**
3. Find **Python** in the list and check both **Private** and **Public** boxes
4. If Python isn't listed, click **Allow another app** and browse to your Python executable

### Step 3: Run Django Server on All Interfaces

Instead of the usual `python manage.py runserver`, use:

```powershell
python manage.py runserver 0.0.0.0:8000
```

The `0.0.0.0` tells Django to listen on all network interfaces, not just localhost.

### Step 4: Access from Your Mobile Phone

1. Make sure your phone is connected to the **same Wi-Fi network** as your computer
2. Open a web browser on your phone (Chrome, Safari, etc.)
3. Enter your computer's IP address followed by `:8000`:
   ```
   http://192.168.1.100:8000
   ```
   (Replace `192.168.1.100` with your actual IP address)

4. You should now see your Django application!

## Quick Test Script

You can use this PowerShell command to get your IP and start the server:

```powershell
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like "*Wi-Fi*" -or $_.InterfaceAlias -like "*Ethernet*"} | Select-Object -First 1).IPAddress
Write-Host "Your IP address is: $ip" -ForegroundColor Green
Write-Host "Access from mobile: http://$ip:8000" -ForegroundColor Cyan
python manage.py runserver 0.0.0.0:8000
```

## Testing Checklist

Once you can access the site on your phone, test:

- [ ] **Navigation**: Menu, buttons, links work correctly
- [ ] **Touch interactions**: Buttons are easy to tap (44px minimum)
- [ ] **Forms**: Input fields are large enough and don't zoom on focus
- [ ] **Layout**: Content displays properly on mobile screen
- [ ] **Images**: Load correctly and are optimized
- [ ] **Responsive design**: Layout adapts to portrait/landscape
- [ ] **Performance**: Pages load quickly on mobile network
- [ ] **Menu grid**: Displays in 1 column on mobile
- [ ] **Cart**: Items stack vertically on mobile
- [ ] **Pagination**: Works correctly on touch devices

## Troubleshooting

### Can't connect from phone?

1. **Check firewall**: Make sure Python is allowed through Windows Firewall
2. **Check IP address**: Verify you're using the correct IP (run `ipconfig` again)
3. **Check network**: Ensure both devices are on the same Wi-Fi
4. **Check server**: Make sure the server is running with `0.0.0.0:8000`
5. **Try different browser**: Some browsers may have restrictions

### Connection refused?

- Make sure you're using `0.0.0.0:8000` not `127.0.0.1:8000`
- Check that no firewall is blocking port 8000
- Try temporarily disabling Windows Firewall to test

### Slow loading?

- This is normal on mobile networks
- Test on Wi-Fi first, then try on mobile data (3G/4G/5G)
- Check that lazy loading is working (images load as you scroll)

## Alternative: Using ngrok (for testing from different networks)

If you want to test from a different network (e.g., your phone's mobile data), you can use ngrok:

1. Install ngrok: https://ngrok.com/download
2. Run your Django server normally: `python manage.py runserver`
3. In another terminal, run: `ngrok http 8000`
4. Use the ngrok URL (e.g., `https://abc123.ngrok.io`) on your phone

**Note**: ngrok URLs are temporary and change each time you restart ngrok.

## Security Note

⚠️ **Important**: The `ALLOWED_HOSTS = ['*']` setting is **ONLY for development/testing**. 

Before deploying to production:
- Change `ALLOWED_HOSTS` to your actual domain name(s)
- Set `DEBUG = False`
- Configure proper security settings

## Next Steps

After testing on mobile:
1. Fix any issues you find
2. Test on different screen sizes (use browser dev tools)
3. Test on both iOS and Android if possible
4. Test on slow networks (use Chrome DevTools throttling)
