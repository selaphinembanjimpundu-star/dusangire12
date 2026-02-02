# Patient Menu & Meal Plan System - User-Friendly Guide

## Overview

The **Patient Menu & Meal Plan System** is designed to provide patients with an easy, intuitive way to:
- ✅ Understand their doctor-prescribed meal plan
- ✅ Browse available healthy meals
- ✅ Place food orders with special dietary notes
- ✅ Track their orders and meal history
- ✅ Monitor their recovery progress through nutrition

## System Components

### 1. Patient Dashboard (`/patient/dashboard/`)

**Purpose:** Central hub for all patient-related activities

**What You See:**
- 📋 **Active Meal Plan** - Your doctor's meal prescription
- 🛒 **Items in Cart** - Quick view of how many meals you've selected
- 📊 **Compliance Score** - Percentage of recommended meals consumed
- ✅ **Orders This Month** - How many orders you've placed
- 📜 **Recent Orders** - Your last 5 orders with status
- 👍 **Your Preferences** - Your dietary restrictions

**Key Buttons:**
- "View My Meal Plan" - See meals recommended by your doctor
- "Browse Menu" - See all available meals
- "My Cart" - Review selected meals before checkout

---

### 2. My Meal Plan (`/menu/my-meal-plan/`)

**Purpose:** Show personalized meal recommendations based on doctor's prescription

**What You See:**
- 🏥 **Your Meal Type** - e.g., "Diabetic-Friendly", "High-Protein", "Low-Sodium"
- 👨‍⚕️ **Prescribed By** - Your assigned doctor
- 📅 **Plan Duration** - From/to dates
- ⚠️ **Important Restrictions** - Dietary restrictions from your prescription
- 💚 **Meals That Match Your Plan** - Recommended meals from our menu
- 📋 **Browse All Meals** - See everything available

**User-Friendly Features:**
- Color-coded meal cards (easy to scan)
- Dietary badges showing what's in each meal
- One-click "Add to Cart" buttons
- Stars showing patient ratings
- Calorie and nutrition information

---

### 3. How to Order Guide (`/menu/how-to-order/`)

**Purpose:** Step-by-step instructions for patients

**5-Step Process:**

#### Step 1: Understand Your Meal Plan
- What is a meal plan?
- Different meal types explained in simple language
- How to find your plan on the dashboard

#### Step 2: Browse Available Meals
- How to search for meals
- How to filter by category
- Understanding dietary labels
- Reading customer reviews

#### Step 3: Add Meals to Cart
- How to add meals
- How to add special dietary notes (allergies, preferences)
- Examples of special requests

#### Step 4: Checkout
- Select delivery location
- Add special instructions for kitchen
- Choose payment method
- Review order total

#### Step 5: Track Your Order
- Understand order statuses:
  - ⏳ Pending - Kitchen is receiving order
  - ✓ Confirmed - Kitchen confirmed it
  - 🍳 Preparing - Chef is cooking
  - 📦 Ready - Meal is ready
  - 🚚 Delivered - It's arrived!
- Track estimated delivery time

---

## User-Friendly Terminology

### Translation Chart: Technical → Patient-Friendly

| Technical Term | Patient-Friendly | Explanation |
|---|---|---|
| Medical Prescription | Your Meal Plan | Doctor's meal recommendations |
| Delivery Address | Your Room/Ward | Where to deliver your meal |
| Special Requests | Your Dietary Notes | Tell kitchen about allergies |
| Dietary Tags | Meal Labels | Shows what type of meal it is |
| Cart | Your Selections | Meals you want to order |
| Order Status | Where's My Meal? | Track your order |
| PatientMealHistory | Your Meal History | Meals you've ordered |
| Compliance Percentage | Your Progress | How many meals you've eaten |
| Health Profile | Your Medical Info | Your health conditions |

---

## Key Features & How to Use Them

### 🔍 Search Meals
```
How: Type meal name in search box
Example: "rice", "chicken", "soup"
Result: See all meals with that ingredient
```

### 🏷️ Filter by Category
```
How: Select category from dropdown
Options: Breakfast, Lunch, Dinner, Snacks
Result: See meals for that time of day
```

### ❤️ Dietary Filters
```
How: Click dietary tag badges
Tags: Diabetic-Friendly, Low-Sodium, High-Protein, etc.
Result: See only meals for your diet type
```

### ⭐ Read Reviews
```
How: Look at star ratings on each meal
Stars: 1-5, where 5 is best
Result: Helps you pick good meals
```

