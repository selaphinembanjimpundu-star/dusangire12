# Phase 2.2: Admin Interface User Guide

## Overview
This guide explains how to use the new Phase 2.2 admin interfaces for managing VIP tiers, loyalty points, referrals, and auto-renewals.

---

## 1. VIP Tier Management

**Access**: Django Admin → Subscriptions → VIP Tiers

### Understanding Tiers
- **Bronze**: 2% loyalty bonus, 0% discount (Default tier)
- **Silver**: 5% loyalty bonus, 5% discount (RWF 500K+ spending)
- **Gold**: 10% loyalty bonus, 10% discount (RWF 2M+ spending)
- **Platinum**: 15% loyalty bonus, 15% discount + benefits (RWF 5M+ spending)

### Key Fields to Monitor
- **Spending YTD**: Year-to-date spending (tracks current year performance)
- **Spending Total**: Lifetime spending (determines tier level)
- **Promotion %**: Auto-calculated loyalty bonus percentage
- **Next Tier Threshold**: How much more customer needs to spend to reach next tier

### Example Scenario
A customer with "Silver" tier and "Spending Total: RWF 500,000":
- They've spent RWF 500,000 lifetime
- Current year spending: Check "Spending YTD" field
- When they hit RWF 2,000,000 total → Upgrade to Gold automatically
- Next Tier Threshold will show: RWF 1,500,000 remaining

### Admin Actions
1. **View Customer Tier**: Click username to see all tier details
2. **Check Tier History**: Use "Achieved At" to see when tier was reached
3. **Filter by Tier**: Use "Tier Level" dropdown to find all Platinum customers
4. **Review Benefits**: Click tier name to see tier-specific benefits (perks, discounts)

---

## 2. Loyalty Points Management

**Access**: Django Admin → Subscriptions → Loyalty Points

### Understanding the System
- **1 Point = RWF 100** (fixed exchange rate)
- **Balance**: Current available points (e.g., 2,500 points = RWF 250,000 credit)
- **Earned Total**: All points ever earned (never decreases)
- **Redeemed Total**: All points ever used (never decreases)
- **Bonus Rate**: Point earning multiplier (1.0 = normal, 1.05 = 5% bonus)

### Key Displays
- **"2,500 pts / RWF 250,000"**: Customer has 2,500 points worth RWF 250,000
- **"Earned: 5,000 pts"**: Customer has earned 5,000 points in their lifetime
- **"Redeemed: 2,500 pts"**: Customer has used 2,500 points
- **"Bonus Rate: +5%"**: This customer earns 5% more points than normal (Silver tier)

### Customer Earning Examples
| Scenario | Points Earned | Notes |
|----------|---------------|-------|
| Spends RWF 10,000 (Bronze 1.0x) | 100 pts | Base rate: 1pt per 100 RWF |
| Spends RWF 10,000 (Silver 1.05x) | 105 pts | 5% bonus from tier |
| Spends RWF 10,000 (Platinum 1.15x) | 115 pts | 15% bonus from tier |

### Admin Actions
1. **Search Customer**: Use search box (username or email)
2. **View Transaction History**: Click customer name → View associated transactions
3. **Check Expiration**: See if points expire (null = no expiration)
4. **Manual Adjustment**: Use "Notes" field to document any manual point awards
5. **Filter by Activity**: Use "Last Activity At" to find recently active customers

### Important Note
- Do NOT manually edit "Earned Total" or "Redeemed Total" (these are auto-calculated)
- Use "Notes" field for documentation instead
- Balance should match: Earned Total - Redeemed Total

---

## 3. Loyalty Transactions (Audit Trail)

**Access**: Django Admin → Subscriptions → Loyalty Transactions

### Understanding Transaction Types
- **+ EARN**: Customer earned points (from subscription/spending)
- **- REDEEM**: Customer used points (redeemed for credit/discount)
- **★ BONUS**: VIP tier bonus or referral reward
- **⚙ ADJUSTMENT**: Admin manual adjustment

### What Each Column Shows
| Column | Meaning | Example |
|--------|---------|---------|
| Type | How points moved | EARN, REDEEM, BONUS, ADJUSTMENT |
| Points Amount | How many points | 100 points earned |
| Change | Net balance change | Green +100, Red -50 |
| Created At | When it happened | 2024-01-15 10:30 |

### Example Transaction
Customer redeems 500 points for discount:
- **Type**: - REDEEM
- **Points Amount**: 500
- **Change**: -500 (shown in red)
- **Balance Before**: 2,500
- **Balance After**: 2,000
- **Description**: "Redeemed for meal discount"

### Audit Trail Use Cases
1. **Customer Question**: "Why did my points decrease?" → Check transactions
2. **Debugging**: "Customer should have more points" → Trace earning history
3. **Compliance**: "Prove the bonus was awarded" → Show BONUS transaction
4. **Reports**: Filter by date range to see monthly point activity

