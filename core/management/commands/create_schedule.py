"""
Management command to create a proper recurring session schedule.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
from sessions.models import Track, SessionSlot


class Command(BaseCommand):
    help = 'Creates a recurring schedule of sessions (9am-10pm hourly)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to schedule (default: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing future sessions before creating new ones'
        )

    def handle(self, *args, **options):
        days_ahead = options['days']
        clear_existing = options['clear']

        # Get or create track
        track = Track.objects.first()
        if not track:
            self.stdout.write(self.style.ERROR('No track found. Please create a track first.'))
            return

        # Clear existing future sessions if requested
        if clear_existing:
            future_sessions = SessionSlot.objects.filter(start_datetime__gte=timezone.now())
            count = future_sessions.count()
            future_sessions.delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing future sessions'))

        # Session configuration
        HOURLY_SLOTS = list(range(9, 23))  # 9am to 10pm (9, 10, 11, ..., 22)
        WEEKDAY_GRAND_PRIX_HOUR = 18  # 6pm
        WEEKEND_GRAND_PRIX_HOURS = [12, 15, 18]  # 12pm, 3pm, 6pm
        
        OPEN_SESSION_DURATION = 60  # minutes
        GRAND_PRIX_DURATION = 90  # minutes
        
        OPEN_SESSION_CAPACITY = 10
        GRAND_PRIX_CAPACITY = 12
        
        OPEN_SESSION_PRICE = 35.00
        GRAND_PRIX_PRICE = 55.00

        created_count = 0
        skipped_count = 0
        
        # Get timezone-aware starting point
        now = timezone.now()
        start_date = now.date()

        self.stdout.write(f'Creating schedule for {days_ahead} days starting from {start_date}...')

        for day_offset in range(days_ahead):
            current_date = start_date + timedelta(days=day_offset)
            weekday = current_date.weekday()  # 0=Monday, 6=Sunday
            is_weekend = weekday >= 5  # Saturday or Sunday

            for hour in HOURLY_SLOTS:
                # Determine if this should be a Grand Prix session
                if is_weekend:
                    is_grand_prix = hour in WEEKEND_GRAND_PRIX_HOURS
                else:
                    is_grand_prix = hour == WEEKDAY_GRAND_PRIX_HOUR

                # Set session parameters
                if is_grand_prix:
                    session_type = 'GRAND_PRIX'
                    duration = GRAND_PRIX_DURATION
                    capacity = GRAND_PRIX_CAPACITY
                    price = GRAND_PRIX_PRICE
                else:
                    session_type = 'OPEN_SESSION'
                    duration = OPEN_SESSION_DURATION
                    capacity = OPEN_SESSION_CAPACITY
                    price = OPEN_SESSION_PRICE

                # Create datetime objects (timezone-aware)
                start_dt = timezone.make_aware(
                    datetime.combine(current_date, time(hour=hour, minute=0))
                )
                end_dt = start_dt + timedelta(minutes=duration)

                # Skip if in the past
                if start_dt < now:
                    skipped_count += 1
                    continue

                # Create session
                session, created = SessionSlot.objects.get_or_create(
                    track=track,
                    session_type=session_type,
                    start_datetime=start_dt,
                    defaults={
                        'end_datetime': end_dt,
                        'capacity': capacity,
                        'price': price
                    }
                )

                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n✓ Created {created_count} new sessions'))
        if skipped_count > 0:
            self.stdout.write(f'  Skipped {skipped_count} past time slots')
        
        # Summary statistics
        total_sessions = SessionSlot.objects.filter(start_datetime__gte=now).count()
        open_sessions = SessionSlot.objects.filter(
            start_datetime__gte=now, 
            session_type='OPEN_SESSION'
        ).count()
        grand_prix = SessionSlot.objects.filter(
            start_datetime__gte=now,
            session_type='GRAND_PRIX'
        ).count()
        
        self.stdout.write(self.style.SUCCESS('\n=== Schedule Summary ==='))
        self.stdout.write(f'Total upcoming sessions: {total_sessions}')
        self.stdout.write(f'  • Open Sessions: {open_sessions}')
        self.stdout.write(f'  • Grand Prix: {grand_prix}')
        self.stdout.write('\nSchedule:')
        self.stdout.write('  • Monday-Friday: Hourly 9am-10pm (6pm = Grand Prix)')
        self.stdout.write('  • Saturday-Sunday: Hourly 9am-10pm (12pm, 3pm, 6pm = Grand Prix)')
