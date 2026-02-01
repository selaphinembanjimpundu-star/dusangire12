# Phase 2.4: API Development & Automation - PLAN

**Status**: 🏗️ **IN PROGRESS**
**Objective**: Expose subscription and loyalty features via REST API and implement background automation.

## 1. API Development (`subscriptions/serializers.py`, `subscriptions/api.py`)

We need to create RESTful endpoints for the frontend/mobile app to interact with the new systems.

### 1.1 Serializers
- **VIPTierSerializer**: Tier level, benefits, progress to next tier.
- **LoyaltyPointsSerializer**: Balance, value in RWF, lifetime stats.
- **LoyaltyTransactionSerializer**: History of points earned/redeemed.
- **ReferralProgramSerializer**: Referral code, link, status, bonuses.
- **SubscriptionAutoRenewalSerializer**: Renewal status, next date, enabled flag.

### 1.2 API Endpoints
- **Loyalty**:
  - `GET /api/loyalty/status/`: Get points balance and VIP tier.
  - `GET /api/loyalty/history/`: Get transaction history.
  - `POST /api/loyalty/redeem/`: Redeem points for credit.
- **Referrals**:
  - `GET /api/referrals/info/`: Get user's referral code and link.
  - `GET /api/referrals/stats/`: Get count of successful referrals.
- **Subscriptions**:
  - `POST /api/subscriptions/<id>/auto-renew/`: Toggle auto-renewal.
  - `GET /api/subscriptions/<id>/renewal-info/`: Get renewal details.

## 2. Automation (`subscriptions/management/commands/process_renewals.py`)

Create a Django management command to be run via cron/scheduler.

- **Command**: `python manage.py process_renewals`
- **Logic**: Calls `SubscriptionRenewalService.process_auto_renewals()`
- **Output**: Logs success/failure counts.

## 3. Implementation Steps

1.  Create `subscriptions/serializers.py`.
2.  Create `subscriptions/api.py` (API Views).
3.  Register URLs in `subscriptions/urls.py`.
4.  Create management command `process_renewals`.
5.  Verify endpoints using a test script.

---