### Filters & Search
- **By Type**: Show only EARN/REDEEM/BONUS/ADJUSTMENT
- **By Date**: Find transactions in specific period
- **By Customer**: Search username to see all their transactions
- **By Description**: Search keywords in reason

---

## 4. Referral Program Management

**Access**: Django Admin → Subscriptions → Referral Programs

### Understanding the System
**Referrer** (Person making referral):
- Gives someone a link: `https://dusangire.rw/refer/{code}`
- If referred person signs up → Referrer gets RWF 10,000 + 100 points

**Referee** (Person being referred):
- Gets 10% discount on first subscription
- Completes first purchase → Status becomes COMPLETED

### Status Tracking
| Status | Meaning | What to Do |
|--------|---------|-----------|
| PENDING | Waiting for referee to use link | Monitor for completion |
| COMPLETED | Referee completed first purchase | Bonus awarded to referrer |
| EXPIRED | Link expired (no action taken) | Can generate new referral |
| CANCELLED | Referral was cancelled | Cannot be reused |

### Example Workflow
1. **Day 1**: Create referral for Customer A
   - Generate referral code: `REF12345`
   - Status: PENDING
   - Bonus (pending): RWF 10,000 + 100 pts to referrer

2. **Day 3**: Customer B receives link and signs up
   - Referee field now shows: Customer B
   - Still Status: PENDING

3. **Day 5**: Customer B completes first subscription purchase
   - Status changes to: COMPLETED
   - Customer A receives: RWF 10,000 + 100 pts
   - LoyaltyTransaction created with BONUS type

### Admin Actions
1. **Create Referral**: Add referrer, leave referee empty, set expires_at
2. **Share Link**: Copy "Referral Link" field to send to referrer
3. **Track Conversion**: Monitor "Completed At" to see when referee purchased
4. **Bulk Manage**: Select multiple referrals and change status
5. **Expiration**: Set "Expires At" to prevent stale referrals

### Performance Dashboard
Use filters to see:
- **Most Active Referrers**: Filter status=COMPLETED, sort by created_at
- **Conversion Rate**: Count COMPLETED vs total referrals
- **Revenue**: Calculate: Completed referrals × (Referee discount impact)

---

## 5. Auto-Renewal Configuration

**Access**: Django Admin → Subscriptions → Subscription Auto-Renewals

### Understanding Auto-Renewal

**Timeline Example** (30-day subscription):
```
Day 27: NOTIFICATION SENT → "Your subscription renews in 3 days"
Day 30: RENEWAL DAY → System attempts charge
        ✓ SUCCESS → Next renewal scheduled 30 days later
        ✗ FAILED → Retry tomorrow (failure_count: 1/3)
Day 31: RETRY 1 → Attempt charge again
        ✓ SUCCESS → Status = SUCCESS, back to normal
        ✗ FAILED → Retry day after (failure_count: 2/3)
Day 32: RETRY 2 → Attempt charge again
        ✓ SUCCESS → Status = SUCCESS, back to normal
        ✗ FAILED → Retry final time (failure_count: 3/3)
Day 33: RETRY 3 → Final attempt
        ✓ SUCCESS → Status = SUCCESS, back to normal
        ✗ FAILED → Status = FAILED, notify customer
```

### Key Fields

| Field | Meaning | Example |
|-------|---------|---------|
| Auto Renew Enabled | Is renewal active? | ✓ Yes / ✗ No |
| Renewal Date | When next charge happens | 2024-01-30 |
| Renewal Interval | Days between renewals | 30 days |
| Notification Days Before | When to warn customer | 3 days |
| Failure Count | Failed attempts so far | 2/3 attempts |
| Last Renewal Status | Previous charge result | SUCCESS/FAILED |

### Failure Scenarios

**Scenario 1**: Payment Method Expired
- Failure 1/3: Charge fails, retry tomorrow
- Send customer email: "Payment failed, we'll retry tomorrow"
- Customer updates payment method
- Failure 2: Charge succeeds, renewal completes

**Scenario 2**: Insufficient Funds
- Failure 1/3, 2/3, 3/3: All fail
- Status = FAILED
- Send customer: "Subscription failed after 3 attempts. Please update payment method."

### Admin Actions

1. **Enable Auto-Renewal**: Select subscription → "✓ Enable Auto-Renewal"
2. **Disable Auto-Renewal**: Select subscription → "✗ Disable Auto-Renewal"
3. **Retry Failed Renewal**: Select subscription → "↻ Retry Failed Renewals"
   - Resets failure_count to 0
   - Attempts charge again
   - Sets status = RETRY_QUEUED

4. **Monitor Failures**: Filter "Failures" column
   - "No failures" = Green (healthy)
   - "1/3 failures" = Yellow (monitoring)
   - "Max retries exceeded" = Red (action needed)

5. **Check Renewal Date**: Sort by "Renewal Date" to see upcoming renewals

### Troubleshooting

**"Payment failed, won't retry"**
- Check: Is failure_count = 3?
- Action: Click "Retry Failed Renewals" after customer fixes payment method

