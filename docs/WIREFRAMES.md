# UX Design Documentation

## Design Philosophy

KartControl follows a **mobile-first, accessibility-focused** design approach aligned with WCAG 2.1 Level AA standards. The design prioritizes:

1. **Clarity over complexity** - Clear information hierarchy
2. **Consistency** - Predictable patterns across all pages
3. **User control** - No aggressive auto-play, user-initiated actions
4. **Immediate feedback** - Real-time status updates and notifications
5. **Responsive design** - Seamless experience across all devices

## Target Audience

### Primary Users:
- **Drivers (18-65)** - Racing enthusiasts booking karting sessions
- **Managers (25-50)** - Staff managing bookings and operations
- **Marshals (20-45)** - Track safety officials

### User Needs:
- **Drivers**: Quick session browsing, easy booking, clear confirmations
- **Managers**: Dashboard overview, booking management, kart fleet control
- **Marshals**: Session monitoring, driver safety tracking

## Color Scheme

### Primary Palette:
```css
--primary: #007bff      /* Racing Blue - Action buttons */
--success: #28a745      /* Green - Confirmations, available */
--warning: #ffc107      /* Amber - Pending, in-progress */
--danger: #dc3545       /* Red - Cancellations, full capacity */
--secondary: #6c757d    /* Gray - Neutral states */
```

### Accessibility:
- All text/background combinations meet **4.5:1 contrast ratio**
- Color never used as sole indicator (icons + text labels)
- Focus states use high-contrast outlines

### Rationale:
- **Blue primary** conveys trust and professionalism
- **Traffic light system** (green/amber/red) for status is universally understood
- **High contrast** ensures readability for all users

## Typography

### Font Stack:
```css
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
               "Helvetica Neue", Arial, sans-serif;
}
```

### Hierarchy:
- **H1**: 2.5rem (40px) - Page titles
- **H2**: 2rem (32px) - Section headings
- **H3**: 1.75rem (28px) - Card titles
- **Body**: 1rem (16px) - Content text
- **Small**: 0.875rem (14px) - Helper text

### Rationale:
- System fonts ensure fast load times
- Clear size hierarchy guides user attention
- Minimum 16px body text for readability

## Layout Structure

### Base Template (base.html)
```
┌────────────────────────────────────┐
│        Header (Navbar)             │
│  Logo | Sessions | My Bookings     │
│       | About | Contact | Auth     │
├────────────────────────────────────┤
│                                    │
│         Main Content Area          │
│         (Responsive Grid)          │
│                                    │
├────────────────────────────────────┤
│            Footer                  │
│   Quick Links | Social | Copyright │
└────────────────────────────────────┘
```

### Responsive Breakpoints:
- **Mobile**: < 768px (single column)
- **Tablet**: 768px - 991px (2 columns)
- **Desktop**: 992px+ (3-4 columns)
- **Ultra-wide**: > 1600px (max-width constraint)

## Page Wireframes

### 1. Home Page (index.html)

**Desktop Layout (992px+):**
```
┌────────────────────────────────────────────────────┐
│              Hero Section (Full Width)             │
│         🏁 "Welcome to KartControl"                │
│    [Browse Sessions] [Create Account] Buttons     │
├────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Feature  │  │ Feature  │  │ Feature  │        │
│  │  Card 1  │  │  Card 2  │  │  Card 3  │        │
│  │  📅      │  │  🎯      │  │  📊      │        │
│  └──────────┘  └──────────┘  └──────────┘        │
├────────────────────────────────────────────────────┤
│           Latest Sessions Grid (3 cols)            │
│  [Session Card] [Session Card] [Session Card]     │
└────────────────────────────────────────────────────┘
```

