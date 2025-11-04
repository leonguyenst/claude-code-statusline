# Claude Code Statusline

Enhanced statusline for Claude Code with fixed cycle times and cost-based usage tracking.

## Features

- **Fixed Cycle Times**: Support for custom reset cycles (6h, 11h, 16h, 21h)
- **Cost-Based Usage Tracking**: Display usage percentage based on Claude Pro plan limits ($5 per 5 hours)
- **Multi-Platform Support**: Works on Windows with fnm node manager
- **Configurable**: Easy to toggle between calculation methods

## Installation

```bash
# Run the installation script
./install.bat
```

## Configuration

Edit `statusline.py` to customize:

```python
# Toggle between fixed cycles (6h,11h,16h,21h) or standard 5-hour blocks
USE_FIXED_CYCLES = True

# Adjust cost limit based on your plan
COST_LIMIT_PER_SESSION = 5.0  # $5 per 5 hours for Claude Pro
```

## Display Format

```
🤖 Sonnet 4.5 │ ⏱ 1h 35m until reset at 21:00 (64%) │ 💵 $3.22
```

- Time remaining until next reset
- Usage percentage based on cost
- Current session cost

## Requirements

- Python 3.6+
- Claude Code CLI
- `ccusage` command available

## License

MIT
