# 🆓 FREE PAYMENT TESTING GUIDE - 15 MINUTES

**Goal**: Get your first FREE payment working in 15 minutes  
**Cost**: ✅ $0 (Completely Free)  
**No Credit Card Needed**: ✅ Yes  
**Testing Gateway**: Flutterwave Sandbox

---

## ⏱️ STEP-BY-STEP (15 minutes)

### STEP 1: Create Free Flutterwave Account (2 minutes)

1. Go to: **https://dashboard.flutterwave.com/signup**
2. Enter:
   - **Email**: Your email address
   - **Password**: Create strong password
   - **First Name**: Your name
   - **Last Name**: Your name
3. Click: **Create Account**
4. Check email: Click confirmation link
5. ✅ Account created!

---

### STEP 2: Get Your Free Sandbox Keys (3 minutes)

1. Login to: https://dashboard.flutterwave.com/
2. Go to: **Settings** (gear icon, top right)
3. Click: **API Keys**
4. You'll see two tabs:
   - **Live Keys** (for production - need approval)
   - **Test Keys** (for free sandbox - available now!)
5. Copy these **TEST KEYS**:
   - **Public Key**: Starts with `pk_test_`
   - **Secret Key**: Starts with `sk_test_`
6. ✅ Keys copied!

---

### STEP 3: Add Keys to Your .env File (2 minutes)

Open `.env` file in your project root:

```bash
# Find these lines and update:

FLUTTERWAVE_PUBLIC_KEY=pk_test_[PASTE_YOUR_KEY_HERE]
FLUTTERWAVE_SECRET_KEY=sk_test_[PASTE_YOUR_KEY_HERE]
FLUTTERWAVE_SECRET_HASH=your-secret-hash

PAYMENT_ENVIRONMENT=sandbox
```

Save the file.

---

### STEP 4: Restart Your Django App (1 minute)

Stop your Django server:
```bash
# Press Ctrl+C in terminal where Django is running
```

Start it again:
```bash
python manage.py runserver
```

---

### STEP 5: Create a Test Order (2 minutes)

1. Open: http://localhost:8000/
2. Login as a customer (or create account)
3. Browse menu and add items to cart
4. Click: **Checkout**
5. Select payment method: **Card Payment** or **Bank Transfer**
6. Click: **Place Order**
7. ✅ Order created!

---

### STEP 6: Make Your First FREE Payment (3 minutes)

You'll see a payment page redirect to Flutterwave.

**Use this TEST CARD** (completely free, no charge):
```
Card Number: 4242 4242 4242 4242
Expiry Date: Any future date (e.g., 12/25)
CVV: Any 3 digits (e.g., 123)
PIN: Any 4 digits (e.g., 1234)
OTP: 12345
```

Steps:
1. Enter card: `4242 4242 4242 4242`
2. Enter expiry: `12/25`
3. Enter CVV: `123`
4. Click: **Pay**
5. Enter OTP: `12345`
6. ✅ Payment processed!

---

## ✅ WHAT HAPPENS NEXT

### Success! 🎉
1. Payment page shows "✅ Payment Successful"
2. Redirects back to your site
3. Order shows as **PAID** ✅
4. Payment appears in admin panel
5. Receipt generated

### Check Your Payment

**Admin Panel**:
```
1. Go to: /admin/
2. Click: Payments
3. See your payment listed!
4. Status: COMPLETED ✅
```

**Customer View**:
```
1. Go to: /payments/history/
2. See payment in list
3. Click for details and receipt
```

---

## 🔍 VERIFY IT WORKED

### In Django Terminal
```bash
python manage.py shell
>>> from payments.models import Payment
>>> Payment.objects.latest('created_at')
# Shows your test payment!
```

### In Flutterwave Dashboard
```
1. Login: https://dashboard.flutterwave.com/
2. Go to: Transactions
3. See your test transaction
4. Status: COMPLETED ✅
```

---

## 🧪 TEST MORE PAYMENTS

### Test Different Scenarios

**Test 1: Successful Payment** ✅
- Use test card: `4242 4242 4242 4242`
- Result: Payment succeeds

**Test 2: Failed Payment** ❌
- Use test card: `5531 8866 5869 0604`
- Result: Payment fails (to test error handling)

**Test 3: Manual Bank Transfer**
- Select: Bank Transfer payment method
- Enter: Any account number
- Later: Admin manually confirms payment

---

## 📱 TEST OTHER PAYMENT METHODS

### Test Cash on Delivery
```
1. Create order
2. Select: Cash on Delivery
3. Order created with PENDING payment
4. Admin can manually confirm
```

### Test Mobile Money (Future)
```
When you add MTN/Airtel sandbox credentials:
1. Create order
2. Select: MTN Mobile Money
3. Enter test phone: 256748937291
4. Payment processes through MTN sandbox
```

---

## 🛠️ TROUBLESHOOTING

### "Payment page won't load"
**Problem**: Redirect not working  
**Solution**:
1. Check .env has correct keys
2. Restart Django: `Ctrl+C` then `python manage.py runserver`
3. Refresh page

### "Card declined"
**Problem**: Test card not working  
**Solution**: 
- Use exact card: `4242 4242 4242 4242`
- Any future expiry date
- Any 3-digit CVV
- OTP: `12345`