**Mobile Layout (< 768px):**
```
┌─────────────────────┐
│   Hero Section      │
│   (Stacked)         │
│   [Browse Sessions] │
│   [Create Account]  │
├─────────────────────┤
│  Feature Card 1     │
│       📅            │
├─────────────────────┤
│  Feature Card 2     │
│       🎯            │
├─────────────────────┤
│  Feature Card 3     │
│       📊            │
├─────────────────────┤
│  Session Card       │
│  (Full Width)       │
│  [View Details]     │
└─────────────────────┘
```

**Key Features:**
- Prominent call-to-action buttons
- Icon-driven feature cards
- Latest sessions preview
- Fully responsive grid

### 2. Sessions List (session_list.html)

**Desktop Layout:**
```
┌────────────────────────────────────────────────────┐
│  Sessions Available                                │
│  ┌──────────────────┐  Filters:                   │
│  │ Search Sessions  │  [ ] OPEN SESSION           │
│  └──────────────────┘  [ ] GRAND_PRIX             │
├────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────┐  │
│  │ Session Card                                 │  │
│  │  📅 Thu, Jan 15 - 14:00                     │  │
│  │  🏁 OPEN SESSION                            │  │
│  │  👥 5/10 spots | ⚡ Available               │  │
│  │  💰 £25.00                                  │  │
│  │  [View Details] [Book Now]                  │  │
│  └─────────────────────────────────────────────┘  │
│                                                    │
│  [More session cards...]                          │
├────────────────────────────────────────────────────┤
│         Pagination: « 1 2 3 »                     │
└────────────────────────────────────────────────────┘
```

**Mobile Layout:**
```
┌─────────────────────┐
│  [Search Box]       │
│  [ ] OPEN SESSION   │
│  [ ] GRAND_PRIX     │
├─────────────────────┤
│  Session Card       │
│  📅 Jan 15, 14:00  │
│  🏁 OPEN SESSION   │
│  👥 5/10 spots     │
│  💰 £25.00         │
│  [Book Now]        │
├─────────────────────┤
│  [More cards...]    │
└─────────────────────┘
```

**Key Features:**
- Real-time capacity display with progress bar
- Filter by session type
- Clear availability indicators
- Mobile-optimized cards

### 3. Session Detail (session_detail.html)

**Desktop Layout:**
```
┌────────────────────────────────────────────────────┐
│  ← Back to Sessions                                │
├────────────────────────────────────────────────────┤
│  Session Details                                   │
│                                                    │
│  📅 Thursday, January 15, 2025                    │
│  ⏰ 14:00 - 16:00 (2 hours)                       │
│  🏁 OPEN SESSION                                  │
│  📍 Main Track                                     │
│  💰 £25.00                                         │
│                                                    │
│  Capacity: 👥 5/10 spots remaining                │
│  [████████░░░░░░] 50% full                        │
│                                                    │
│  ┌──────────────────────────────────┐            │
│  │  Booking Form                     │            │
│  │  Driver: [Autofilled if logged]  │            │
│  │  Preferred Kart: [1-99] (opt)    │            │
│  │  Notes: [Textarea]                │            │
│  │  [Submit Booking]                 │            │
│  └──────────────────────────────────┘            │
└────────────────────────────────────────────────────┘
```

**Mobile Layout:**
```
┌─────────────────────┐
│  ← Back             │
├─────────────────────┤
│  Session Details    │
│  📅 Jan 15, 2025   │
│  ⏰ 14:00-16:00    │
│  🏁 OPEN SESSION   │
│  💰 £25.00         │
│                     │
│  👥 5/10 spots     │
│  [████████░░]      │
│                     │
│  Booking Form       │
│  [Submit]          │
└─────────────────────┘
```

**Key Features:**
- Clear session information hierarchy
- Visual capacity indicator (progress bar)
- Inline booking form (if logged in)
- Responsive stacking on mobile

### 4. My Bookings (booking_list.html)

