# CUSTOMER DASHBOARD - VISUAL GUIDE & REFERENCE

## 🎨 Color Palette

### Primary Colors
```
Primary:     #667eea  ■■■■■ Purple-Blue (Main brand color)
Secondary:   #764ba2  ■■■■■ Purple (Accents, gradients)
```

### Status Colors
```
Success:     #48bb78  ■■■■■ Green (Delivered, Active, Completed)
Danger:      #f56565  ■■■■■ Red (Cancelled, Error, Danger)
Warning:     #ed8936  ■■■■■ Orange (Pending, Paused, Warning)
Info:        #4299e1  ■■■■■ Blue (Shipped, Processing, Info)
```

### Neutral Colors
```
Light BG:    #f7fafc  ■■■■■ Light gray (Backgrounds)
Border:      #e2e8f0  ■■■■■ Light border (Dividers, borders)
Text Dark:   #2d3748  ■■■■■ Dark gray (Primary text)
Text Light:  #718096  ■■■■■ Medium gray (Secondary text)
White:       #ffffff  ■■■■■ White (Card backgrounds)
```

### Gradient
```
Default Gradient: #667eea → #764ba2 (Left to Right)
Alternative: 135deg (Diagonal)
Usage: Headers, buttons, widgets
```

---

## 📐 Layout Components

### Dashboard Card
```
┌─────────────────────────────────┐
│  Title              [Action Button]
├─────────────────────────────────┤
│                                 │
│   Main Content                  │
│                                 │
└─────────────────────────────────┘
```

**CSS**:
```css
.dashboard-card {
    background: white;
    border-radius: 0.8rem;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: 1px solid #e2e8f0;
}
```

---

### Stat Card
```
┌──────────────────┐
│  Label           │  ← Icon (right side, 30% opacity)
│  Value (2.5rem)  │
│  [Action Button] │
└──────────────────┘
```

**CSS**:
```css
.stat-card {
    background: white;
    border-radius: 1rem;
    padding: 1.5rem;
    min-width: 250px;
    border: 1px solid #e2e8f0;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}
```

---

### Gradient Header
```
╔════════════════════════════════════╗
║  🎯 Welcome back, John!            ║
║  Here's your dashboard overview    ║
╚════════════════════════════════════╝
```

**CSS**:
```css
.dashboard-header {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 2.5rem;
    border-radius: 1rem;
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
}
```

---

### Sidebar Navigation
```
┌──────────────────────┐
│ 👤 John Doe          │
├──────────────────────┤
│ ACCOUNT              │
│ • Dashboard          │  ← Active
│ • My Orders          │
│ • Subscriptions      │
├──────────────────────┤
│ REWARDS              │
│ • Loyalty & Rewards  │
│ • Billing & Invoices │
├──────────────────────┤
│ HEALTH               │
│ • Meal Plans         │
│ • Consultations      │
│ • Health Reports     │
├──────────────────────┤
│ SETTINGS             │
│ • My Profile         │
│ • Notifications      │
└──────────────────────┘
```

**CSS**:
```css
.dashboard-sidebar {
    width: 280px;
    background: linear-gradient(180deg, #2d3748, #1a202c);
    color: white;
    position: sticky;
    top: 80px;
    height: calc(100vh - 80px);
}

.nav-link-custom.active {
    background: #667eea;
    border-left: 4px solid white;
}
```

---

### Badge System
```
✓ Delivered    → Green background, dark text
⏳ Pending     → Orange background, dark text
📦 Shipped     → Blue background, dark text
✗ Cancelled    → Red background, dark text
```

**CSS**:
```css
.badge-custom {
    padding: 0.4rem 0.8rem;
    border-radius: 2rem;
    font-size: 0.8rem;
    font-weight: 600;
}

.badge-success {
    background: rgba(72, 187, 120, 0.2);
    color: #22543d;
}
```

---

### Button Styles

#### Primary (Gradient)
```
┌──────────────────────┐
│ ➔ Action             │  ← Purple gradient
└──────────────────────┘
```

**CSS**:
```css
.btn-primary-custom {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 0.6rem;
}

.btn-primary-custom:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
}
```

#### Secondary (White with Border)
```
┌──────────────────────┐
│ ➔ View               │  ← White with border
└──────────────────────┘
```

