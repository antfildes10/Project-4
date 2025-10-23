# KartControl - Comprehensive Testing Plan

## Backend Deployment Status
✅ **CONFIRMED LIVE**
- Platform: Heroku
- Database: PostgreSQL (Essential-0 tier)
- URL: https://project-4-karting-121d969fb7d5.herokuapp.com
- All migrations applied successfully
- Superuser created

---

## Testing Requirements (Code Institute LO4)

Target: **≥80% test coverage** for automated tests
All critical user journeys must be tested manually

---

## 1. AUTOMATED TESTS TO CREATE

### 1.1 Model Tests (`tests/test_models.py`)

#### Booking Model
- [ ] `test_booking_creation` - Create booking successfully
- [ ] `test_booking_capacity_validation` - Prevent overbooking (11th of 10)
- [ ] `test_booking_driver_overlap` - Prevent driver double-booking same time
- [ ] `test_booking_status_transitions` - PENDING → CONFIRMED → COMPLETED
- [ ] `test_booking_kart_assignment` - Random kart assignment on confirmation
- [ ] `test_booking_chosen_kart_validation` - Validate chosen kart availability
- [ ] `test_booking_cancellation_logic` - can_be_cancelled() method

#### SessionSlot Model
- [ ] `test_session_creation` - Create session with valid data
- [ ] `test_session_time_validation` - start_datetime < end_datetime
- [ ] `test_session_capacity_positive` - Capacity must be > 0
- [ ] `test_session_get_available_spots` - Calculate available capacity
- [ ] `test_session_is_full` - Check if session at capacity
- [ ] `test_session_is_past` - Check if session in the past

#### Kart Model
- [ ] `test_kart_creation` - Create kart with unique number
- [ ] `test_kart_number_unique` - Duplicate numbers rejected
- [ ] `test_kart_status_choices` - ACTIVE vs MAINTENANCE
- [ ] `test_maintenance_kart_blocked` - MAINTENANCE karts not assignable

#### Profile Model
- [ ] `test_profile_creation_on_signup` - Profile auto-created with User
- [ ] `test_profile_role_defaults` - Default role is DRIVER
- [ ] `test_profile_is_manager` - Manager role check

### 1.2 View Tests (`tests/test_views.py`)

#### Authentication Views
- [ ] `test_registration_success` - New user signup works
- [ ] `test_login_valid_credentials` - Login with correct password
- [ ] `test_login_invalid_credentials` - Login fails with wrong password
- [ ] `test_logout` - Logout clears session
- [ ] `test_profile_view_authenticated` - Profile page loads for logged-in user
- [ ] `test_profile_view_unauthenticated` - Redirect to login

#### Session Views
- [ ] `test_session_list_public` - Anonymous users can view sessions
- [ ] `test_session_detail_public` - Session detail accessible to all
- [ ] `test_session_list_filter_by_type` - Filter Grand Prix vs Open Session
- [ ] `test_session_list_filter_by_date` - Filter by specific date

#### Booking Views
- [ ] `test_booking_create_authenticated` - Logged-in user can book
- [ ] `test_booking_create_unauthenticated` - Redirect to login
- [ ] `test_booking_create_full_session` - Error when session full
- [ ] `test_booking_create_past_session` - Cannot book past sessions
- [ ] `test_booking_list_own_only` - Drivers see only their bookings
- [ ] `test_booking_detail_permission` - Cannot view others' bookings
- [ ] `test_booking_cancel_own` - Driver can cancel own booking
- [ ] `test_booking_cancel_others` - Cannot cancel others' bookings
- [ ] `test_booking_confirm_manager_only` - Only managers can confirm
- [ ] `test_booking_complete_manager_only` - Only managers can complete

#### Manager Views
- [ ] `test_admin_dashboard_manager_only` - Manager access required
- [ ] `test_admin_dashboard_driver_denied` - Driver gets 403/redirect

### 1.3 Form Tests (`tests/test_forms.py`)

- [ ] `test_booking_form_valid` - Valid form submission
- [ ] `test_booking_form_empty` - Empty form shows errors
- [ ] `test_contact_form_validation` - Contact form validates email
- [ ] `test_contact_form_required_fields` - All required fields validated