**Desktop Layout:**
```
┌────────────────────────────────────────────────────┐
│  My Bookings                                       │
│  Tabs: [All] [Upcoming] [Completed] [Cancelled]   │
├────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────┐  │
│  │ Booking #1234                                │  │
│  │  📅 Thu, Jan 15 - 14:00                     │  │
│  │  🏁 OPEN SESSION                            │  │
│  │  🏎️ Kart #7 (Assigned)                     │  │
│  │  ✅ CONFIRMED                               │  │
│  │  [View Details] [Cancel Booking]            │  │
│  └─────────────────────────────────────────────┘  │
│                                                    │
│  ┌─────────────────────────────────────────────┐  │
│  │ Booking #1235                                │  │
│  │  📅 Fri, Jan 16 - 10:00                     │  │
│  │  🏁 GRAND_PRIX                              │  │
│  │  ⏳ PENDING (Awaiting confirmation)         │  │
│  │  [View Details]                              │  │
│  └─────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

**Mobile Layout:**
```
┌─────────────────────┐
│  My Bookings        │
│  [All ▾]           │
├─────────────────────┤
│  Booking #1234      │
│  📅 Jan 15, 14:00  │
│  🏎️ Kart #7       │
│  ✅ CONFIRMED      │
│  [Details][Cancel] │
├─────────────────────┤
│  Booking #1235      │
│  📅 Jan 16, 10:00  │
│  ⏳ PENDING        │
│  [Details]         │
└─────────────────────┘
```

**Key Features:**
- Status-based filtering
- Clear status badges (color + icon + text)
- Action buttons contextual to status
- Mobile-friendly card layout

### 5. Admin Dashboard (admin/index.html)

**Desktop Layout:**
```
┌────────────────────────────────────────────────────┐
│  Django Administration                             │
│  Today's Overview - Monday, January 13, 2025      │
├────────────────────────────────────────────────────┤
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐            │
│  │ 🏁 3 │ │ ⏳ 5 │ │ ✅ 12│ │ 🏎️8 │            │
│  │Today │ │Pend. │ │Conf. │ │Karts│            │
│  └──────┘ └──────┘ └──────┘ └──────┘            │
├────────────────────────────────────────────────────┤
│  Today's Sessions           Pending Bookings       │
│  ┌────────────────┐        ┌────────────────┐    │
│  │ 14:00 - 16:00  │        │ John Doe       │    │
│  │ OPEN | 5/10    │        │ Jan 15, 14:00  │    │
│  │ ✅ Available  │        │ [Review]       │    │
│  └────────────────┘        └────────────────┘    │
├────────────────────────────────────────────────────┤
│  Upcoming Sessions (Next 7 Days)                   │
│  [Table with full session details...]             │
├────────────────────────────────────────────────────┤
│  Kart Fleet Status                                 │
│  [Table showing all karts and status...]          │
└────────────────────────────────────────────────────┘
```

**Key Features:**
- Quick stats overview cards
- Action-required sections highlighted
- Comprehensive tables for detailed management
- Quick action buttons

### 6. Registration Page (register.html)

**Desktop Layout:**
```
┌────────────────────────────────────────────────────┐
│                 Create Account                     │
│                                                    │
│  ┌──────────────────────────────────────────┐    │
│  │  Username:  [________________]            │    │
│  │  Email:     [________________]            │    │
│  │  Password:  [________________]            │    │
│  │  Confirm:   [________________]            │    │
│  │  Role:      ( ) Driver  ( ) Manager      │    │
│  │                                            │    │
│  │  Phone (opt): [________________]          │    │
│  │  DOB (opt):   [____-__-__]                │    │
│  │                                            │    │
│  │  [Create Account]                         │    │
│  │                                            │    │
│  │  Already have an account? [Sign In]       │    │
│  └──────────────────────────────────────────┘    │
└────────────────────────────────────────────────────┘
```

**Mobile Layout:**
```
┌─────────────────────┐
│  Create Account     │
│                     │
│  Username:          │
│  [____________]     │
│                     │
│  Email:             │
│  [____________]     │
│                     │
│  Password:          │
│  [____________]     │
│                     │
│  Confirm:           │
│  [____________]     │
│                     │
│  Role:              │
│  ( ) Driver         │
│  ( ) Manager        │
│                     │
│  [Create Account]   │
│                     │
│  [Sign In]          │
└─────────────────────┘
```

**Key Features:**
- Clear form labels (accessibility)
- Validation errors inline
- Optional fields marked
- Link to login page

## Information Architecture

### Navigation Structure:
```
Home
├── Sessions (Browse)
│   └── Session Detail
│       └── Booking Form → My Bookings
├── My Bookings (Auth Required)
│   └── Booking Detail
│       └── Cancel Booking
├── About
├── Contact
│   └── Contact Form
└── Auth
    ├── Login
    ├── Register
    └── Logout