### 📝 Add Special Notes
```
During Checkout, use the Special Notes box:

Examples:
✓ "Allergic to peanuts"
✓ "No salt, please"
✓ "Cut into small pieces"
✓ "Extra spice"
✓ "Cannot eat dairy"
```

### 🛒 Manage Cart
```
At /orders/cart/:
- See all selected meals
- Adjust quantities
- Remove meals you don't want
- See total price
- Proceed to checkout
```

### 💳 Payment Options
```
Available methods:
1. 💵 Cash on Delivery
2. 📱 Mobile Money (MTN, Airtel)
3. 🏦 Bank Transfer
4. 💳 Debit/Credit Card
```

---

## Order Statuses Explained

When you order a meal, it goes through these stages:

| Status | Icon | Meaning | Time |
|---|---|---|---|
| **Pending** | ⏳ | Kitchen received your order | 5-10 min |
| **Confirmed** | ✓ | Chef will start cooking | 10-15 min |
| **Preparing** | 🍳 | Chef is actively cooking | 20-40 min |
| **Ready** | 📦 | Meal is packaged and ready | 5-10 min |
| **Delivered** | 🚚 | At your room! | 10-20 min |

**Total time: Usually 1 hour from order to delivery**

---

## Understanding Meal Types (Simplified)

### 🍚 Diabetic-Friendly
**For:** Patients with diabetes or high blood sugar
**What:** Low sugar, controlled portions
**Example:** Brown rice, grilled chicken, steamed vegetables

### 🧂 Low-Sodium
**For:** Heart patients or high blood pressure
**What:** Low salt, promotes heart health
**Example:** Boiled vegetables, unsalted rice, grilled fish

### 💪 High-Protein
**For:** Recovery and muscle building
**What:** Extra protein for strength
**Example:** Eggs, beans, chicken, fish

### 🫒 Low-Fat
**For:** Easy digestion or weight management
**What:** Light and easy on stomach
**Example:** Grilled vegetables, white rice, lean meat

### 🥬 Vegetarian
**For:** Patients who don't eat meat
**What:** Plant-based, nutritious meals
**Example:** Beans, lentils, vegetables, grains

### 🌾 Gluten-Free
**For:** Celiac disease or gluten sensitivity
**What:** No wheat, no gluten
**Example:** Corn, rice, vegetables, beans

---

## Special Requests - Complete Guide

### When to Add Special Requests?

**ALWAYS add notes about:**
- ❌ Allergies
- 🚫 Foods to avoid
- 📝 Portion preferences
- 🍽️ Preparation preferences

### Example Special Requests

**Allergies:**
```
"I am allergic to peanuts. Please avoid all peanut products."
"Cannot eat eggs - I am allergic"
"Allergic to shellfish"
```

**Dietary Preferences:**
```
"Very spicy, please"
"No salt at all"
"Extra pepper on the side"
"Cut into small, easy-to-chew pieces"
```

**Portions:**
```
"Small portion - I'm not very hungry"
"Extra portion - I'm very hungry"
"Half of normal portion"
```

**Preparation:**
```
"Very soft - I have trouble chewing"
"Warm but not hot"
"On the side: sauce, dressing, toppings"
```

---

## Meal Compliance Tracking

### What is Compliance?
**Answer:** The percentage of meals you've eaten vs. meals your doctor recommended

### How Does It Work?
```
Formula: (Meals eaten ÷ Meals recommended) × 100 = Compliance %

Example:
- Doctor recommended: 20 meals this week
- You've eaten: 15 meals
- Compliance: 75% ✓ Good!
```

### Why Does It Matter?
- ✅ Helps your doctor adjust your meal plan
- ✅ Tracks your recovery progress
- ✅ Shows what meals you like
- ✅ Helps optimize your nutrition

### How to Improve Compliance
1. Review your meal plan regularly
2. Pick meals you actually enjoy
3. Add special notes for customizations
4. Order consistently
5. Rate meals so we know what you like

---

## Troubleshooting Guide

### ❓ "I don't have a meal plan yet"
**Solution:** Check back tomorrow. Your doctor will assign one soon. In the meantime, you can still browse and order from our regular menu!

### ❓ "I have an allergy - will the kitchen know?"
**Solution:** YES - but ONLY if you write it in the Special Requests box during checkout. Always mention allergies clearly!

### ❓ "How long until my meal arrives?"
**Solution:** Typically 1 hour. Check your order status:
- Pending → 10 min
- Confirmed → 15 min
- Preparing → 25 min
- Ready → 10 min
- Delivered → Your meal is here!

