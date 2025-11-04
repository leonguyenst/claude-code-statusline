#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys, os, subprocess, io
from datetime import datetime, timedelta
from pathlib import Path

# Configuration: Toggle between time calculation methods
# Set to True to use fixed cycle times (6h, 11h, 16h, 21h)
# Set to False to use original 5-hour block calculation
USE_FIXED_CYCLES = True

# Configuration: Cost limit per 5-hour session (Claude Pro)
# Adjust this based on your plan
COST_LIMIT_PER_SESSION = 5.0  # $5 per 5 hours for Claude Pro

# Fix encoding on Windows
if sys.platform == "win32":
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Beautiful color palette (RGB)
class Colors:
    # Neon gradient colors
    CYAN = "\033[38;2;0;240;255m"        # Bright cyan
    BLUE = "\033[38;2;100;150;255m"      # Sky blue
    PURPLE = "\033[38;2;180;100;255m"    # Purple
    MAGENTA = "\033[38;2;255;0;240m"     # Neon magenta
    PINK = "\033[38;2;255;105;180m"      # Hot pink
    ORANGE = "\033[38;2;255;165;0m"      # Orange
    YELLOW = "\033[38;2;255;220;0m"      # Gold
    GREEN = "\033[38;2;0;255;150m"       # Neon green
    RED = "\033[38;2;255;50;100m"        # Red

    # Subtle colors
    GRAY = "\033[38;2;150;150;150m"      # Gray
    WHITE = "\033[38;2;255;255;255m"     # White

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

def get_context_length_from_transcript(transcript_path):
    """Parse transcript JSONL to get current context length"""
    try:
        if not os.path.exists(transcript_path):
            return 0

        with open(transcript_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        most_recent_timestamp = None
        context_length = 0

        for line in lines:
            try:
                data = json.loads(line.strip())
                # Skip sidechain and error messages
                if data.get('isSidechain') or data.get('isApiErrorMessage'):
                    continue

                usage = data.get('message', {}).get('usage', {})
                timestamp_str = data.get('timestamp')

                if not usage or not timestamp_str:
                    continue

                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

                # Track most recent main chain entry
                if most_recent_timestamp is None or timestamp > most_recent_timestamp:
                    most_recent_timestamp = timestamp
                    # Context = input_tokens + cache_read + cache_creation
                    context_length = (
                        usage.get('input_tokens', 0) +
                        usage.get('cache_read_input_tokens', 0) +
                        usage.get('cache_creation_input_tokens', 0)
                    )
            except Exception:
                continue

        return context_length
    except Exception:
        return 0

def get_block_start_time(transcript_path):
    """
    Calculate the start time of current 5-hour block
    Based on ccstatusline logic
    """
    try:
        if not transcript_path or not os.path.exists(transcript_path):
            return None

        with open(transcript_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        timestamps = []
        for line in lines:
            try:
                data = json.loads(line.strip())
                if data.get('isSidechain') or data.get('isApiErrorMessage'):
                    continue

                usage = data.get('message', {}).get('usage', {})
                if not usage.get('input_tokens') or not usage.get('output_tokens'):
                    continue

                timestamp_str = data.get('timestamp')
                if timestamp_str:
                    ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    timestamps.append(ts)
            except Exception:
                continue

        if not timestamps:
            return None

        # Sort timestamps
        timestamps.sort()

        # Find session gaps (5 hours)
        session_duration_ms = 5 * 60 * 60 * 1000
        blocks = []
        current_block_start = None

        for ts in timestamps:
            # Floor timestamp to hour (like ccstatusline does)
            floored = ts.replace(minute=0, second=0, microsecond=0)

            if current_block_start is None:
                current_block_start = floored
                current_block_end = current_block_start + timedelta(milliseconds=session_duration_ms)
                blocks.append({'start': current_block_start, 'end': current_block_end})
            else:
                # Check if timestamp is beyond current block end
                if ts > current_block_end:
                    # Start new block
                    current_block_start = floored
                    current_block_end = current_block_start + timedelta(milliseconds=session_duration_ms)
                    blocks.append({'start': current_block_start, 'end': current_block_end})

        # Find current block
        now = datetime.now(timestamps[0].tzinfo) if timestamps else datetime.now()
        for block in blocks:
            if block['start'] <= now <= block['end']:
                return block['start']

        # If no current block found, return most recent block start
        return blocks[-1]['start'] if blocks else None

    except Exception:
        return None

def get_git_info(cwd):
    """Get git branch and status"""
    try:
        # Get branch name
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            cwd=cwd
        )
        if result.returncode == 0 and result.stdout.strip():
            branch = result.stdout.strip()

            # Get git status (check if dirty)
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                cwd=cwd
            )
            is_dirty = bool(status_result.stdout.strip())

            return branch, is_dirty
    except Exception:
        pass
    return None, False