**CSS**:
```css
.btn-secondary-custom {
    background: white;
    color: #667eea;
    border: 1px solid #e2e8f0;
}

.btn-secondary-custom:hover {
    background: #f7fafc;
    border-color: #667eea;
}
```

---

### Delivery Widget
```
╔════════════════════════════════════╗
║ 📦 Your Deliveries               ║
├────────────────────────────────────┤
║ Order #123          Status: Shipped║
║ Est. Delivery: Jan 15, 2024        ║
║ [Track Order]                      ║
║                                    ║
║ Order #124          Status: Pending║
║ Est. Delivery: Jan 16, 2024        ║
║ [Track Order]                      ║
╚════════════════════════════════════╝
```

**CSS**:
```css
.delivery-widget {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 2rem;
    border-radius: 1rem;
}

.delivery-info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
}

.delivery-info-item {
    background: rgba(255, 255, 255, 0.15);
    padding: 1.5rem;
    border-radius: 0.8rem;
    backdrop-filter: blur(10px);
}
```

---

### Order Card
```
┌──────────────────────────────────────┐
│ Order #123          ✓ Delivered      │  ← Left border color-coded
├──────────────────────────────────────┤
│ Jan 15, 2024 • 2:30 PM • 3 items    │
├──────────────────────────────────────┤
│ Items:                               │
│ • Grilled Chicken Salad    Qty: 1   │
│ • Quinoa Bowl              Qty: 2   │
│ • Green Smoothie           Qty: 1   │
├──────────────────────────────────────┤
│ Delivery Information                 │
│ Status: Delivered                    │
│ Address: 123 Main St...             │
├──────────────────────────────────────┤
│ [View Details] [Repeat] [Receipt]   │
└──────────────────────────────────────┘
```

---

### Breadcrumb Navigation
```
🏠 Dashboard > My Orders
```

**CSS**:
```css
.breadcrumb {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}

.breadcrumb-item a {
    color: #667eea;
    text-decoration: none;
}

.breadcrumb-item.active {
    color: #718096;
}
```

---

## 📱 Responsive Breakpoints

### Desktop (> 992px)
```
┌─────────────────────────────────────────┐
│ SIDEBAR (280px) │  MAIN CONTENT        │
│ Sticky          │  Full width          │
│                 │  4-column grids      │
│                 │  All features        │
└─────────────────────────────────────────┘
```

### Tablet (768px - 992px)
```
┌─────────────────────────────────────┐
│ SIDEBAR (horizontal scroll at top) │
├─────────────────────────────────────┤
│  MAIN CONTENT (full width)          │
│  2-3 column grids                   │
│  Optimized for touch                │
└─────────────────────────────────────┘
```

### Mobile (< 768px)
```
┌──────────────────┐
│ HEADER (compact) │
├──────────────────┤
│ MAIN CONTENT     │
│ 1 column grid    │
│ Full width cards │
│ Optimized fonts  │
└──────────────────┘
```

---

## 🎭 Interactive States

### Hover State (Cards)
```
Before:                After:
┌────────────┐         ┌────────────┐
│ Content    │    →    │ Content    │  (lifted 4px)
└────────────┘         └────────────┘
```

### Active State (Sidebar)
```
Before:                After:
□ Dashboard      →    ■ Dashboard  (blue background)
                      with left border indicator
```

### Focus State (Buttons)
```
[Normal]  →  [Focused with outline]
```

### Disabled State
```
[Normal]  →  [Disabled - opacity 0.6, no cursor]
```

---

## 📊 Responsive Grid Examples

### 4-Column Grid (Desktop)
```
┌──────┬──────┬──────┬──────┐
│ Card │ Card │ Card │ Card │
└──────┴──────┴──────┴──────┘
```

**CSS**: `grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));`

### 2-Column Grid (Tablet)
```
┌──────────┬──────────┐
│   Card   │   Card   │
├──────────┼──────────┤
│   Card   │   Card   │
└──────────┴──────────┘
```

### 1-Column Grid (Mobile)
```
┌────────────┐
│   Card     │
├────────────┤
│   Card     │
├────────────┤
│   Card     │
└────────────┘
```

---

## 🔤 Typography

### Headings
```
h1: 2rem, bold, primary color        (Dashboard title)
h2: 1.3rem, bold, primary color      (Section titles)
h3: 1.1rem, bold, primary color      (Card titles)
h5: 1rem, bold, dark text            (Subsections)
h6: 0.85rem, bold, secondary text    (Labels)
```