### 1.4 URL Tests (`tests/test_urls.py`)

- [ ] `test_all_urls_resolve` - All named URLs resolve correctly
- [ ] `test_homepage_url` - Homepage URL works
- [ ] `test_booking_urls` - All booking URLs resolve
- [ ] `test_session_urls` - All session URLs resolve

---

## 2. MANUAL TESTING CHECKLIST

### 2.1 Authentication & Authorization

| Test Case | Steps | Expected Result | Status |
|-----------|-------|----------------|--------|
| User Registration | 1. Click Register<br>2. Fill form<br>3. Submit | Account created, redirect to login | ⬜ |
| User Login | 1. Click Login<br>2. Enter credentials<br>3. Submit | Redirect to homepage, navbar shows username | ⬜ |
| User Logout | 1. Click Logout in dropdown<br>2. Confirm | Session cleared, navbar shows Login/Register | ⬜ |
| Role Badge Display | 1. Login as Driver<br>2. Login as Manager | Correct role badge shown in navbar | ⬜ |
| Manager-only Access | 1. Login as Driver<br>2. Try to access /admin/ | Redirect or 403 error | ⬜ |

### 2.2 Session Browsing (Public)

| Test Case | Steps | Expected Result | Status |
|-----------|-------|----------------|--------|
| View Sessions List | 1. Navigate to /sessions/ | All upcoming sessions displayed | ⬜ |
| Filter by Type | 1. Select "Grand Prix"<br>2. Apply filter | Only Grand Prix sessions shown | ⬜ |
| Filter by Date | 1. Select date<br>2. Apply filter | Only sessions on that date shown | ⬜ |
| View Session Detail | 1. Click "View Details" | Session details, capacity, price shown | ⬜ |
| Guest Cannot Book | 1. Logout<br>2. View session<br>3. Try to book | "Please login" message shown | ⬜ |

### 2.3 Booking Flow (Driver)

| Test Case | Steps | Expected Result | Status |
|-----------|-------|----------------|--------|
| Create Booking | 1. Login as Driver<br>2. Click "Book Now"<br>3. Submit form | Booking created with PENDING status | ⬜ |
| Prevent Overbooking | 1. Fill session to capacity<br>2. Try to book 11th slot | Error: "Session is fully booked" | ⬜ |
| Prevent Double Booking | 1. Book session A<br>2. Try to book overlapping session B | Error: "You already have a booking during this time" | ⬜ |
| View My Bookings | 1. Navigate to My Bookings | All user's bookings displayed | ⬜ |
| Filter Upcoming | 1. Click "Upcoming" tab | Only future PENDING/CONFIRMED shown | ⬜ |
| Filter by Status | 1. Click "Confirmed" tab | Only CONFIRMED bookings shown | ⬜ |
| Cancel Own Booking | 1. Open booking detail<br>2. Click Cancel | Status changes to CANCELLED, capacity freed | ⬜ |
| Cannot Cancel Past | 1. Try to cancel past booking | Error or button disabled | ⬜ |

### 2.4 Booking Management (Manager)

| Test Case | Steps | Expected Result | Status |
|-----------|-------|----------------|--------|
| View All Bookings | 1. Login as Manager<br>2. Access admin panel | All bookings visible | ⬜ |
| Confirm Booking | 1. Open PENDING booking<br>2. Click Confirm | Status → CONFIRMED, kart assigned, email sent | ⬜ |
| Random Kart Assignment | 1. Confirm booking without chosen kart | Random ACTIVE kart assigned | ⬜ |
| No Available Karts | 1. Set all karts to MAINTENANCE<br>2. Try to confirm | Error: "No available karts" | ⬜ |
| Complete Booking | 1. After session ends<br>2. Click Complete | Status → COMPLETED | ⬜ |
| Cannot Complete Future | 1. Try to complete future booking | Error: "Session hasn't ended yet" | ⬜ |

### 2.5 Session Management (Manager)

