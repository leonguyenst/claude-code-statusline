#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test cost-based percentage calculation"""
import sys, io

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
COST_LIMIT_PER_SESSION = 5.0  # $5 per 5 hours for Claude Pro

# Test cases based on real data
test_cases = [
    (2.37, 48),   # Current: $2.37 should be ~48%
    (1.00, 20),   # $1 should be 20%
    (2.50, 50),   # $2.50 should be 50%
    (5.00, 100),  # $5 should be 100%
    (0.00, 0),    # $0 should be 0%
]

print("Testing cost-based percentage calculation:")
print(f"Cost limit: ${COST_LIMIT_PER_SESSION:.2f} per session\n")

for cost, expected_pct in test_cases:
    calculated_pct = int((cost / COST_LIMIT_PER_SESSION) * 100)
    calculated_pct = max(0, min(100, calculated_pct))  # Clamp to 0-100%

    status = "✅" if abs(calculated_pct - expected_pct) <= 1 else "❌"
    print(f"{status} Cost: ${cost:.2f} | Expected: {expected_pct}% | Calculated: {calculated_pct}%")
