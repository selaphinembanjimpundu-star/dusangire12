# Phase 3: Advanced Shopping Cart & Ordering - ENHANCEMENT PLAN

**Objective**: Integrate the newly built Loyalty, VIP, and Referral systems into the existing Shopping Cart and Ordering flow.

## 1. Database Enhancements (`orders/models.py`)

We need to update the `Order` model to store information about discounts and loyalty points used.

### New Fields for `Order`:
- `discount_amount`: Total discount applied (Decimal).
- `loyalty_points_redeemed`: Number of points used (Integer).
- `loyalty_discount_amount`: Value of points in RWF (Decimal).
- `vip_discount_amount`: Amount saved via VIP tier (Decimal).
- `referral_discount_amount`: Amount saved via referral code (Decimal).
- `coupon_code`: Optional coupon code used (String).

## 2. Business Logic (`orders/services.py`)

Create a service to handle price calculations to keep views clean.

### `OrderCalculationService`:
- `calculate_total(cart, user)`:
  - Subtotal
  - VIP Discount (based on `user.vip_tier`)
  - Referral Discount (if applicable)
  - Loyalty Redemption (if requested)
  - Delivery Fee
  - Final Total

## 3. Checkout Flow Enhancements

### 3.1 Checkout View (`orders/views.py`)
- Fetch user's VIP tier and calculate potential discount.
- Fetch user's loyalty points balance.
- Check for active referral discount (10% off first order).
- Allow user to input "Points to Redeem".
- Display breakdown: Subtotal - Discounts + Delivery = Total.

### 3.2 Checkout Template (`templates/orders/checkout.html`)
- Show "You are a [Gold] member! You save [10%]" badge.
- Show "You have [1200] points (Value: 1200 RWF). Redeem? [Input]"
- Show detailed pricing breakdown.

## 4. Post-Order Processing

- **Signal Updates**: Ensure the `Payment` completion signal (Phase 2.3) correctly handles the final amount.
- **Point Deduction**: If points were used, deduct them from `LoyaltyPoints` immediately upon order placement (or payment confirmation).

## 5. Implementation Steps

1.  **Modify Models**: Add fields to `Order`.
2.  **Create Service**: Implement `OrderCalculationService`.
3.  **Update Views**: Integrate service into `checkout` and `place_order` views.
4.  **Update Templates**: Add UI for discounts and points.
5.  **Verify**: Test the full flow.

---