| Test Case | Steps | Expected Result | Status |
|-----------|-------|----------------|--------|
| Create Session | 1. Admin → Sessions → Add<br>2. Fill form<br>3. Save | New session appears in list | ⬜ |
| Edit Session | 1. Click Edit<br>2. Change time<br>3. Save | Changes reflected immediately | ⬜ |
| Delete Session | 1. Click Delete<br>2. Confirm | Session removed from list | ⬜ |
| Prevent Invalid Times | 1. Set end_time before start_time<br>2. Try to save | Validation error shown | ⬜ |

### 2.6 Kart Management (Manager)

| Test Case | Steps | Expected Result | Status |
|-----------|-------|----------------|--------|
| Add Kart | 1. Admin → Karts → Add<br>2. Enter number<br>3. Save | New kart in list | ⬜ |
| Edit Kart Status | 1. Change ACTIVE → MAINTENANCE<br>2. Save | Kart not assignable to bookings | ⬜ |
| Unique Kart Numbers | 1. Try to create duplicate number<br>2. Save | Error: "Kart number must be unique" | ⬜ |

### 2.7 UI/UX Testing

| Test Case | Expected Result | Status |
|-----------|----------------|--------|
| Responsive Mobile (375px) | No horizontal scroll, navbar collapses | ⬜ |
| Responsive Tablet (768px) | Layout adapts, cards stack properly | ⬜ |
| Responsive Desktop (1440px) | Full layout, all elements visible | ⬜ |
| Logged-in User Welcome | Blue hero section with "Welcome back, [username]!" | ⬜ |
| Logged-out User CTA | "Register Now" and "Login" buttons visible | ⬜ |
| Booking Statistics | Homepage shows booking count for logged-in users | ⬜ |
| Booked Sessions Badge | Sessions user booked show blue "Booked" badge | ⬜ |
| Status Banners | Green banner for logged-in, yellow for logged-out | ⬜ |

### 2.8 Accessibility Testing

| Test Case | Tool | Expected Result | Status |
|-----------|------|----------------|--------|
| Contrast Ratio | Chrome DevTools | All text ≥ 4.5:1 ratio | ⬜ |
| Keyboard Navigation | Tab key | All interactive elements accessible | ⬜ |
| Screen Reader | VoiceOver/NVDA | All content announced correctly | ⬜ |
| Focus Indicators | Visual inspection | Visible red outline on focus | ⬜ |
| ARIA Labels | HTML validation | All icons have aria-hidden or aria-label | ⬜ |
| Form Labels | HTML validation | All inputs have associated labels | ⬜ |

---

## 3. VALIDATION TESTING

### 3.1 Code Validation

| Validator | Files | Command | Status |
|-----------|-------|---------|--------|
| **Python (flake8)** | All .py files | `flake8 --exclude=venv,migrations` | ⬜ |
| **Python (black)** | All .py files | `black . --check` | ⬜ |
| **HTML** | All templates | W3C Validator | ⬜ |
| **CSS** | style.css | Jigsaw Validator | ⬜ |
| **JavaScript** | main.js | ESLint / Prettier | ⬜ |

### 3.2 Django System Checks

| Check | Command | Expected Result | Status |
|-------|---------|----------------|--------|
| Development | `python manage.py check` | 0 issues | ⬜ |
| Production | `heroku run "python manage.py check --deploy" -a project-4-karting` | 0 issues | ⬜ |

---

## 4. DEPLOYMENT VERIFICATION

### 4.1 Heroku Deployment Checklist

| Item | Verification | Status |
|------|--------------|--------|
| PostgreSQL Connected | Check DATABASE_URL exists | ✅ |
| All Migrations Applied | `heroku run "python manage.py showmigrations"` | ✅ |
| Static Files Served | CSS/JS loading on live site | ⬜ |
| DEBUG = False | Check config vars | ✅ |
| SECRET_KEY Secured | Not in git, env var set | ✅ |
| HTTPS Enforced | Check SECURE_SSL_REDIRECT | ✅ |
| Admin Panel Secure | /admin/ requires authentication | ⬜ |
| Error Pages Work | Test 404, 500 pages | ⬜ |

### 4.2 Dev/Prod Parity Check