def format_time_remaining(start_time):
    """Format time remaining in 5-hour block"""
    try:
        now = datetime.now(start_time.tzinfo)
        block_duration = timedelta(hours=5)
        block_end = start_time + block_duration

        remaining = block_end - now
        if remaining.total_seconds() <= 0:
            return None, None, 0

        total_seconds = int(remaining.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        return hours, minutes, total_seconds
    except Exception:
        return None, None, 0

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

def get_usage_info_from_ccusage():
    """Get usage information from ccusage command"""
    try:
        # Try to find ccusage command
        ccusage_cmd = "ccusage"

        # On Windows, try common npm global paths
        if sys.platform == "win32":
            possible_paths = [
                "ccusage",  # Try PATH first
                os.path.expandvars("%APPDATA%\\npm\\ccusage.cmd"),
                os.path.expandvars("%USERPROFILE%\\AppData\\Roaming\\npm\\ccusage.cmd"),
            ]

            # Try fnm paths
            appdata_roaming = os.path.expandvars("%APPDATA%")
            if os.path.exists(os.path.join(appdata_roaming, "fnm")):
                # Look for ccusage in fnm node versions
                fnm_dir = os.path.join(appdata_roaming, "fnm", "node-versions")
                if os.path.exists(fnm_dir):
                    for version_dir in os.listdir(fnm_dir):
                        ccusage_path = os.path.join(fnm_dir, version_dir, "installation", "ccusage.cmd")
                        if os.path.exists(ccusage_path):
                            possible_paths.append(ccusage_path)
                            break
        else:
            possible_paths = ["ccusage"]

        # Try each possible command
        for cmd in possible_paths:
            try:
                result = subprocess.run(
                    [cmd, "blocks", "--json"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    timeout=5,
                    shell=True if sys.platform == "win32" else False
                )

                if result.returncode == 0 and result.stdout.strip():
                    break
            except (FileNotFoundError, OSError):
                continue
        else:
            return None

        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            blocks = data.get('blocks', [])

            # Find active block first
            for block in blocks:
                if block.get('isActive'):
                    return {
                        'start_time': block.get('startTime'),
                        'reset_time': block.get('usageLimitResetTime') or block.get('endTime'),
                        'total_tokens': block.get('totalTokens', 0),
                        'cost_usd': block.get('costUSD', 0),
                        'tokens_per_minute': block.get('burnRate', {}).get('tokensPerMinute', 0),
                        'entries': block.get('entries', 0)
                    }

            # Fallback: Find most recent non-gap block
            for block in reversed(blocks):
                if not block.get('isGap'):
                    return {
                        'start_time': block.get('startTime'),
                        'reset_time': block.get('usageLimitResetTime') or block.get('endTime'),
                        'total_tokens': block.get('totalTokens', 0),
                        'cost_usd': block.get('costUSD', 0),
                        'tokens_per_minute': block.get('burnRate', {}).get('tokensPerMinute', 0),
                        'entries': block.get('entries', 0)
                    }
    except Exception:
        pass
    return None

def format_progress_bar(percentage, width=10):
    """Create a progress bar string"""
    try:
        percentage = max(0, min(100, int(percentage)))
        filled = int(percentage * width / 100)
        empty = width - filled
        return f"[{'=' * filled}{'-' * empty}]"
    except Exception:
        return ""

def calculate_session_percentage(start_time_str, reset_time_str):
    """Calculate percentage of session elapsed"""
    try:
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        reset_time = datetime.fromisoformat(reset_time_str.replace('Z', '+00:00'))
        now = datetime.now(start_time.tzinfo)

        total_duration = (reset_time - start_time).total_seconds()
        elapsed = (now - start_time).total_seconds()

        if total_duration <= 0:
            return 0

        percentage = (elapsed / total_duration) * 100
        return max(0, min(100, int(percentage)))
    except Exception:
        return 0

try:
    # Load input data
    data = json.load(sys.stdin)

    # Extract data
    model = data.get("model", {}).get("display_name", "Claude")
    workspace = data.get("workspace", {})
    transcript_path = data.get("transcript_path", "")

    cost_data = data.get("cost", {})
    lines_added = cost_data.get("total_lines_added", 0)
    lines_removed = cost_data.get("total_lines_removed", 0)

    # Get git info
    branch, is_dirty = get_git_info(workspace.get("current_dir", "."))

    # Get context length from transcript
    context_length = get_context_length_from_transcript(transcript_path)
    context_percentage = (context_length / 200000) * 100 if context_length > 0 else 0

    # Get block start time from transcript
    block_start = get_block_start_time(transcript_path)

    # Get usage info from ccusage
    usage_info = get_usage_info_from_ccusage()

    # Build status line parts
    parts = []

    # Model info
    parts.append(f"{Colors.CYAN}{Colors.BOLD}🤖 {model}{Colors.RESET}")

    # Git branch
    if branch:
        git_icon = "🔴" if is_dirty else "🌿"
        parts.append(f"{Colors.GREEN}{git_icon} {branch}{Colors.RESET}")

    # Session timer - Choose calculation method based on configuration
    if USE_FIXED_CYCLES:
        # Use fixed cycle times (6h, 11h, 16h, 21h)
        hours_left, minutes_left, seconds_left, next_reset = calculate_fixed_cycle_time_remaining()
        if seconds_left and seconds_left > 0:
            # Color based on remaining time
            if seconds_left > 3600:  # More than 1 hour
                time_color = Colors.GREEN
            elif seconds_left > 1800:  # More than 30 minutes
                time_color = Colors.YELLOW
            else:
                time_color = Colors.RED

            # Format time string
            if hours_left and hours_left > 0:
                time_str = f"{hours_left}h {minutes_left}m"
            else:
                time_str = f"{minutes_left}m"

            # Format reset time
            reset_hm = next_reset.strftime("%H:%M") if next_reset else ""

            # Calculate usage percentage based on cost
            usage_pct = 0
            if usage_info:
                current_cost = usage_info.get('cost_usd', 0)
                if current_cost > 0:
                    usage_pct = int((current_cost / COST_LIMIT_PER_SESSION) * 100)
                    usage_pct = max(0, min(100, usage_pct))  # Clamp to 0-100%

            # Build session info with usage percentage
            if usage_pct > 0:
                session_info = f"⏱ {time_str} until reset at {reset_hm} ({usage_pct}%)"
            else:
                session_info = f"⏱ {time_str} until reset at {reset_hm}"

            parts.append(f"{time_color}{session_info}{Colors.RESET}")

    # Session timer from ccusage (prioritize over block_start)
    elif usage_info and usage_info.get('reset_time'):
        try:
            reset_time = datetime.fromisoformat(usage_info['reset_time'].replace('Z', '+00:00'))
            now = datetime.now(reset_time.tzinfo)
            remaining = reset_time - now

            if remaining.total_seconds() > 0:
                total_seconds = int(remaining.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60

                # Calculate session percentage
                session_pct = 0
                if usage_info.get('start_time'):
                    session_pct = calculate_session_percentage(
                        usage_info['start_time'],
                        usage_info['reset_time']
                    )

                # Color based on remaining percentage
                remaining_pct = 100 - session_pct
                if remaining_pct <= 10:
                    time_color = Colors.RED
                elif remaining_pct <= 25:
                    time_color = Colors.YELLOW
                else:
                    time_color = Colors.GREEN

                # Format time string
                if hours > 0:
                    time_str = f"{hours}h {minutes}m"
                else:
                    time_str = f"{minutes}m"

                # Format reset time
                reset_hm = reset_time.strftime("%H:%M")

                # Build session info
                session_info = f"⏱ {time_str} until reset at {reset_hm} ({session_pct}%)"

                # Add progress bar
                progress = format_progress_bar(session_pct, 10)

                parts.append(f"{time_color}{session_info} {progress}{Colors.RESET}")
        except Exception:
            # Fallback to block_start if ccusage parsing fails
            if block_start:
                hours_left, minutes_left, seconds_left = format_time_remaining(block_start)
                if seconds_left and seconds_left > 0:
                    if seconds_left > 3600:
                        time_color = Colors.GREEN
                    elif seconds_left > 1800:
                        time_color = Colors.YELLOW
                    else:
                        time_color = Colors.RED

                    if hours_left and hours_left > 0:
                        time_str = f"{hours_left}h {minutes_left}m"
                    else:
                        time_str = f"{minutes_left}m"

                    parts.append(f"{time_color}⏳ {time_str}{Colors.RESET}")
    elif block_start:
        # Fallback to original block_start countdown
        hours_left, minutes_left, seconds_left = format_time_remaining(block_start)
        if seconds_left and seconds_left > 0:
            if seconds_left > 3600:
                time_color = Colors.GREEN
            elif seconds_left > 1800:
                time_color = Colors.YELLOW
            else:
                time_color = Colors.RED

            if hours_left and hours_left > 0:
                time_str = f"{hours_left}h {minutes_left}m"
            else:
                time_str = f"{minutes_left}m"

            parts.append(f"{time_color}⏳ {time_str}{Colors.RESET}")

    # Usage stats from ccusage
    if usage_info:
        # Requests/entries count
        entries = usage_info.get('entries', 0)
        if entries > 0:
            parts.append(f"{Colors.BLUE}💬 {entries} requests{Colors.RESET}")

        # Tokens used
        total_tokens = usage_info.get('total_tokens', 0)
        if total_tokens > 0:
            tokens_str = f"{total_tokens:,}"
            tokens_per_min = usage_info.get('tokens_per_minute', 0)
            if tokens_per_min > 0:
                parts.append(f"{Colors.PURPLE}📊 {tokens_str} tok ({tokens_per_min:.0f} tpm){Colors.RESET}")
            else:
                parts.append(f"{Colors.PURPLE}📊 {tokens_str} tok{Colors.RESET}")

        # Cost
        cost_usd = usage_info.get('cost_usd', 0)
        if cost_usd > 0:
            parts.append(f"{Colors.YELLOW}💵 ${cost_usd:.2f}{Colors.RESET}")

    # Context window percentage
    if context_length > 0:
        if context_percentage < 50:
            color = Colors.GREEN
        elif context_percentage < 80:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        parts.append(f"{color}📈 {context_percentage:.1f}%{Colors.RESET}")

    # Code stats
    if lines_added > 0 or lines_removed > 0:
        parts.append(f"{Colors.GREEN}+{lines_added}{Colors.RESET} {Colors.RED}-{lines_removed}{Colors.RESET}")

    # Join with separator
    separator = f" {Colors.GRAY}│{Colors.RESET} "
    output = separator.join(parts)

    print(output, flush=True)

except Exception as e:
    # Fallback to simple display
    print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}", file=sys.stderr)
    sys.exit(1)
