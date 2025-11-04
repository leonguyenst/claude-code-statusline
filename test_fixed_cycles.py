#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for fixed cycle time calculation"""
import sys, io
from datetime import datetime, timedelta

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def calculate_fixed_cycle_time_remaining():
    """
    Calculate time remaining until next fixed cycle reset
    Cycles are at: 6:00, 11:00, 16:00, 21:00 daily
    Returns: (hours, minutes, total_seconds, next_reset_time)
    """
    try:
        # Define cycle times in 24-hour format
        cycle_hours = [6, 11, 16, 21]

        # Get current time
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute

        # Find next cycle time
        next_cycle_hour = None
        for cycle_hour in cycle_hours:
            if current_hour < cycle_hour or (current_hour == cycle_hour and current_minute < 0):
                next_cycle_hour = cycle_hour
                break

        # If no cycle found today, use first cycle of next day
        if next_cycle_hour is None:
            next_cycle_hour = cycle_hours[0]
            next_reset = now.replace(hour=next_cycle_hour, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            next_reset = now.replace(hour=next_cycle_hour, minute=0, second=0, microsecond=0)

        # Calculate remaining time
        remaining = next_reset - now
        total_seconds = int(remaining.total_seconds())

        if total_seconds <= 0:
            return None, None, 0, None

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        return hours, minutes, total_seconds, next_reset
    except Exception:
        return None, None, 0, None

# Test cases
print("Testing fixed cycle time calculation:\n")

# Test current time
now = datetime.now()
hours, minutes, seconds, next_reset = calculate_fixed_cycle_time_remaining()
print(f"Current time: {now.strftime('%H:%M:%S')}")
if next_reset:
    print(f"Next reset at: {next_reset.strftime('%H:%M')}")
    print(f"Time remaining: {hours}h {minutes}m ({seconds} seconds)")
    print()

# Test specific times
test_cases = [
    ("18:40", 21, 2, 20),  # 18:40 -> 21:00 (2h20m)
    ("05:30", 6, 0, 30),   # 05:30 -> 06:00 (0h30m)
    ("10:45", 11, 0, 15),  # 10:45 -> 11:00 (0h15m)
    ("15:00", 16, 1, 0),   # 15:00 -> 16:00 (1h0m)
    ("20:30", 21, 0, 30),  # 20:30 -> 21:00 (0h30m)
    ("22:00", 6, 8, 0),    # 22:00 -> 06:00 next day (8h0m)
]

print("Test cases:")
for time_str, expected_next_hour, expected_hours, expected_minutes in test_cases:
    # Mock current time
    hour, minute = map(int, time_str.split(':'))
    test_now = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Calculate for test time
    cycle_hours = [6, 11, 16, 21]
    next_cycle_hour = None
    for cycle_hour in cycle_hours:
        if test_now.hour < cycle_hour:
            next_cycle_hour = cycle_hour
            break

    if next_cycle_hour is None:
        next_cycle_hour = cycle_hours[0]
        next_reset = test_now.replace(hour=next_cycle_hour, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        next_reset = test_now.replace(hour=next_cycle_hour, minute=0, second=0, microsecond=0)

    remaining = next_reset - test_now
    total_seconds = int(remaining.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    status = "✅" if (hours == expected_hours and minutes == expected_minutes) else "❌"
    print(f"{status} {time_str} -> {next_reset.strftime('%H:%M')} | Expected: {expected_hours}h {expected_minutes}m | Got: {hours}h {minutes}m")