| Feature | Dev (localhost) | Prod (Heroku) | Status |
|---------|----------------|---------------|--------|
| Homepage loads | ⬜ | ⬜ | ⬜ |
| User registration | ⬜ | ⬜ | ⬜ |
| User login | ⬜ | ⬜ | ⬜ |
| Session browsing | ⬜ | ⬜ | ⬜ |
| Create booking | ⬜ | ⬜ | ⬜ |
| Manager confirm booking | ⬜ | ⬜ | ⬜ |
| Static files load | ⬜ | ⬜ | ⬜ |

---

## 5. PERFORMANCE TESTING

| Metric | Tool | Target | Status |
|--------|------|--------|--------|
| Page Load Time | Lighthouse | < 3s | ⬜ |
| Performance Score | Lighthouse | > 90 | ⬜ |
| Accessibility Score | Lighthouse | > 95 | ⬜ |
| Best Practices Score | Lighthouse | > 90 | ⬜ |
| SEO Score | Lighthouse | > 90 | ⬜ |

---

## 6. SECURITY TESTING

| Test | Verification | Status |
|------|--------------|--------|
| CSRF Protection | Try to submit form without token | ⬜ |
| SQL Injection | Try malicious input in forms | ⬜ |
| XSS Prevention | Try script tags in text fields | ⬜ |
| Password Hashing | Check db - passwords not plain text | ⬜ |
| Session Security | Logout invalidates session | ⬜ |
| Permission Enforcement | Driver cannot access manager routes | ⬜ |

---

## 7. BROWSER COMPATIBILITY

| Browser | Version | Homepage | Sessions | Booking | Admin | Status |
|---------|---------|----------|----------|---------|-------|--------|
| Chrome | Latest | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Firefox | Latest | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Safari | Latest | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Edge | Latest | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

---

## 8. BUG TRACKING

| Bug ID | Description | Severity | Found | Fixed | Commit | Retested |
|--------|-------------|----------|-------|-------|--------|----------|
| 001 | Booking form validation - RelatedObjectDoesNotExist | High | ✅ | ✅ | b88e5c8 | ⬜ |
| 002 | Static files not loading on Heroku | High | ✅ | ✅ | b88e5c8 | ⬜ |
| 003 | Booking list filters not working | Medium | ✅ | ✅ | 70a6fc8 | ⬜ |

---

## 9. EXECUTION PLAN

### Week 1: Automated Tests
1. Create test files structure
2. Write model tests (aim for 80% coverage)
3. Write view tests
4. Write form tests
5. Run coverage report: `coverage run --source='.' manage.py test && coverage report`

### Week 2: Manual Testing
1. Execute all authentication tests
2. Execute all booking flow tests
3. Execute all manager function tests
4. Document results in TESTING.md

### Week 3: Validation & Deployment
1. Run all validators (HTML, CSS, JS, Python)
2. Fix any validation errors
3. Run Lighthouse audits
4. Verify dev/prod parity
5. Document all results

### Week 4: Final Review
1. Retest all previously found bugs
2. Browser compatibility testing
3. Accessibility audit
4. Performance optimization if needed
5. Final deployment verification

---

## 10. COMMANDS REFERENCE

### Run All Tests
```bash
python manage.py test
```

### Run Specific Test File
```bash
python manage.py test bookings.tests.test_models
```

### Coverage Report
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Linting
```bash
flake8 --exclude=venv,migrations
black . --check
```

### Django Checks
```bash
python manage.py check
python manage.py check --deploy
```

---

## SUCCESS CRITERIA

✅ **PASS** = All of the following met:
- [ ] ≥80% automated test coverage
- [ ] All manual test cases passed
- [ ] 0 critical bugs remaining
- [ ] All validators passing (HTML, CSS, JS, Python)
- [ ] Lighthouse scores >90 (Performance, Accessibility, Best Practices)
- [ ] Dev/Prod parity confirmed
- [ ] All 7 Learning Outcomes demonstrated
- [ ] TESTING.md fully documented

---

**Testing Plan Created**: 2025-10-23
**Project**: KartControl - Portfolio Project 4
**Assessor**: Code Institute
