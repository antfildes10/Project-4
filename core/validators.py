"""
Shared validation utilities for the KartControl application.

This module provides reusable validation functions for:
- Date and time validations
- Session slot validations
- Booking validations
- Kart validations
"""

from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


# =============================================================================
# DATE & TIME VALIDATORS
# =============================================================================

def validate_future_datetime(value, field_name='datetime'):
    """
    Validate that a datetime is in the future.

    Args:
        value (datetime): The datetime to validate
        field_name (str): Name of the field for error message

    Raises:
        ValidationError: If datetime is not in the future

    Example:
        >>> validate_future_datetime(start_datetime, 'Start time')
    """
    if value <= timezone.now():
        raise ValidationError(
            f'{field_name} must be in the future.'
        )


def validate_datetime_order(start, end, start_name='Start', end_name='End'):
    """
    Validate that start datetime is before end datetime.

    Args:
        start (datetime): The start datetime
        end (datetime): The end datetime
        start_name (str): Name of start field for error message
        end_name (str): Name of end field for error message

    Raises:
        ValidationError: If start is not before end

    Example:
        >>> validate_datetime_order(start_datetime, end_datetime)
    """
    if start >= end:
        raise ValidationError(
            f'{start_name} must be before {end_name}.'
        )


def validate_minimum_duration(start, end, min_minutes=30):
    """
    Validate that duration between start and end meets minimum.

    Args:
        start (datetime): The start datetime
        end (datetime): The end datetime
        min_minutes (int): Minimum duration in minutes

    Raises:
        ValidationError: If duration is less than minimum

    Example:
        >>> validate_minimum_duration(start_datetime, end_datetime, 30)
    """
    duration = (end - start).total_seconds() / 60
    if duration < min_minutes:
        raise ValidationError(
            f'Duration must be at least {min_minutes} minutes. '
            f'Current duration: {int(duration)} minutes.'
        )


def validate_maximum_duration(start, end, max_minutes=240):
    """
    Validate that duration between start and end does not exceed maximum.

    Args:
        start (datetime): The start datetime
        end (datetime): The end datetime
        max_minutes (int): Maximum duration in minutes

    Raises:
        ValidationError: If duration exceeds maximum

    Example:
        >>> validate_maximum_duration(start_datetime, end_datetime, 240)
    """
    duration = (end - start).total_seconds() / 60
    if duration > max_minutes:
        raise ValidationError(
            f'Duration cannot exceed {max_minutes} minutes. '
            f'Current duration: {int(duration)} minutes.'
        )


# =============================================================================
# SESSION SLOT VALIDATORS
# =============================================================================

def validate_session_times(start_datetime, end_datetime):
    """
    Comprehensive validation for session slot times.

    Validates:
    - Start is in the future
    - Start is before end
    - Minimum duration of 30 minutes
    - Maximum duration of 4 hours

    Args:
        start_datetime (datetime): Session start time
        end_datetime (datetime): Session end time

    Raises:
        ValidationError: If any validation fails

    Example:
        >>> validate_session_times(start_datetime, end_datetime)
    """
    # Check start is in future
    validate_future_datetime(start_datetime, 'Start time')

    # Check start is before end
    validate_datetime_order(start_datetime, end_datetime, 'Start time', 'End time')

    # Check minimum duration (30 minutes)
    validate_minimum_duration(start_datetime, end_datetime, min_minutes=30)

    # Check maximum duration (4 hours)
    validate_maximum_duration(start_datetime, end_datetime, max_minutes=240)


def validate_session_capacity(capacity):
    """
    Validate session capacity is within acceptable range.

    Args:
        capacity (int): The session capacity

    Raises:
        ValidationError: If capacity is invalid

    Example:
        >>> validate_session_capacity(12)
    """
    if capacity < 1:
        raise ValidationError('Capacity must be at least 1.')

    if capacity > 20:
        raise ValidationError(
            'Capacity cannot exceed 20 drivers for safety reasons.'
        )


# =============================================================================
# BOOKING VALIDATORS
# =============================================================================

def validate_booking_not_in_past(session_start):
    """
    Validate that a booking is not for a past session.

    Args:
        session_start (datetime): The session start datetime

    Raises:
        ValidationError: If session has already started

    Example:
        >>> validate_booking_not_in_past(session.start_datetime)
    """
    if session_start <= timezone.now():
        raise ValidationError(
            'Cannot create or modify booking for a session that has already started.'
        )


def validate_booking_advance_time(session_start, min_hours=2):
    """
    Validate that booking is made with sufficient advance notice.

    Args:
        session_start (datetime): The session start datetime
        min_hours (int): Minimum hours in advance required

    Raises:
        ValidationError: If booking is too close to session start

    Example:
        >>> validate_booking_advance_time(session.start_datetime, min_hours=2)
    """
    time_until_session = session_start - timezone.now()
    if time_until_session < timedelta(hours=min_hours):
        hours_remaining = time_until_session.total_seconds() / 3600
        raise ValidationError(
            f'Bookings must be made at least {min_hours} hours in advance. '
            f'Only {hours_remaining:.1f} hours until session starts.'
        )


# =============================================================================
# KART VALIDATORS
# =============================================================================

def validate_kart_number(number):
    """
    Validate kart number is within acceptable range.

    Args:
        number (int): The kart number

    Raises:
        ValidationError: If number is invalid

    Example:
        >>> validate_kart_number(5)
    """
    if number < 1:
        raise ValidationError('Kart number must be at least 1.')

    if number > 99:
        raise ValidationError('Kart number cannot exceed 99.')


# =============================================================================
# GENERAL VALIDATORS
# =============================================================================

def validate_positive_decimal(value, field_name='Value'):
    """
    Validate that a decimal value is positive.

    Args:
        value (Decimal): The value to validate
        field_name (str): Name of the field for error message

    Raises:
        ValidationError: If value is not positive

    Example:
        >>> validate_positive_decimal(price, 'Price')
    """
    if value <= 0:
        raise ValidationError(f'{field_name} must be greater than zero.')
