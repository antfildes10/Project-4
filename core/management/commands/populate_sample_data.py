"""
Management command to populate the database with sample data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from sessions.models import Track, SessionSlot
from karts.models import Kart
from accounts.models import Profile
from bookings.models import Booking


class Command(BaseCommand):
    help = 'Populates the database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create Track
        track, created = Track.objects.get_or_create(
            name='KartControl Racing Track',
            defaults={
                'address': 'Dublin International Karting Circuit\nNaas Road\nDublin 12\nIreland',
                'phone': '+353 1 234 5678',
                'email': 'info@kartcontrol.com',
                'description': 'Ireland\'s premier indoor and outdoor karting facility featuring a challenging 1.2km circuit with 15 corners. Perfect for both beginners and experienced racers.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created track: {track.name}'))
        else:
            self.stdout.write(f'  Track already exists: {track.name}')

        # Create Karts
        kart_count = 0
        for i in range(1, 11):  # Create karts 1-10
            kart, created = Kart.objects.get_or_create(
                number=i,
                defaults={'status': 'ACTIVE'}
            )
            if created:
                kart_count += 1
        self.stdout.write(self.style.SUCCESS(f'✓ Created {kart_count} karts'))

        # Create test users
        users_data = [
            {'username': 'john_driver', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Smith', 'role': 'DRIVER'},
            {'username': 'jane_racer', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Doe', 'role': 'DRIVER'},
            {'username': 'mike_manager', 'email': 'mike@example.com', 'first_name': 'Mike', 'last_name': 'Johnson', 'role': 'MANAGER'},
            {'username': 'sarah_marshal', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Williams', 'role': 'MARSHAL'},
        ]

        user_count = 0
        for user_data in users_data:
            role = user_data.pop('role')
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password('password123')
                user.save()
                user.profile.role = role
                user.profile.save()
                user_count += 1
        self.stdout.write(self.style.SUCCESS(f'✓ Created {user_count} test users'))

        # Create Session Slots
        now = timezone.now()
        sessions_data = [
            # Past sessions
            {'session_type': 'OPEN_SESSION', 'start': now - timedelta(days=3, hours=2), 'duration': 60, 'capacity': 10, 'price': 35.00},
            {'session_type': 'GRAND_PRIX', 'start': now - timedelta(days=2, hours=3), 'duration': 90, 'capacity': 12, 'price': 55.00},
            
            # Today's sessions
            {'session_type': 'OPEN_SESSION', 'start': now + timedelta(hours=2), 'duration': 60, 'capacity': 10, 'price': 35.00},
            {'session_type': 'GRAND_PRIX', 'start': now + timedelta(hours=5), 'duration': 90, 'capacity': 12, 'price': 55.00},
            
            # Tomorrow
            {'session_type': 'OPEN_SESSION', 'start': now + timedelta(days=1, hours=10), 'duration': 60, 'capacity': 10, 'price': 35.00},
            {'session_type': 'GRAND_PRIX', 'start': now + timedelta(days=1, hours=14), 'duration': 90, 'capacity': 12, 'price': 55.00},
            {'session_type': 'OPEN_SESSION', 'start': now + timedelta(days=1, hours=18), 'duration': 60, 'capacity': 10, 'price': 35.00},
            
            # Next week
            {'session_type': 'GRAND_PRIX', 'start': now + timedelta(days=7, hours=10), 'duration': 120, 'capacity': 15, 'price': 65.00},
            {'session_type': 'OPEN_SESSION', 'start': now + timedelta(days=7, hours=15), 'duration': 60, 'capacity': 10, 'price': 35.00},
            {'session_type': 'GRAND_PRIX', 'start': now + timedelta(days=8, hours=14), 'duration': 90, 'capacity': 12, 'price': 55.00},
            
            # Two weeks out
            {'session_type': 'OPEN_SESSION', 'start': now + timedelta(days=14, hours=10), 'duration': 60, 'capacity': 10, 'price': 35.00},
            {'session_type': 'OPEN_SESSION', 'start': now + timedelta(days=14, hours=14), 'duration': 60, 'capacity': 10, 'price': 35.00},
            {'session_type': 'GRAND_PRIX', 'start': now + timedelta(days=14, hours=18), 'duration': 120, 'capacity': 15, 'price': 65.00},
            
            # Weekend special
            {'session_type': 'GRAND_PRIX', 'start': now + timedelta(days=5, hours=12), 'duration': 120, 'capacity': 15, 'price': 70.00},
            {'session_type': 'OPEN_SESSION', 'start': now + timedelta(days=6, hours=10), 'duration': 60, 'capacity': 12, 'price': 40.00},
        ]

        session_count = 0
        for session_data in sessions_data:
            start_dt = session_data['start']
            end_dt = start_dt + timedelta(minutes=session_data['duration'])
            
            session, created = SessionSlot.objects.get_or_create(
                session_type=session_data['session_type'],
                start_datetime=start_dt,
                defaults={
                    'track': track,
                    'end_datetime': end_dt,
                    'capacity': session_data['capacity'],
                    'price': session_data['price']
                }
            )
            if created:
                session_count += 1
        self.stdout.write(self.style.SUCCESS(f'✓ Created {session_count} session slots'))

        # Create some sample bookings for past sessions
        past_sessions = SessionSlot.objects.filter(start_datetime__lt=now)[:2]
        drivers = User.objects.filter(profile__role='DRIVER')
        
        booking_count = 0
        for session in past_sessions:
            for driver in drivers[:3]:  # Book first 3 drivers
                booking, created = Booking.objects.get_or_create(
                    session_slot=session,
                    driver=driver,
                    defaults={
                        'status': 'COMPLETED',
                        'assigned_kart': Kart.objects.filter(status='ACTIVE').first()
                    }
                )
                if created:
                    booking_count += 1
        
        # Create some pending bookings for upcoming sessions
        upcoming_sessions = SessionSlot.objects.filter(start_datetime__gt=now)[:3]
        for session in upcoming_sessions:
            if drivers.exists():
                booking, created = Booking.objects.get_or_create(
                    session_slot=session,
                    driver=drivers.first(),
                    defaults={'status': 'PENDING'}
                )
                if created:
                    booking_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {booking_count} sample bookings'))

        self.stdout.write(self.style.SUCCESS('\n=== Sample Data Created Successfully! ==='))
        self.stdout.write('\nTest User Credentials (all passwords: password123):')
        self.stdout.write('  • john_driver (Driver)')
        self.stdout.write('  • jane_racer (Driver)')
        self.stdout.write('  • mike_manager (Manager)')
        self.stdout.write('  • sarah_marshal (Marshal)')
        self.stdout.write('\nAdmin User:')
        self.stdout.write('  • admin (superuser - set password on first login)')
        self.stdout.write(f'\nSessions Created:')
        self.stdout.write(f'  • Open Sessions: {SessionSlot.objects.filter(session_type="OPEN_SESSION").count()}')
        self.stdout.write(f'  • Grand Prix: {SessionSlot.objects.filter(session_type="GRAND_PRIX").count()}')
        self.stdout.write(f'  • Total Karts: {Kart.objects.count()}')
