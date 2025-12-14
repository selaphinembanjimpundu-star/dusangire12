# Simple Mobile Testing Guide

## Quick Start (3 Steps)

### Step 1: Run the Helper Script

**If you're using PowerShell:**
```powershell
.\start_mobile_server.ps1
```

**If you're using Bash/Git Bash:**
```bash
chmod +x start_mobile_server.sh
./start_mobile_server.sh
```

**Or run directly:**
```bash
bash start_mobile_server.sh
```

This will:
- Find your IP address automatically
- Show you the URL to use on your phone
- Start the server

### Step 2: On Your Phone

1. Make sure your phone is on the **same Wi-Fi** as your computer
2. Open a browser (Chrome, Safari, etc.)
3. Type the URL shown in Step 1 (something like `http://192.168.1.100:8000`)

### Step 3: Test!

Navigate through your app and test all the mobile features.

---

## Manual Method (If Script Doesn't Work)

### Find Your IP Address

**On Windows (PowerShell or CMD):**
1. Type: `ipconfig`
2. Look for your Wi-Fi adapter section
3. Find the line that says **"IPv4 Address"**
4. Copy that number (e.g., `192.168.1.100`)

**On Linux/WSL:**
```bash
hostname -I
```

### Start the Server

```bash
python manage.py runserver 0.0.0.0:8000
```

### Access from Phone

Open browser on phone and go to: `http://YOUR_IP:8000`

---

## Common Issues

### "Can't connect" or "Connection refused"

**Solution 1: Allow Python through Firewall**
1. Press `Windows Key` and search for "Firewall"
2. Click "Allow an app through firewall"
3. Find "Python" and check both boxes (Private & Public)
4. If Python isn't there, click "Allow another app" and browse to your Python.exe

**Solution 2: Check IP Address**
- Make sure you're using the correct IP from `ipconfig`
- Make sure it's not `127.0.0.1` or `169.254.x.x` (those won't work)

**Solution 3: Check Network**
- Both devices must be on the same Wi-Fi
- Try disconnecting and reconnecting your phone to Wi-Fi

### Script Won't Run

If PowerShell says "execution policy", run this first:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try the script again.

---

## What to Test on Mobile

- [ ] Navigation menu works
- [ ] Buttons are easy to tap
- [ ] Forms are easy to fill
- [ ] Images load properly
- [ ] Layout looks good on small screen
- [ ] Can scroll smoothly
- [ ] Can add items to cart
- [ ] Can place orders

---

## Need More Help?

Check the detailed guide: `MOBILE_TESTING_GUIDE.md`