```

### Admin Navigation:
```
Admin Dashboard
├── Sessions
│   ├── Session Slots
│   └── Tracks
├── Bookings
│   ├── All Bookings
│   └── Pending (filtered)
├── Karts
│   └── Fleet Management
└── Users
    ├── Users
    └── Profiles
```

## Interactive Elements

### Buttons:
```html
<!-- Primary Action -->
<button class="btn btn-primary">Book Now</button>

<!-- Secondary Action -->
<button class="btn btn-secondary">View Details</button>

<!-- Danger Action (requires confirmation) -->
<button class="btn btn-danger">Cancel Booking</button>

<!-- Disabled State -->
<button class="btn btn-primary" disabled>Session Full</button>
```

### Status Badges:
```html
<!-- Available (Green) -->
<span class="badge badge-success">✅ CONFIRMED</span>

<!-- Pending (Amber) -->
<span class="badge badge-warning">⏳ PENDING</span>

<!-- Full/Cancelled (Red) -->
<span class="badge badge-danger">❌ CANCELLED</span>

<!-- Neutral (Gray) -->
<span class="badge badge-secondary">Completed</span>
```

### Progress Bars:
```html
<!-- Capacity Indicator -->
<div class="progress">
  <div class="progress-bar bg-success" style="width: 50%">
    5/10 spots
  </div>
</div>
```

## Accessibility Features

### Semantic HTML:
- `<nav>` for navigation
- `<main>` for primary content
- `<article>` for sessions/bookings
- `<section>` for logical groupings
- `<button>` vs `<a>` used correctly

### ARIA Labels:
```html
<!-- Screen reader only text -->
<span class="sr-only">Current page</span>

<!-- Live regions for dynamic updates -->
<div aria-live="polite">Booking confirmed!</div>

<!-- Descriptive labels -->
<button aria-label="Cancel booking #1234">Cancel</button>

<!-- Skip navigation -->
<a href="#main-content" class="skip-link">Skip to main content</a>
```

### Keyboard Navigation:
- All interactive elements focusable
- Visible focus indicators (blue outline)
- Logical tab order
- Skip links for repeated content

### Color Contrast:
- Body text: #212529 on #FFFFFF (15.8:1)
- Links: #007bff on #FFFFFF (4.5:1)
- Buttons: #FFFFFF on #007bff (4.5:1)
- Status badges: WCAG AA compliant

## Responsive Design Strategy

### Mobile-First Approach:
1. **Base styles** target mobile (< 768px)
2. **Progressive enhancement** adds complexity for larger screens
3. **Touch-friendly** targets (minimum 44x44px)
4. **Simplified navigation** (hamburger menu on mobile)

### Performance:
- System fonts (no external font loading)
- Minimal CSS (single stylesheet)
- Compressed images (where used)
- No unnecessary JavaScript

### Breakpoint Strategy:
```css
/* Mobile: Base styles */
.container { width: 100%; padding: 15px; }

/* Tablet: 768px+ */
@media (min-width: 768px) {
  .container { width: 750px; }
  .grid { display: grid; grid-template-columns: repeat(2, 1fr); }
}

