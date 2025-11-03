# Data Model Documentation

## Overview

The KartControl database schema manages a go-kart racing facility with session bookings, kart fleet management, and role-based access control. The system uses PostgreSQL in production and SQLite for development.

## Entity Relationship Diagram

```
User (Django) ─────1:1─────▶ Profile (role: DRIVER/MANAGER/MARSHAL)
                                    │
Track (singleton) ─1:N─▶ SessionSlot │
                             │       │
                           1:N       │
                             │       │
                             ▼       │
                         Booking ◀───┘
                             │
                           N:1
                             │
                             ▼
                          Kart (1-99, ACTIVE/MAINTENANCE)
```

## Core Models

### 1. Profile (accounts/models.py)
**Purpose:** Extends Django User with role-based access control

**Fields:**
- `user`: OneToOneField → User (CASCADE)
- `role`: CharField - DRIVER, MANAGER, or MARSHAL
- `phone_number`: CharField(20) - Optional contact
- `date_of_birth`: DateField - Optional for age verification
- `created_at`, `updated_at`: DateTime fields

**Business Rules:**
- Auto-created on user registration (signal)
- Roles determine system-wide permissions
- CASCADE delete with User

### 2. Track (sessions/models.py)
**Purpose:** Go-kart track information (Singleton pattern)

**Fields:**
- `name`: CharField(200)
- `description`: TextField
- `address`: TextField
- `capacity`: PositiveIntegerField (max simultaneous drivers)
- `created_at`, `updated_at`

**Business Rules:**
- **Only ONE track allowed** (enforced in save())
- Cannot delete if SessionSlots exist

### 3. SessionSlot (sessions/models.py)
**Purpose:** Bookable time slots for racing

**Fields:**
- `track`: ForeignKey → Track (CASCADE)
- `session_type`: OPEN_SESSION or GRAND_PRIX
- `start_datetime`, `end_datetime`: DateTimeField
- `capacity`: PositiveIntegerField (≥1)
- `price`: DecimalField(6,2) (≥0)
- `created_at`, `updated_at`

**Validation:**
- start_datetime < end_datetime
- No overlapping sessions
- Capacity ≥ existing confirmed bookings

**Methods:**
- `is_full()` - Check if capacity reached
- `is_past()` - Check if session ended
- `get_available_spots()` - Remaining capacity

### 4. Kart (karts/models.py)
**Purpose:** Fleet management

**Fields:**
- `number`: PositiveIntegerField (1-99, UNIQUE)
- `status`: ACTIVE or MAINTENANCE
- `created_at`, `updated_at`

**Business Rules:**
- Only ACTIVE karts assignable to bookings
- Cannot delete karts with bookings
- Unique kart numbers

### 5. Booking (bookings/models.py)
**Purpose:** Session reservations with complex business logic

**Fields:**
- `session_slot`: ForeignKey → SessionSlot (CASCADE)
- `driver`: ForeignKey → User (CASCADE)
- `assigned_kart`: ForeignKey → Kart (SET_NULL)
- `status`: PENDING → CONFIRMED → COMPLETED/CANCELLED
- `chosen_kart_number`: PositiveIntegerField (optional preference)
- `driver_notes`, `manager_notes`: TextField
- `created_at`, `updated_at`

**State Machine:**
```
PENDING ──confirm()──▶ CONFIRMED ──complete()──▶ COMPLETED
   │                       │
   └───cancel()──▶ CANCELLED
                           │
                    (can also cancel)
```

**Business Rules (validated in clean()):**

1. **Capacity Enforcement:** PENDING + CONFIRMED ≤ session capacity
2. **Driver Overlap Prevention:** No time conflicts for same driver
3. **Kart Availability:** Only ACTIVE karts can be assigned
4. **State Validation:**
   - CANCELLED bookings cannot be reactivated
   - COMPLETED bookings immutable
   - CONFIRMED must have assigned_kart
5. **Time Validation:** Cannot book past sessions

**Race Condition Prevention:**
```python
# Row-level locking in assign_random_kart()
with transaction.atomic():
    available_karts = Kart.objects.select_for_update()
    overlapping_sessions = SessionSlot.objects.filter(
        Q(start_datetime__lt=self.session_slot.end_datetime) &
        Q(end_datetime__gt=self.session_slot.start_datetime)
    )
    # Excludes karts assigned to overlapping sessions
```

