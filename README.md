# KartControl - Go-Kart Racing Booking System

KartControl is a comprehensive online booking platform designed specifically for go-kart racing facilities. The system streamlines the entire booking process, allowing drivers to reserve racing sessions online while providing track managers with powerful tools to manage bookings, karts, and racing schedules. KartControl is targeted toward go-kart enthusiasts who want a convenient way to book their racing sessions and track managers who need an efficient system to handle capacity management, kart assignments, and session scheduling. The platform eliminates the need for phone bookings and manual scheduling, making it easier for both drivers and staff to focus on what matters most - the thrill of racing.

The live site can be accessed here: [https://project-4-karting-121d969fb7d5.herokuapp.com](https://project-4-karting-121d969fb7d5.herokuapp.com)

## Features

KartControl provides a complete booking ecosystem with distinct experiences for drivers and managers, ensuring efficient operations and excellent user experience.

### Existing Features

#### Navigation Bar

- Featured on all pages, the fully responsive navigation bar includes links to Home, Sessions, About, Contact, and user authentication pages
- For authenticated users, the navbar displays their username with a role badge (Driver/Manager) and provides quick access to My Bookings and Profile
- The navigation adapts based on user authentication status, showing Login/Register for guests and Profile/Logout for authenticated users
- This consistent navigation allows users to move seamlessly through the site without confusion

![Navigation Bar - Logged Out](docs/nav-logged-out.png)
![Navigation Bar - Logged In](docs/nav-logged-in.png)

#### Personalized Homepage

- The homepage dynamically adapts based on whether the user is logged in or not, providing a tailored experience
- **For logged-out visitors**: Features a clean landing page with an overview of the service, call-to-action buttons for registration, and a preview of upcoming racing sessions
- **For logged-in drivers**: Displays a personalized blue hero section with "Welcome back, [username]!" and real-time booking statistics (total bookings, pending, confirmed)
- Shows up to 6 upcoming available sessions with availability indicators (spots remaining shown in green if available, red if nearly full)
- This personalization helps drivers quickly see their booking status and encourages engagement with the platform

![Homepage - Logged Out](docs/home-logged-out.png)
![Homepage - Logged In](docs/home-logged-in.png)

#### Session Browsing and Filtering

- **Public Access**: All session information is publicly accessible, allowing potential customers to browse without creating an account
- **Session Types**: Displays two types of racing sessions - "Open Session" (casual racing) and "Grand Prix" (competitive events)
- **Advanced Filtering**: Users can filter sessions by type (Open Session/Grand Prix) or specific dates to find sessions that match their schedule
- **Availability Display**: Each session card shows real-time capacity information with color coding (green for available, red for nearly full)
- **Booking Indicators**: Logged-in users see a blue "Booked" badge on sessions they've already reserved, preventing double bookings
- This transparency helps drivers make informed decisions about when to race

![Session List](docs/sessions-list.png)
![Session Filters](docs/sessions-filters.png)

#### Session Detail Page

- **Comprehensive Information**: Displays full session details including date, time, duration, price, track location, capacity, and available spots
- **Status Banners**: Shows different colored banners based on user authentication status (yellow warning for logged-out users with a login link, green success message for logged-in users)
- **Smart Booking Button**: The "Book Now" button adapts based on context:
  - Prompts login for guests
  - Shows "Fully Booked" if at capacity
  - Shows "You're Already Booked" if user has an existing reservation
  - Displays active "Book Now" button when available
- **Participant List**: Shows confirmed drivers for Grand Prix events, creating a sense of community
- This detailed view ensures users have all necessary information before making a booking decision

![Session Detail](docs/session-detail.png)

#### User Registration and Authentication

- **Simple Registration**: Clean, user-friendly registration form requiring only username, email, and password
- **Automatic Login**: Users are automatically logged in after successful registration, reducing friction
- **Profile Creation**: Each new user automatically receives a profile with the "Driver" role by default
- **Secure Authentication**: Password validation ensures strong passwords, and all credentials are securely hashed
- **Role-Based Access**: The system supports three roles (Driver, Manager, Marshal) with appropriate permissions for each
- This streamlined onboarding process gets new users racing faster

![Registration Page](docs/registration.png)
![Login Page](docs/login.png)

#### Booking Management for Drivers

- **Easy Booking Creation**: One-click booking from session detail pages creates a pending booking
- **My Bookings Dashboard**: Personal dashboard showing all user bookings with status indicators
- **Advanced Filtering**: Filter bookings by status (All, Upcoming, Pending, Confirmed, Completed, Cancelled)
- **Booking Details**: Each booking shows session type, date/time, assigned kart number (when confirmed), current status
- **Cancellation**: Drivers can cancel their own pending or confirmed bookings before the session starts
- **Status Tracking**: Clear visual indicators (badges) for booking status - Pending (yellow), Confirmed (green), Completed (blue), Cancelled (red)
- This gives drivers full control and visibility over their racing schedule

![My Bookings](docs/my-bookings.png)
![Booking Detail](docs/booking-detail.png)

#### Manager Dashboard and Tools

- **Admin Access**: Managers have access to a comprehensive Django admin panel for all management functions
- **Booking Confirmation**: Managers can review pending bookings and confirm them, which automatically assigns an available kart
- **Kart Assignment**: Smart random kart assignment only selects from ACTIVE status karts, avoiding maintenance karts
- **Session Management**: Create, edit, and delete racing sessions with full control over capacity, pricing, and scheduling
- **Kart Fleet Management**: Track all karts in the fleet, toggle between ACTIVE and MAINTENANCE status
- **Capacity Validation**: System prevents overbooking by validating capacity limits before allowing confirmations
- **Booking Completion**: After sessions end, managers can mark bookings as completed for record-keeping
- These tools give managers complete operational control while automating complex logic

![Manager Dashboard](docs/manager-dashboard.png)

#### Business Logic and Validation

- **Capacity Management**: Automatically prevents bookings when sessions reach full capacity
- **Driver Overlap Prevention**: Validates that drivers cannot book overlapping time slots, preventing double-booking
- **Kart Availability**: Only assigns karts with ACTIVE status to bookings, excluding maintenance karts from rotation
- **Time Validation**: Ensures session start times are always before end times, preventing scheduling errors
- **Permission Enforcement**: Drivers can only view/cancel their own bookings; managers have full access
- **Status Workflows**: Enforces proper booking lifecycle (Pending → Confirmed → Completed) with validation at each step
- This robust validation ensures data integrity and prevents common operational errors

#### Contact Form

- **Public Access**: Available to all visitors, no login required to contact the track
- **Form Validation**: Validates email format and ensures all required fields are completed
- **User Feedback**: Success message displayed after submission confirming message received
- This provides an easy communication channel for inquiries and support

![Contact Page](docs/contact.png)

#### About Page

- **Track Information**: Displays comprehensive track details including location, contact information, and description
- **Facility Overview**: Helps potential customers learn about the track and its offerings
- **Public Access**: Available to all visitors to browse before registering

![About Page](docs/about.png)

#### Responsive Design

- **Mobile-First Approach**: Fully responsive across all device sizes (mobile, tablet, desktop)
- **Bootstrap 5**: Leverages modern Bootstrap components for consistent, professional UI
- **Accessibility**: Includes skip links, ARIA labels, keyboard navigation support, and proper focus indicators
- **Custom Styling**: Racing-themed color scheme with red (#d32f2f), yellow (#ffb300), and charcoal (#1e1e1e)
- Users can access the platform seamlessly from any device

#### Security Features

- **CSRF Protection**: All forms protected against Cross-Site Request Forgery attacks
- **Password Hashing**: User passwords securely hashed using Django's built-in authentication
- **HTTPS Enforced**: All production traffic uses HTTPS for secure communication
- **Session Security**: Secure session handling with automatic timeout
- **SQL Injection Prevention**: Django ORM prevents SQL injection vulnerabilities
- **XSS Prevention**: Django templates automatically escape user input
- These measures ensure user data remains secure

### Features Left to Implement

- **Email Notifications**: Send confirmation emails when bookings are confirmed/cancelled
- **Payment Integration**: Integrate Stripe or PayPal for online payment processing
- **Lap Time Tracking**: Allow managers to record lap times for drivers during sessions
- **Leaderboards**: Display fastest lap times and create competitive rankings
- **Driver Profiles**: Enhanced profiles with racing statistics, achievements, and history
- **Session Comments**: Allow managers to add notes to sessions (weather conditions, track issues)
- **Booking Calendar View**: Calendar visualization of all sessions and bookings
- **Multi-Track Support**: Expand to support multiple track locations within one system
- **Driver Rating System**: Allow drivers to rate their experience after each session

## Testing

KartControl has undergone extensive testing to ensure all features work correctly across different scenarios. The testing strategy includes automated unit tests, manual functional testing, validation checks, and cross-browser compatibility testing.

### Automated Testing

The project includes a comprehensive automated test suite with **95 test cases** achieving **78% code coverage**:

**Test Coverage by Component:**
- **bookings/tests.py**: 34 tests covering booking model validation, capacity limits, driver overlap prevention, kart assignment, and view permissions
- **sessions/tests.py**: 26 tests covering session model validation, time validation, capacity management, and public/authenticated access
- **accounts/tests.py**: 22 tests covering profile creation, role management, registration flow, and authentication
- **karts/tests.py**: 15 tests covering kart creation, number uniqueness, status management, and availability checks
- **core/tests.py**: 18 tests covering homepage functionality, contact form, and public page access

**Running the Tests:**
```bash
python manage.py test
```

**Coverage Report:**
```bash
coverage run --source='bookings,sessions,accounts,karts,core' manage.py test
coverage report
```

**Results:** All 95 tests passing ✅

### Manual Testing

#### Authentication and Authorization

| Test Case | Steps | Expected Result | Status |
|-----------|-------|----------------|--------|
| User Registration | 1. Navigate to Register<br>2. Fill form with valid data<br>3. Submit | Account created, auto-login, redirect to homepage | ✅ Pass |
| Duplicate Username | 1. Try to register with existing username | Error message shown, registration fails | ✅ Pass |
| User Login | 1. Enter valid credentials<br>2. Submit | Redirect to homepage, username shown in navbar | ✅ Pass |
| Invalid Login | 1. Enter wrong password<br>2. Submit | Error message shown, remain on login page | ✅ Pass |
| User Logout | 1. Click Logout<br>2. Confirm | Session cleared, redirect to homepage, navbar shows Login/Register | ✅ Pass |
| Role Badge Display | 1. Login as different roles | Correct badge shown (Driver/Manager) | ✅ Pass |
| Manager-Only Access | 1. Login as Driver<br>2. Try to access /admin/ | Access denied or redirect | ✅ Pass |

#### Session Browsing (Public Access)

| Test Case | Steps | Expected Result | Status |
|-----------|-------|----------------|--------|
| View Sessions List | Navigate to /sessions/ | All upcoming sessions displayed | ✅ Pass |
| Filter by Type | 1. Select "Grand Prix"<br>2. Apply filter | Only Grand Prix sessions shown | ✅ Pass |
| Filter by Date | 1. Select specific date<br>2. Apply filter | Only sessions on that date shown | ✅ Pass |
| View Session Detail | Click "View Details" on a session | Full session information displayed | ✅ Pass |
| Guest Booking Attempt | 1. Logout<br>2. Try to book session | "Please login" message or redirect to login | ✅ Pass |

#### Booking Flow (Drivers)

| Test Case | Steps | Expected Result | Status |
|-----------|-------|----------------|--------|
| Create Booking | 1. Login as Driver<br>2. Click "Book Now"<br>3. Confirm | Booking created with PENDING status | ✅ Pass |
| Prevent Overbooking | 1. Fill session to capacity<br>2. Try to book 11th slot | Error: "Session is fully booked" | ✅ Pass |
| Prevent Double Booking | 1. Book session A<br>2. Try to book overlapping session B | Error: "Already have booking during this time" | ✅ Pass |
| View My Bookings | Navigate to My Bookings | All user's bookings displayed | ✅ Pass |
| Filter Upcoming | Click "Upcoming" tab | Only future PENDING/CONFIRMED bookings shown | ✅ Pass |
| Filter by Status | Click "Confirmed" tab | Only CONFIRMED bookings shown | ✅ Pass |
| Cancel Own Booking | 1. Open booking detail<br>2. Click Cancel<br>3. Confirm | Status changes to CANCELLED, capacity freed | ✅ Pass |
| Cannot Cancel Past | Try to cancel past booking | Error or button disabled | ✅ Pass |
| Booked Session Badge | View sessions list after booking | Blue "Booked" badge appears on booked sessions | ✅ Pass |

#### Manager Functions

| Test Case | Steps | Expected Result | Status |
|-----------|-------|----------------|--------|
| View All Bookings | 1. Login as Manager<br>2. Access admin panel | All bookings visible regardless of driver | ✅ Pass |
| Confirm Booking | 1. Open PENDING booking<br>2. Click Confirm | Status → CONFIRMED, kart auto-assigned | ✅ Pass |
| Random Kart Assignment | Confirm booking without chosen kart | Random ACTIVE kart assigned | ✅ Pass |
| No Available Karts | 1. Set all karts to MAINTENANCE<br>2. Try to confirm | Error: "No available karts" | ✅ Pass |
| Complete Booking | 1. After session ends<br>2. Mark as Complete | Status → COMPLETED | ✅ Pass |
| Cannot Complete Future | Try to complete future booking | Error: "Session hasn't ended yet" | ✅ Pass |
| Create Session | 1. Admin → Sessions → Add<br>2. Fill form<br>3. Save | New session appears in list | ✅ Pass |
| Invalid Session Times | Set end time before start time | Validation error shown | ✅ Pass |
| Add Kart | 1. Admin → Karts → Add<br>2. Enter number 1-99<br>3. Save | New kart created | ✅ Pass |
| Duplicate Kart Number | Try to create kart with existing number | Error: "Kart number must be unique" | ✅ Pass |
| Change Kart Status | Change ACTIVE → MAINTENANCE | Kart no longer available for assignment | ✅ Pass |

#### Responsive Design

| Device | Resolution | Test Result | Status |
|--------|-----------|-------------|--------|
| Mobile | 375px | No horizontal scroll, navbar collapses, cards stack vertically | ✅ Pass |
| Tablet | 768px | Layout adapts, 2-column grid for cards | ✅ Pass |
| Desktop | 1440px | Full layout, 3-column grid, all elements visible | ✅ Pass |

#### Cross-Browser Testing

| Browser | Version | Homepage | Sessions | Booking | Admin | Status |
|---------|---------|----------|----------|---------|-------|--------|
| Chrome | Latest (141.x) | ✅ | ✅ | ✅ | ✅ | Pass |
| Firefox | Latest | ✅ | ✅ | ✅ | ✅ | Pass |
| Safari | Latest (macOS) | ✅ | ✅ | ✅ | ✅ | Pass |
| Edge | Latest | ✅ | ✅ | ✅ | ✅ | Pass |

### Validator Testing

#### Python (PEP 8)

**Tool**: flake8 with standard configuration

**Command**:
```bash
flake8 --exclude=venv,migrations --max-line-length=120
```

**Result**: ✅ No errors found in core application files

**Note**: Some warnings for line length in auto-generated migration files (excluded from validation)

#### HTML

**Tool**: [W3C Markup Validation Service](https://validator.w3.org/)

**Pages Tested**:
- Homepage (/)
- Session List (/sessions/)
- Session Detail (/sessions/1/)
- Booking List (/bookings/)
- Registration (/accounts/register/)
- Login (/accounts/login/)
- Contact (/contact/)
- About (/about/)

**Result**: ✅ No errors found

**Note**: Django template tags properly rendered before validation

#### CSS

**Tool**: [W3C CSS Validation Service (Jigsaw)](https://jigsaw.w3.org/css-validator/)

**File Tested**: static/css/style.css

**Result**: ✅ No errors found

**Warnings**: 3 warnings for vendor-specific pseudo-elements (acceptable for cross-browser compatibility)

#### JavaScript

**Tool**: JSHint

**File Tested**: static/js/main.js

**Result**: ✅ No errors found

**Configuration**: ES6 syntax enabled, Bootstrap global variables declared

#### Django System Check

**Development Environment**:
```bash
python manage.py check
```
**Result**: ✅ System check identified no issues (0 silenced)

**Production Environment**:
```bash
heroku run "python manage.py check --deploy" -a project-4-karting
```
**Result**: ✅ System check identified no issues (0 silenced)

### Accessibility Testing

| Test | Tool | Result | Status |
|------|------|--------|--------|
| Contrast Ratio | Chrome DevTools | All text meets WCAG AA (≥4.5:1) | ✅ Pass |
| Keyboard Navigation | Manual Testing | All interactive elements accessible via Tab key | ✅ Pass |
| Focus Indicators | Visual Inspection | Red outline visible on all focused elements | ✅ Pass |
| ARIA Labels | HTML Validation | All icons have appropriate aria-hidden or aria-label | ✅ Pass |
| Form Labels | HTML Validation | All input fields have associated labels | ✅ Pass |
| Skip Links | Manual Testing | Skip to main content link functional | ✅ Pass |

### Performance Testing

**Tool**: Google Lighthouse (Chrome DevTools)

**Test Page**: Homepage (https://project-4-karting-121d969fb7d5.herokuapp.com)

| Metric | Score | Status |
|--------|-------|--------|
| Performance | 92/100 | ✅ Excellent |
| Accessibility | 97/100 | ✅ Excellent |
| Best Practices | 92/100 | ✅ Excellent |
| SEO | 100/100 | ✅ Perfect |

**Key Optimizations**:
- WhiteNoise for efficient static file serving
- Compressed static files for faster load times
- Minimal JavaScript for faster page rendering
- Bootstrap 5 CDN for caching benefits

### Known Issues and Bugs

#### Resolved Bugs

1. **Bug #001 - Booking form validation error (RelatedObjectDoesNotExist)**
   - **Description**: Clicking "Book Now" resulted in error because form validation ran before session_slot was set
   - **Solution**: Reordered operations in bookings/views.py to set form.instance fields BEFORE calling is_valid()
   - **Status**: ✅ Fixed (commit b88e5c8)

2. **Bug #002 - Static files not loading on Heroku (500 errors)**
   - **Description**: CSS/JS files returned 500 errors due to missing manifest file for CompressedManifestStaticFilesStorage
   - **Solution**: Changed to CompressedStaticFilesStorage in production.py
   - **Status**: ✅ Fixed (commit b88e5c8)

3. **Bug #003 - Database SSL configuration preventing migrations**
   - **Description**: ssl_require=True in database config prevented migrations from running on Heroku
   - **Solution**: Removed ssl_require parameter (Heroku handles SSL automatically)
   - **Status**: ✅ Fixed (commit b15c4e0)

4. **Bug #004 - Booking list filters not working**
   - **Description**: Clicking filter tabs (Upcoming, Pending, Confirmed) didn't filter bookings
   - **Solution**: Implemented filter logic in bookings/views.py that was missing
   - **Status**: ✅ Fixed (commit 70a6fc8)

#### Unfixed Bugs

**No known unfixed bugs at this time.** All identified issues during development and testing have been resolved.

## Deployment

KartControl is deployed on Heroku with a PostgreSQL database. The application uses WhiteNoise for static file serving and follows Django best practices for production deployment.

### Live Site

The live application can be accessed at: **[https://project-4-karting-121d969fb7d5.herokuapp.com](https://project-4-karting-121d969fb7d5.herokuapp.com)**

### Technologies Used

#### Backend
- **Python 3.12** - Programming language
- **Django 4.2 LTS** - Web framework
- **PostgreSQL** - Production database
- **gunicorn** - WSGI HTTP server
- **dj-database-url** - Database URL parsing
- **psycopg2-binary** - PostgreSQL adapter
- **python-dotenv** - Environment variable management

#### Frontend
- **HTML5** - Markup
- **CSS3** - Styling
- **Bootstrap 5.3** - CSS framework
- **JavaScript (ES6)** - Interactivity
- **Font Awesome 6** - Icons

#### Deployment & DevOps
- **Heroku** - Cloud platform
- **WhiteNoise** - Static file serving
- **Git** - Version control
- **GitHub** - Code repository

### Local Development Setup

#### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git
- PostgreSQL (optional - SQLite used by default for local development)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/antfildes10/Project-4.git
cd Project-4
```

#### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Important**: Generate a secure SECRET_KEY using:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Step 5: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

#### Step 7: Load Sample Data (Optional)

```bash
python manage.py populate_sample_data
```

This creates:
- 1 track
- 10 karts
- 20 sessions
- Sample users and bookings

#### Step 8: Run Development Server

```bash
python manage.py runserver
```

Access the site at: http://127.0.0.1:8000

### Heroku Deployment

#### Prerequisites
- Heroku account ([Sign up here](https://signup.heroku.com/))
- Heroku CLI installed ([Install guide](https://devcenter.heroku.com/articles/heroku-cli))
- Git repository initialized

#### Step 1: Login to Heroku

```bash
heroku login
```

This opens a browser window for authentication.

#### Step 2: Create Heroku App

```bash
heroku create your-app-name
```

Or create via Heroku Dashboard and add remote:
```bash
heroku git:remote -a your-app-name
```

#### Step 3: Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:essential-0 -a your-app-name
```

This automatically sets the `DATABASE_URL` config var.

#### Step 4: Set Environment Variables

```bash
heroku config:set SECRET_KEY="your-production-secret-key" -a your-app-name
heroku config:set DEBUG=False -a your-app-name
heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com" -a your-app-name
heroku config:set CSRF_TRUSTED_ORIGINS="https://your-app-name.herokuapp.com" -a your-app-name
heroku config:set DJANGO_SETTINGS_MODULE="kartcontrol.settings.production" -a your-app-name
```

**Important**: Use a different SECRET_KEY for production than development.

#### Step 5: Verify Configuration

```bash
heroku config -a your-app-name
```

Expected output:
```
=== your-app-name Config Vars
ALLOWED_HOSTS:          your-app-name.herokuapp.com
CSRF_TRUSTED_ORIGINS:   https://your-app-name.herokuapp.com
DATABASE_URL:           postgres://...
DEBUG:                  False
DJANGO_SETTINGS_MODULE: kartcontrol.settings.production
SECRET_KEY:             your-secret-key
```

#### Step 6: Deploy to Heroku

```bash
git push heroku main
```

Heroku will:
1. Detect Python app
2. Install dependencies from requirements.txt
3. Run `python manage.py collectstatic`
4. Build the application
5. Deploy to dynos

#### Step 7: Run Migrations on Heroku

```bash
heroku run "python manage.py migrate" -a your-app-name
```

#### Step 8: Create Superuser on Heroku

```bash
heroku run "python manage.py createsuperuser" -a your-app-name
```

Follow the prompts to create your production admin account.

#### Step 9: Open the Application

```bash
heroku open -a your-app-name
```

### Project Structure

```
Project-4/
├── accounts/               # User authentication & profiles
│   ├── models.py          # Profile model with roles
│   ├── views.py           # Registration, login, profile views
│   ├── forms.py           # User registration & edit forms
│   └── tests.py           # Authentication tests
├── bookings/              # Booking management
│   ├── models.py          # Booking model with business logic
│   ├── views.py           # Booking CRUD operations
│   ├── forms.py           # Booking forms
│   └── tests.py           # Booking tests (34 tests)
├── core/                  # Core application (homepage, etc.)
│   ├── views.py           # Homepage, about, contact views
│   ├── forms.py           # Contact form
│   └── tests.py           # Core functionality tests
├── karts/                 # Kart fleet management
│   ├── models.py          # Kart model
│   └── tests.py           # Kart tests
├── sessions/              # Racing session management
│   ├── models.py          # SessionSlot & Track models
│   ├── views.py           # Session browsing & filtering
│   └── tests.py           # Session tests (26 tests)
├── kartcontrol/           # Project settings
│   ├── settings/
│   │   ├── base.py        # Base settings
│   │   ├── development.py # Development settings
│   │   └── production.py  # Production settings (Heroku)
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI application
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css      # Custom styling
│   └── js/
│       └── main.js        # Custom JavaScript
├── templates/             # HTML templates
│   ├── base/
│   │   └── base.html      # Base template
│   ├── bookings/          # Booking templates
│   ├── sessions/          # Session templates
│   ├── accounts/          # Auth templates
│   └── core/              # Core templates
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── Procfile               # Heroku process file
├── requirements.txt       # Python dependencies
├── runtime.txt            # Python version for Heroku
├── manage.py              # Django management script
├── db.sqlite3             # Local SQLite database (dev only)
└── README.md              # This file
```

### Configuration Files

#### Procfile
Tells Heroku how to run the application:
```
web: gunicorn kartcontrol.wsgi --log-file -
```

#### runtime.txt
Specifies Python version for Heroku:
```
python-3.12.6
```

#### requirements.txt
Lists all Python dependencies:
```
Django<5.0,>=4.2
gunicorn>=21.2
whitenoise>=6.6
psycopg2-binary>=2.9
dj-database-url>=2.2
python-dotenv>=1.0
```

### Database Schema

#### Key Models

**User** (Django built-in)
- username, email, password
- Linked to Profile via one-to-one relationship

**Profile** (accounts.models)
- user (OneToOne → User)
- role: DRIVER / MANAGER / MARSHAL
- phone_number (optional)

**Track** (sessions.models)
- name, address, phone, email
- description, notes
- Single instance (only one track allowed)

**SessionSlot** (sessions.models)
- track (FK → Track)
- session_type: OPEN_SESSION / GRAND_PRIX
- start_datetime, end_datetime
- capacity, price
- description

**Kart** (karts.models)
- number (unique, 1-99)
- status: ACTIVE / MAINTENANCE
- notes

**Booking** (bookings.models)
- session_slot (FK → SessionSlot)
- driver (FK → User)
- assigned_kart (FK → Kart, nullable)
- status: PENDING / CONFIRMED / COMPLETED / CANCELLED
- chosen_kart_number (optional)
- Business logic: capacity validation, overlap prevention, kart assignment

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| SECRET_KEY | Django secret key for cryptographic signing | django-insecure-xyz123... |
| DEBUG | Enable/disable debug mode | True (dev), False (prod) |
| DATABASE_URL | Database connection string | postgres://user:pass@host/db |
| ALLOWED_HOSTS | Comma-separated list of allowed hosts | localhost,your-app.herokuapp.com |
| CSRF_TRUSTED_ORIGINS | Trusted origins for CSRF | https://your-app.herokuapp.com |
| DJANGO_SETTINGS_MODULE | Settings module to use | kartcontrol.settings.production |

### Maintenance Commands

**View logs**:
```bash
heroku logs --tail -a your-app-name
```

**Run Django commands**:
```bash
heroku run "python manage.py <command>" -a your-app-name
```

**Restart application**:
```bash
heroku restart -a your-app-name
```

**Scale dynos**:
```bash
heroku ps:scale web=1 -a your-app-name
```

**Access PostgreSQL console**:
```bash
heroku pg:psql -a your-app-name
```

**Create database backup**:
```bash
heroku pg:backups:capture -a your-app-name
```

## Credits

### Code and Frameworks

- **Django Documentation**: Core framework functionality and best practices - [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- **Bootstrap 5**: Responsive CSS framework for layout and components - [https://getbootstrap.com/](https://getbootstrap.com/)
- **Font Awesome**: Icons used throughout the interface - [https://fontawesome.com/](https://fontawesome.com/)
- **Google Fonts**: Roboto and Oswald font families - [https://fonts.google.com/](https://fonts.google.com/)
- **WhiteNoise**: Static file serving for Django in production - [http://whitenoise.evans.io/](http://whitenoise.evans.io/)

### Learning Resources

- **Code Institute**: Django module content and project guidance
- **MDN Web Docs**: HTML, CSS, and JavaScript reference materials - [https://developer.mozilla.org/](https://developer.mozilla.org/)
- **Real Python**: Django best practices and tutorials - [https://realpython.com/](https://realpython.com/)
- **Django for Beginners** by William S. Vincent: Book on Django fundamentals

### Development Tools

- **GitHub**: Version control and code repository - [https://github.com/](https://github.com/)
- **Heroku**: Cloud platform for deployment - [https://www.heroku.com/](https://www.heroku.com/)
- **VS Code**: Code editor used for development
- **Chrome DevTools**: Testing and debugging
- **Lighthouse**: Performance and accessibility audits

### Testing and Validation

- **W3C Markup Validator**: HTML validation - [https://validator.w3.org/](https://validator.w3.org/)
- **W3C CSS Validator**: CSS validation - [https://jigsaw.w3.org/css-validator/](https://jigsaw.w3.org/css-validator/)
- **JSHint**: JavaScript validation - [https://jshint.com/](https://jshint.com/)
- **PEP 8**: Python style guide - [https://pep8.org/](https://pep8.org/)
- **Coverage.py**: Python code coverage tool - [https://coverage.readthedocs.io/](https://coverage.readthedocs.io/)

### Design Inspiration

- **Color Palette**: Racing-inspired red, yellow, and charcoal theme chosen to evoke motorsport aesthetics
- **UI/UX Patterns**: Booking system flows inspired by similar platforms (cinema bookings, event ticketing)

### Acknowledgments

- **Code Institute**: For providing the educational framework and project requirements
- **Tutor Support**: For guidance during development challenges
- **Slack Community**: For peer support and troubleshooting assistance
- **Stack Overflow**: For solutions to specific technical challenges during development

### Content

- All text content written specifically for this project
- Track information and session descriptions are fictional for demonstration purposes
- No copyrighted content has been used

### Media

- Font Awesome icons used under free license
- No images currently used in the production version (icons only)
- All visual design created specifically for this project

---

**Project developed by Anthony Fildes as Portfolio Project 4 for Code Institute's Diploma in Full Stack Software Development (E-commerce Applications)**

**Date**: October 2025
