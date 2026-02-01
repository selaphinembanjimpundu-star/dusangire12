# Phase 3 Quick Reference - Shopping Cart & Loyalty Integration

**Status**: ✅ COMPLETE | **Date**: January 22, 2026

---

## 🚀 QUICK START

### 1. Run the Server
```bash
cd c:\Users\niyig\rukundo\Dusangire19\ (2)\Dusangire19\Dusangire
python manage.py runserver
```

### 2. Access Checkout
- Login: http://localhost:8000/accounts/login/
- Menu: http://localhost:8000/menu/
- Cart: http://localhost:8000/orders/cart/
- Checkout: http://localhost:8000/orders/checkout/

### 3. Admin Access
- URL: http://localhost:8000/admin/
- Manage: Orders, VIP Tiers, Loyalty Points, Referrals

---

## 💰 DISCOUNT SYSTEM EXPLAINED

### How Discounts Work

```
CALCULATION FLOW:
┌─────────────────────────────────────────────────────────┐
│ 1. Get Cart Subtotal                                    │
│    Example: RWF 10,000                                  │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 2. Calculate VIP Discount (if applicable)               │
│    Bronze: 5%, Silver: 10%, Gold: 15%, Platinum: 20%   │
│    Example (Gold): RWF 10,000 × 15% = RWF 1,500        │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 3. Check Corporate Discount (if employee)               │
│    If contract discount > VIP discount: use corporate   │
│    Otherwise: keep VIP discount                         │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 4. Add Referral Discount (first order only)             │
│    If referred: +10% additional discount                │
│    Stacks with VIP/Corporate                            │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 5. Loyalty Points Redemption (optional)                 │
│    User slides: 0-X points to redeem                    │
│    1 point = RWF 100                                    │
│    Example: 50 points = RWF 5,000 discount              │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 6. Add Delivery Charge                                  │
│    Based on delivery zone selected                      │
│    Example: RWF 1,000                                   │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ FINAL TOTAL = Subtotal - All Discounts + Delivery      │
│ Example: 10,000 - 1,500 - 5,000 + 1,000 = RWF 4,500   │
└─────────────────────────────────────────────────────────┘
```

### Example Discount Scenario

**Customer**: John (Gold VIP, Referred, 200 loyalty points)

1. **Subtotal**: RWF 50,000
2. **VIP Discount** (Gold 15%): -RWF 7,500
3. **Referral Discount** (10%): -RWF 5,000
4. **Loyalty Points** (100 points redeemed): -RWF 10,000
5. **Delivery**: +RWF 2,000
6. **TOTAL**: RWF 29,500 (Saved RWF 20,500!)

---

## 🎯 KEY FEATURES

### VIP Tier System
```
TIER          DISCOUNT    ANNUAL SPEND
Bronze        5%          RWF 0 - 500K
Silver        10%         RWF 500K - 1M
Gold          15%         RWF 1M - 3M
Platinum      20%         RWF 3M+

Automatic Progression: System calculates based on annual spending
```

### Loyalty Points
```
EARNING:
- 1 RWF spent = 1 loyalty point earned
- Referral bonus = 100 points
- Birthday bonus = 50 points (if enabled)

REDEEMING:
- 1 point = 100 RWF value
- Redeemed at checkout with slider
- Deducted from balance after purchase
```

### Referral Program
```
REFEREE (customer who refers):
- Earns RWF 10,000 cash bonus
- Earns 100 loyalty points
- Gets RWF 10K discount on referring customer's first order

REFEREE (new customer referred):
- Gets 10% discount on first order
- Can redeem after first purchase
```

---

## 📱 CHECKOUT WORKFLOW

### Step-by-Step User Journey

```
1. VIEW CART
   └─> See all items with prices
   
2. PROCEED TO CHECKOUT
   └─> Review delivery addresses
       └─> Select saved address OR
       └─> Enter new address + select zone
   
3. REVIEW LOYALTY BENEFITS
   └─> See VIP tier badge
   └─> See loyalty points balance
   └─> See referral discount (if applicable)
   
4. REDEEM LOYALTY POINTS (Optional)
   └─> Drag slider: 0 to max points
   └─> See real-time RWF value
   └─> See updated total
   
5. SELECT PAYMENT METHOD
   └─> Cash on Delivery
   └─> Mobile Money (MTN/Airtel)
       └─> Enter phone number
   └─> Bank Transfer
       └─> Enter account number
   
6. REVIEW PRICING BREAKDOWN
   └─> Subtotal
   └─> All discounts applied
   └─> Delivery charge
   └─> **Final Total**
   
7. PLACE ORDER
   └─> Submit form
   └─> Create order in database
   └─> Clear cart
   └─> Show confirmation
   └─> Redirect to order detail
```

---

## 🔧 TECHNICAL DETAILS

### Main Files

**Models** (`orders/models.py`):
```python
- Cart: User's shopping cart
- CartItem: Items in cart with quantity
- Order: Placed order with discounts
- OrderItem: Items that were ordered
```

**Service** (`orders/services.py`):
```python
OrderCalculationService:
  - calculate_order_total(cart, user, loyalty_points_to_redeem)
  - get_user_loyalty_info(user)
```

**Views** (`orders/views.py`):
```python
- add_to_cart(request, item_id)
- remove_from_cart(request, item_id)
- update_cart_item(request, item_id)
- cart(request)
- checkout(request)              # POST: Place order
- order_detail(request, order_id)
- order_history(request)
```

**Template** (`templates/orders/checkout.html`):
```html
- Left: Checkout form (address, payment)
- Right: Sticky order summary
  - VIP badge
  - Referral banner
  - Loyalty points slider
  - Real-time price breakdown
```

---

## 📊 DATABASE FIELDS