### ❓ "Can I change my order?"
**Solution:** Depends on status:
- **Pending/Confirmed:** Contact support immediately
- **Preparing or later:** Usually too late, but try calling support

### ❓ "What if I don't like a meal?"
**Solution:** 
1. Leave a review so we know
2. Try a different meal next time
3. Contact support if there's a problem

### ❓ "How do I pay?"
**Solution:** Multiple options:
- Cash when meal is delivered
- Mobile Money (MTN/Airtel)
- Bank transfer
- Debit/credit card

### ❓ "Where do I see my order history?"
**Solution:** Go to Patient Dashboard → Recent Orders, or click "View" on any order.

---

## Patient Dashboard Features

### Quick Stats (Top Section)
```
📋 Active Meal Plan: Shows if you have one
🛒 Items in Cart: How many meals selected
📊 Compliance: Your progress %
✅ Orders This Month: How many orders
```

### Recent Orders Table
```
Shows:
- Date of order
- Number of items
- Total cost
- Current status (Pending/Confirmed/Preparing/Ready/Delivered)
- View button to see details
```

### Your Preferences
```
Shows:
- Your meal type (Diabetic, Low-Sodium, etc.)
- Any dietary restrictions
- Your doctor's name
- Plan start/end dates
```

### Quick Actions
```
Buttons to quickly navigate to:
1. View My Meal Plan
2. Browse Menu
3. View Cart
```

---

## Tips for Success

### 📋 Best Practices
1. **Check your meal plan daily** - See what's recommended
2. **Read meal descriptions** - Understand what you're ordering
3. **Read reviews** - See what others thought
4. **Add special notes** - Especially for allergies
5. **Order early** - Get your favorites before they run out
6. **Track your order** - Know when it's arriving
7. **Rate meals** - Help us improve

### 🚫 Common Mistakes to Avoid
1. ❌ Forgetting to add allergy info in special requests
2. ❌ Ordering meals you don't like
3. ❌ Not checking order status
4. ❌ Asking kitchen about changes after "Preparing" status
5. ❌ Not mentioning portion preferences

### ✅ Pro Tips
1. ✓ Bookmark your favorite meals for quick reordering
2. ✓ Order breakfast/lunch by 10 AM
3. ✓ Order dinner by 3 PM
4. ✓ Check ratings before trying new meals
5. ✓ Be specific in special requests - ambiguous notes confuse the kitchen

---

## Patient Privacy & Security

### Your Data is Safe
- ✅ Your medical information is private
- ✅ Only your doctor sees your meal plan
- ✅ Order history is only for you
- ✅ Your payment info is encrypted

### What We Collect
- Order history (so we can track your meals)
- Allergy info (to keep you safe)
- Dietary preferences (to help you)
- Ratings (to improve meals)

### What We Don't Share
- Your personal information
- Your medical conditions
- Your meal preferences (without permission)
- Your payment details

---

## Contact Support

### When to Contact Support
- ❓ Questions about your meal plan
- 🚨 Allergy concerns
- 📦 Order not received
- 💳 Payment issues
- 🍽️ Problem with meal quality

### How to Contact
- 📞 Hospital Front Desk
- 📧 support@dusangire.rw
- 💬 Chat with support staff
- 🏥 Contact your assigned nurse

---

## FAQs

**Q: Can I see nutrition information?**
A: Yes! Each meal shows calories, protein, fat, carbs.

**Q: Can I reorder meals I've had before?**
A: Yes! Click "Reorder" on any past order.

**Q: What if my meal doesn't arrive?**
A: Contact support immediately. We'll either find your meal or remake it.

**Q: Can I cancel an order?**
A: Only if it's still "Pending". After that, contact support.

**Q: How do I rate a meal?**
A: After delivery, click "Rate" on the order details page.

**Q: Can my family member order for me?**
A: Ask support about proxy ordering options.

---

## Conclusion

The **Patient Menu & Meal Plan System** is designed to make eating healthy meals easy and convenient during your recovery. We use simple, understandable language and provide clear guidance at every step.

### Remember:
- 🎯 Your meal plan is customized for YOUR health
- 🍽️ Every meal is prepared with care
- 🏥 The kitchen team is trained to handle allergies
- 📞 Support is always available if you need help
- 💪 Healthy eating is part of your recovery!

### Quick Links
- [Patient Dashboard](/patient/dashboard/)
- [My Meal Plan](/menu/my-meal-plan/)
- [How to Order Guide](/menu/how-to-order/)
- [Browse Menu](/menu/)

---

**Made with ❤️ for your recovery**
*Dusangire - Healthy Eating for Healthy Recovery*