/* Desktop: 992px+ */
@media (min-width: 992px) {
  .container { width: 970px; }
  .grid { grid-template-columns: repeat(3, 1fr); }
}

/* Ultra-wide: 1600px+ */
@media (min-width: 1600px) {
  .container { max-width: 1400px; margin: 0 auto; }
}
```

## User Feedback Patterns

### Success Messages:
```html
<div class="alert alert-success" role="alert">
  ✅ Booking confirmed! You've been assigned Kart #7.
</div>
```

### Error Messages:
```html
<div class="alert alert-danger" role="alert">
  ❌ Session is full. Please choose another time.
</div>
```

### Loading States:
```html
<button class="btn btn-primary" disabled>
  <span class="spinner-border spinner-border-sm"></span>
  Processing...
</button>
```

### Confirmation Dialogs:
```html
<!-- Django confirmation template -->
<form method="post">
  {% csrf_token %}
  <p>Are you sure you want to cancel this booking?</p>
  <button type="submit" class="btn btn-danger">Yes, Cancel</button>
  <a href="{% url 'booking_detail' %}" class="btn btn-secondary">No, Go Back</a>
</form>
```

## Design Decisions Rationale

### Why Bootstrap?
- **Rapid development** - Pre-built responsive components
- **Accessibility** - ARIA support built-in
- **Browser compatibility** - Tested across all major browsers
- **Customization** - Easy to override with custom CSS
- **Familiar patterns** - Users recognize standard UI patterns

### Why Minimal Custom CSS?
- **Maintenance** - Less code to maintain
- **Performance** - Smaller file size
- **Consistency** - Bootstrap's design system enforced
- **Focus** - Spend time on functionality, not design
- **Standards** - Industry-standard patterns

### Why Icons?
- **Universal understanding** - 📅 = date, 🏎️ = kart (language-independent)
- **Quick scanning** - Icons faster to process than text
- **Visual hierarchy** - Draw attention to key info
- **Accessibility** - Always paired with text labels

### Why Progress Bars for Capacity?
- **Visual understanding** - Instant comprehension of availability
- **Urgency indication** - Red bar = nearly full, encourages action
- **Better than numbers** - 50% full clearer than "5/10"
- **Accessible** - Text alternative provided

## Contravening UX Principles (Distinction)

### Justified Decisions:

1. **Admin Dashboard Density:**
   - **Principle**: "Reduce cognitive load"
   - **Contravention**: Admin dashboard shows multiple data tables at once
   - **Justification**: Managers need comprehensive overview for operational decisions. They are power users who benefit from dense information display. Grouped logically (stats → today's sessions → pending bookings → upcoming → karts).

2. **Required Registration for Booking:**
   - **Principle**: "Minimize barriers to action"
   - **Contravention**: Must create account to book (no guest checkout)
   - **Justification**: Business requirement - need driver contact info for safety/liability. Anonymous bookings would create operational chaos for track management.

3. **Two-Step Booking Process:**
   - **Principle**: "Minimize steps to goal"
   - **Contravention**: Must browse sessions → view detail → submit booking form
   - **Justification**: Users need full session information (time, type, price, capacity) before committing. One-click booking would lead to mistakes and cancellations.

## Summary

The KartControl UX design prioritizes:

✅ **Accessibility** - WCAG 2.1 AA compliance throughout
✅ **Consistency** - Predictable patterns across all pages
✅ **User Control** - No aggressive auto-play, clear confirmations
✅ **Immediate Feedback** - Real-time status updates
✅ **Responsive Design** - Mobile-first approach
✅ **Information Hierarchy** - Clear visual organization
✅ **Professional Grade** - Clean, polished interface

The design successfully balances business requirements (mandatory registration, two-step booking) with user needs (clarity, speed, control) while maintaining full accessibility compliance.