### Order Model Discount Fields
```python
order.discount_amount              # Total discount applied
order.loyalty_points_redeemed      # Number of points used
order.loyalty_discount_amount      # RWF value of loyalty discount
order.vip_discount_amount          # RWF value of VIP discount
order.corporate_discount_amount    # RWF value of corporate discount
order.referral_discount_amount     # RWF value of referral discount
order.coupon_code                  # Optional coupon code
```

---

## 🧪 TESTING SCENARIOS

### Test 1: Gold VIP Customer
```
1. Login as VIP customer (set VIPTier to Gold)
2. Add items to cart (Total: RWF 10,000)
3. Go to checkout
4. Verify Gold badge displays (15% discount)
5. Check discount amount: RWF 1,500
6. Final total: RWF 8,500
```

### Test 2: Referred Customer
```
1. Create referral program for user
2. Login as referred user
3. Add items (Total: RWF 5,000)
4. Go to checkout
5. Verify referral badge displays (10% discount)
6. Check discount: RWF 500
7. Final total: RWF 4,500
```

### Test 3: Loyalty Points Redemption
```
1. Ensure user has 100+ loyalty points
2. Add items to cart (Total: RWF 10,000)
3. Go to checkout
4. Drag points slider to 50
5. Verify real-time calculation:
   - Points value: RWF 5,000
   - New total: RWF 5,000
6. Place order
7. Verify LoyaltyPoints.balance decreased by 50
```

### Test 4: Multiple Discounts
```
1. Create Gold VIP customer with referral
2. Add items (Total: RWF 20,000)
3. Go to checkout
4. Verify:
   - VIP discount: RWF 3,000 (15%)
   - Referral: Not applied (doesn't stack with VIP)
   - User can choose to redeem points
5. Final total: 20,000 - 3,000 + delivery + points
```

---

## 🎨 UI COMPONENTS

### Checkout Summary (Right Side - Sticky)

```
┌─────────────────────────────────┐
│ ORDER SUMMARY                   │
├─────────────────────────────────┤
│ 🥇 GOLD MEMBER                  │  ← VIP Badge
│    15% Discount Applied!        │
├─────────────────────────────────┤
│ 🎁 FIRST ORDER BONUS!           │  ← Referral Banner
│    10% Referral Discount        │
├─────────────────────────────────┤
│ ⭐ YOUR POINTS: 250 pts         │  ← Loyalty Points
│    = RWF 25,000                 │
│ [═══════════ SLIDER ═══════════] │
│  0 points         -RWF 0         │
├─────────────────────────────────┤
│ Items:                          │
│ • Chicken + Rice × 2   RWF 4K   │
│ • Vegetables × 1       RWF 2K   │
├─────────────────────────────────┤
│ Subtotal:          RWF 6,000    │
│ VIP Discount (15%):  -RWF 900   │
│ Referral:           -RWF 600    │
│ Delivery:           +RWF 1,000  │
├─────────────────────────────────┤
│ 🎉 YOU'RE SAVING:               │
│         RWF 1,500              │
├─────────────────────────────────┤
│ TOTAL: RWF 5,500 ← Main focus  │
└─────────────────────────────────┘
```

---

## 📋 ADMIN MANAGEMENT

### Django Admin Features

**Orders Section**:
- View all orders
- Filter by status
- Filter by date
- Export order data
- Inline order items
- View discount breakdown

**Access**: http://localhost:8000/admin/orders/order/

**Key Fields to Monitor**:
- `discount_amount`: Total discount given
- `loyalty_points_redeemed`: Points used
- `vip_discount_amount`: VIP benefit
- `total`: Final amount paid

---

## 🔗 API ENDPOINTS

### Order-Related APIs
```
GET  /orders/order_history/          # User's order history
GET  /orders/order/<id>/             # Order details
POST /subscriptions/api/loyalty/redeem/  # Redeem points (Phase 2.4)
GET  /subscriptions/api/loyalty/status/  # Loyalty status (Phase 2.4)
```

---

## ⚠️ COMMON ISSUES & FIXES

### Issue: Discounts not showing
**Solution**: 
- Check user's VIPTier record exists
- Verify VIPTier.tier_level is set
- Check LoyaltyPoints balance > 0

### Issue: Cart total not calculating
**Solution**:
- Refresh browser cache
- Check CartItem.quantity > 0
- Verify MenuItem.price exists

### Issue: Order not placed
**Solution**:
- Check delivery address is complete
- Verify payment method selected
- Check customer name/phone filled
- Review error logs for details

### Issue: Loyalty points not deducted
**Solution**:
- Check LoyaltyTransaction was created
- Verify payment was completed
- Check Signal handlers are active

---

## 📞 SUPPORT RESOURCES

### Documentation Files
- `PHASE3_FINAL_COMPLETION.md` - Complete phase details
- `PHASE3_ENHANCEMENT_PLAN.md` - Implementation guide
- `PROJECT_STATUS.md` - Overall project status

### Code Files
- `orders/models.py` - Database models
- `orders/views.py` - Checkout logic
- `orders/services.py` - Discount calculations
- `templates/orders/checkout.html` - UI template

### Django Management
```bash
# Check system health
python manage.py check

# View migrations
python manage.py showmigrations orders

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access admin
# http://localhost:8000/admin/
```

---

## 🎉 SUCCESS METRICS

**Phase 3 Completion**:
- ✅ System check: 0 issues
- ✅ All migrations applied
- ✅ Discount engine working
- ✅ UI fully responsive
- ✅ All discounts calculating correctly
- ✅ Order placement functional
- ✅ Loyalty integration complete

**Ready for**: Phase 4 (Analytics & Reporting)

---

*Keep this guide handy for troubleshooting and feature reference!*