### Body Text
```
Regular: 0.95rem, dark text          (Content)
Small: 0.85rem, secondary text       (Metadata)
Tiny: 0.8rem, secondary text         (Labels)
```

### Font Weight
```
Regular: 400
Semi-bold: 600
Bold: 700
Extra Bold: 800 (Not used usually)
```

---

## 🎯 Icon Usage

### Navigation Icons
```
🏠 Dashboard     → bi-speedometer2
📦 Orders        → bi-bag-check
📅 Subscriptions → bi-calendar2-check
⭐ Loyalty       → bi-star
👤 Profile       → bi-person-circle
❤️ Health        → bi-heart-pulse
💬 Consultations → bi-chat-dots
📊 Reports       → bi-file-text
⚙️ Settings      → bi-gear
🔔 Notifications → bi-bell
```

### Action Icons
```
➕ Add           → bi-plus-circle
✏️ Edit          → bi-pencil
👁️ View          → bi-eye
🔗 Open          → bi-arrow-right
❌ Delete        → bi-trash
✓ Confirm        → bi-check-circle
⏸️ Pause         → bi-pause-circle
🔄 Repeat        → bi-arrow-repeat
📥 Download      → bi-download
📤 Share         → bi-share
```

---

## ✨ Animation Reference

### Transitions
```
All animations use: 0.3s ease
- Hover effects
- State changes
- Loading states
```

### Transform Effects
```
Hover lift:    translateY(-2px) to (-4px)
Scale:         scale(1) to scale(1.02)
Opacity:       1 to 0.8 (disabled)
```

### Shadows
```
Resting:       0 2px 8px rgba(0, 0, 0, 0.05)
Hover:         0 12px 24px rgba(0, 0, 0, 0.1)
Elevated:      0 8px 24px rgba(color, 0.2)
```

---

## 📏 Spacing Scale (rem-based)

```
0.25rem  → xs (1/4)
0.5rem   → s  (1/2)
0.75rem  → sm (3/4)
1rem     → base
1.5rem   → md
2rem     → lg
2.5rem   → xl
3rem     → xxl
```

---

## 🔍 Quick Component Lookup

| Component | Class | Usage |
|-----------|-------|-------|
| Card | `.dashboard-card` | Content container |
| Header | `.dashboard-header` | Gradient header |
| Stats | `.stat-card` | Metrics display |
| Table | `.dashboard-table` | Data tables |
| Button Primary | `.btn-primary-custom` | Main actions |
| Button Secondary | `.btn-secondary-custom` | Secondary actions |
| Badge | `.badge-custom` | Status indicators |
| Sidebar | `.dashboard-sidebar` | Navigation |
| Widget | `.delivery-widget` | Info widget |

---

## 🎨 Creating New Components

### Template
```django
<div class="dashboard-card">
    <div class="card-header">
        <h2>Section Title</h2>
        <button class="btn-custom btn-primary-custom">Action</button>
    </div>
    
    <!-- Content here -->
</div>
```

### Color Usage
```css
/* Always use variables */
color: var(--text-primary);
background: var(--primary-color);
border: 1px solid var(--border-color);
```

### Grid Usage
```css
/* For responsive layouts */
display: grid;
grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
gap: 1.5rem;
```

### Button Usage
```django
<!-- Primary action -->
<a class="btn-custom btn-primary-custom">
    <i class="bi bi-icon"></i> Action
</a>

<!-- Secondary action -->
<a class="btn-custom btn-secondary-custom">
    <i class="bi bi-icon"></i> View
</a>
```

---

## 🧪 Testing Checklist

- [ ] Colors match spec
- [ ] Typography hierarchy correct
- [ ] Spacing consistent
- [ ] Icons display
- [ ] Gradients render
- [ ] Shadows correct
- [ ] Hover effects work
- [ ] Mobile responsive
- [ ] Tablet responsive
- [ ] Desktop layout
- [ ] Touch targets 44px+
- [ ] Text readable
- [ ] No scroll issues
- [ ] Links work
- [ ] Forms submit
- [ ] Empty states show

---

**Version**: 1.0
**Last Updated**: Today
**Status**: Complete Reference Guide