**Custom QuerySet Methods:**
- `upcoming()` - Future PENDING/CONFIRMED bookings
- `for_driver(driver)` - Driver's bookings
- `upcoming_for_driver(driver)` - Combined filter
- `completed()`, `cancelled()`, `pending()`, `confirmed()` - Status filters

## Database Indexes

**Performance optimization for common queries:**

### Booking Model (bookings/models.py:147-155)
```python
indexes = [
    models.Index(fields=["driver"]),  # Fast user lookup
    models.Index(fields=["session_slot"]),  # Session bookings
    models.Index(fields=["status"]),  # Status filtering
    # Composite indexes for multi-condition queries
    models.Index(fields=["driver", "session_slot"]),  # Duplicate check
    models.Index(fields=["session_slot", "status"]),  # Active bookings
    models.Index(fields=["driver", "status"]),  # User's active bookings
]
```

**Rationale:**
- Single indexes: O(log n) lookup vs O(n) table scan
- Composite indexes: Eliminate need for multiple index lookups
- Most frequent query: "Show my upcoming bookings" uses (driver, status) index

### SessionSlot Model
- Index on `start_datetime` for date-range queries

## Foreign Key Relationships

### CASCADE Deletes:
- User → Profile (delete user → delete profile)
- User → Booking (delete user → delete bookings)
- Track → SessionSlot (delete track → delete sessions)
- SessionSlot → Booking (delete session → delete bookings)

### SET_NULL:
- Kart → Booking (delete kart → keep booking, null kart reference)

### PROTECT:
- Track protected if SessionSlots exist
- SessionSlot protected if CONFIRMED Bookings exist

## Data Integrity

### Database Constraints

**Unique:**
- User.username
- User.email
- Kart.number
- Profile.user (OneToOne)

**Check Constraints (via validators):**
- SessionSlot.capacity ≥ 1
- SessionSlot.price ≥ 0
- Kart.number: 1-99
- SessionSlot: start < end

### Application-Level Validation

**Model clean() Methods:**

1. **SessionSlot.clean():**
   - Validates time ordering
   - Checks for overlapping sessions

2. **Booking.clean():**
   - Capacity enforcement
   - Driver overlap prevention
   - State transition validation
   - Kart assignment validation

3. **Track.save():**
   - Singleton pattern enforcement

## Query Optimization

### N+1 Query Prevention

**select_related() for ForeignKey:**
```python
# ✅ GOOD: Single query
bookings = Booking.objects.select_related(
    "session_slot", "assigned_kart"
).filter(driver=user)

# ❌ BAD: N+1 queries
bookings = Booking.objects.filter(driver=user)
for booking in bookings:
    print(booking.session_slot.name)  # Extra query!
```

### Atomic Transactions

**Critical operations protected:**
```python
from django.db import transaction

with transaction.atomic():
    session = SessionSlot.objects.select_for_update().get(pk=id)
    if session.get_available_spots() > 0:
        booking = Booking.objects.create(...)
```

**Row-level locking:**
- `select_for_update()` locks rows
- Prevents concurrent modifications
- Used in booking creation and kart assignment

## Database Configuration

### Development (SQLite)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Production (PostgreSQL)
```python
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,  # Connection pooling
        ssl_require=True
    )
}
```

## Security

**SQL Injection Prevention:**
- Django ORM auto-parameterizes queries
- No raw SQL without parameterization
- Form validation sanitizes all input

**Data Protection:**
- Passwords hashed with PBKDF2-SHA256
- Database credentials in environment variables
- SSL required for production database
- CSRF protection on all forms

## Migrations

**All migrations in `*/migrations/` directories**

**Key migrations:**
1. `accounts/migrations/0001_initial.py` - Profile
2. `sessions/migrations/0001_initial.py` - Track, SessionSlot
3. `karts/migrations/0001_initial.py` - Kart
4. `bookings/migrations/0001_initial.py` - Booking with indexes

**Migration safety:**
- All reversible (except data migrations)
- No data loss on rollback
- Tested before production

## Summary

The KartControl schema demonstrates:

✅ **Normalized structure** - No redundant data
✅ **Data integrity** - Foreign keys, constraints, validators
✅ **Business logic** - Model-level validation
✅ **Performance** - Strategic indexes, query optimization
✅ **Security** - Parameterized queries, hashed passwords
✅ **Scalability** - Atomic transactions, row locking

The schema supports all business requirements while maintaining flexibility for future enhancements.