### "Payment pending, not completing"
**Problem**: Webhook not received  
**Solution**:
- Payment will eventually complete
- Check payment detail page
- Click "Verify Payment" button manually

### "Can't login to Flutterwave"
**Problem**: Forgot password or account issue  
**Solution**:
1. Go to: https://dashboard.flutterwave.com/
2. Click: "Forgot Password?"
3. Reset via email

---

## 💡 TIPS & TRICKS

### Tip 1: Keep Keys Safe
```bash
# These are TEST keys (safe to share for testing)
pk_test_xxxxx ← Can show people
sk_test_xxxxx ← Don't commit to git

# These are LIVE keys (NEVER share!)
pk_live_xxxxx ← KEEP SECRET!
sk_live_xxxxx ← KEEP SECRET!
```

### Tip 2: Test Thoroughly
```
Before going LIVE, test:
□ Successful payment
□ Failed payment
□ Payment verification
□ Receipt generation
□ Refund process
□ Admin confirmation
```

### Tip 3: Clear Test Data
```bash
# Delete test payments after testing
python manage.py shell
>>> from payments.models import Payment
>>> Payment.objects.all().delete()
```

---

## 🚀 NEXT STEPS

### Now That It Works

**Option A: Keep Testing Free**
```
1. Create more test orders
2. Try different payment methods
3. Verify all features work
4. Test error scenarios
```

**Option B: Prepare for Production**
```
1. Get MTN sandbox keys (also free)
2. Get Airtel sandbox keys (also free)
3. Test all payment methods
4. Verify webhooks work
5. Document your setup
```

**Option C: Go Live** (When ready)
```
1. Get production keys from Flutterwave
2. Update .env with live keys
3. Deploy to production
4. Start accepting real payments
5. Pay per transaction (~1.4% fee)
```

---

## 📊 FREE vs PAID

### FREE Sandbox Mode (Right Now)
✅ Use any test card  
✅ Make unlimited test payments  
✅ $0 cost  
✅ No real money moves  
✅ Perfect for development  

### PAID Production Mode (When Ready)
💰 Use real customer cards  
💰 Real money processed  
💰 Pay ~1.4% per transaction  
💰 Goes live immediately  
💰 Keep 98.6% of payment  

---

## ✅ CHECKLIST

```
Setup Complete:
□ Flutterwave account created (free)
□ Test keys obtained
□ Keys added to .env
□ Django restarted
□ Test order created
□ Test payment processed
□ Payment appears in admin
□ Receipt generated
□ Verification passed

All checks complete? ✅ YOUR PAYMENT SYSTEM IS WORKING!
```

---

## 🎉 CONGRATULATIONS!

You now have:
✅ FREE payment testing working  
✅ No costs involved  
✅ Real payment flow verified  
✅ Ready for more testing  
✅ Ready to add more gateways  

### Your Payment System Is ALIVE! 🚀

---

## 📞 NEED HELP?

### Common Questions

**Q: Can I use this in production?**
A: No, sandbox is for testing only. But it's FREE and perfect for dev!

**Q: Will customers see "TEST" mode?**
A: In production, you'll switch to live keys - no test labels shown.

**Q: Can I add more payment methods?**
A: Yes! Follow same process for MTN and Airtel sandbox keys.

**Q: What if payment fails?**
A: Check our troubleshooting section above.

**Q: How long do test payments last?**
A: They stay in sandbox forever (only for testing).

---

## 🔗 QUICK LINKS

- **Flutterwave Dashboard**: https://dashboard.flutterwave.com/
- **Test Cards**: https://developer.flutterwave.com/docs/test-cards-and-bvn
- **API Documentation**: https://developer.flutterwave.com/
- **Support**: https://support.flutterwave.com/

---

## 📈 PAYMENT FLOW YOU JUST TESTED

```
1. You created an order
2. Selected payment method
3. System generated payment link
4. Redirected to Flutterwave
5. You entered test card details
6. Flutterwave processed payment
7. Redirected back to your site
8. Payment marked COMPLETED
9. Receipt generated
10. Admin can see transaction

✅ FULL PAYMENT FLOW WORKING!
```

---

## 🎯 WHAT'S NEXT?

### Immediate (Today)
- [x] Setup free payment testing ✅
- [x] Process first payment ✅
- [ ] Test a few more payments
- [ ] Try different scenarios

### This Week
- [ ] Add MTN sandbox keys
- [ ] Add Airtel sandbox keys
- [ ] Test all payment methods
- [ ] Verify error handling

### Next Week
- [ ] Get production credentials
- [ ] Deploy to production server
- [ ] Enable real payments
- [ ] Go live! 🚀

---

**Total Time Spent**: 15 minutes ⏱️  
**Total Cost**: $0 💰  
**Payment System Status**: ✅ WORKING  

### Ready for More? 

Continue with:
- **PAYMENT_SETUP_GUIDE.md** - Add more gateways
- **PAYMENT_FINALIZATION_CHECKLIST.md** - Production deployment
- **PAYMENT_SYSTEM_ARCHITECTURE.md** - Technical details

---

**Date**: February 1, 2026  
**Status**: ✅ PAYMENT TESTING LIVE & FREE