**"Notification not sent"**
- Check: Is notification_sent = null AND 0 < days_remaining ≤ 3?
- Action: Next scheduled task should send (no manual action needed)

**"Renewal date in past"**
- Check: Is renewal_date < today?
- Action: Click renewal record, update renewal_date to tomorrow or next billing cycle

---

## 6. Bulk Actions Reference

### VIP Tier Admin
No bulk actions (tier changes automatic)

### Loyalty Points Admin
- **Bulk Search**: Use search box to find customers by username/email
- **Export Data**: Django admin export (if configured)

### Loyalty Transaction Admin
- **No bulk actions** (transactions are immutable records)
- Use **Date Range Filter** to view period summaries

### Referral Program Admin
- **Enable Auto-Renewal**: Select multiple → "Enable Auto-Renewal"
- **Disable Auto-Renewal**: Select multiple → "Disable Auto-Renewal"
- **Retry Failed Renewals**: Select multiple → "Retry Failed Renewals"
- **Bulk Status Change**: Select multiple → Change status dropdown

### Auto-Renewal Admin
- **✓ Enable Auto-Renewal**: Selected subscriptions will auto-renew
- **✗ Disable Auto-Renewal**: Selected subscriptions won't auto-renew
- **↻ Retry Failed Renewals**: Reset failures and retry charges

---

## 7. Filtering & Search Quick Reference

### VIP Tier Filters
- Tier Level: Bronze/Silver/Gold/Platinum
- Achieved At: Date range (when tier was reached)

### Loyalty Points Filters
- Last Activity At: Date range (when last transaction occurred)

### Loyalty Transaction Filters
- Type: EARN/REDEEM/BONUS/ADJUSTMENT
- Created At: Date range

### Referral Program Filters
- Status: PENDING/COMPLETED/EXPIRED/CANCELLED
- Created At: Date range
- Completed At: Date range (when referee purchased)

### Auto-Renewal Filters
- Auto Renew Enabled: Yes/No
- Renewal Date: Date range
- Last Renewal At: Date range

---

## 8. Common Tasks

### Task: Award Points to Customer
1. Go to Loyalty Points
2. Search customer by username
3. Click customer name
4. View "Loyalty Transactions"
5. Create new LoyaltyTransaction with type=BONUS
6. This will appear in their transaction history

### Task: Fix Wrong Tier
1. Go to VIP Tiers
2. Find customer
3. Click to edit
4. Update "Spending Total" to correct amount
5. Tier level will auto-adjust on next system check
6. Update "Achieved At" to today

### Task: Check Referral Conversion
1. Go to Referral Programs
2. Filter Status = COMPLETED
3. You'll see all successful referrals
4. Calculate: Completed referrals / Total referrals = Conversion Rate

### Task: Disable Auto-Renewal
1. Go to Subscription Auto-Renewals
2. Find subscription
3. Select it
4. Click "✗ Disable Auto-Renewal"
5. Uncheck "Auto Renew Enabled" and save

### Task: Investigate Payment Failure
1. Go to Subscription Auto-Renewals
2. Filter Failures = "Max retries exceeded"
3. Click subscription
4. Check "Last Renewal Status" (should show FAILED)
5. Check "Last Renewal At" (when last attempt was)
6. Contact customer to update payment method
7. Click "↻ Retry Failed Renewals" after fix

---

## 9. Dashboard Monitoring

### Daily Checks
- **Auto-Renewal Failures**: Filter for "Max retries exceeded" (red icon)
- **Pending Referrals**: Filter Referral Status = PENDING (near expiration)
- **Loyalty Redemptions**: Check LoyaltyTransaction type = REDEEM (customer satisfaction)

### Weekly Reports
- **VIP Tier Upgrades**: Filter Achieved At = past 7 days
- **Referral Conversions**: Count COMPLETED status created in past 7 days
- **Points Activity**: Total points earned/redeemed last week

### Monthly Analysis
- **Revenue from Referrals**: # Completed referrals × value per conversion
- **Loyalty Engagement**: % of customers with transactions last month
- **Tier Distribution**: How many customers in each tier
- **Auto-Renewal Success**: Successful renewals / Total renewal attempts

---

## 10. Tips & Best Practices

✅ **Do**:
- Use filters to find specific customers/transactions
- Check "Last Activity At" to identify active vs. inactive customers
- Use date ranges for monthly/quarterly reports
- Archive old referral links (set to EXPIRED)
- Monitor auto-renewal failures regularly

❌ **Don't**:
- Manually edit "Earned Total" or "Redeemed Total" (auto-calculated)
- Delete transactions (they're audit records)
- Create duplicate VIP tiers (OneToOne relationship)
- Change referral code after creation (breaks links)
- Ignore payment failures without customer follow-up

---

**Version**: 1.0 (Phase 2.2 Release)  
**Last Updated**: 2024  
**Related Files**: PHASE2_2_COMPLETION_SUMMARY.md
