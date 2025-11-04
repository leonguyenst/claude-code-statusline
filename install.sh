#!/bin/bash
# Installation script for Claude Code Statusline (Linux/macOS)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
CLAUDE_DIR="$HOME/.claude"
STATUSLINE_PY="$CLAUDE_DIR/statusline.py"
SETTINGS_JSON="$CLAUDE_DIR/settings.json"

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Claude Code Statusline - Installation      ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# Check Python
echo -e "${YELLOW}[1/5]${NC} Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Found: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✓${NC} Found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python not found!"
    echo -e "${YELLOW}Please install Python 3.6+ and try again.${NC}"
    exit 1
fi

# Create .claude directory if not exists
echo -e "${YELLOW}[2/5]${NC} Creating .claude directory..."
mkdir -p "$CLAUDE_DIR"
echo -e "${GREEN}✓${NC} Directory ready: $CLAUDE_DIR"

# Copy statusline.py
echo -e "${YELLOW}[3/5]${NC} Installing statusline.py..."
if [ -f "$STATUSLINE_PY" ]; then
    echo -e "${YELLOW}⚠${NC} Existing statusline.py found. Creating backup..."
    cp "$STATUSLINE_PY" "$STATUSLINE_PY.backup.$(date +%Y%m%d_%H%M%S)"
fi
cp "statusline.py" "$STATUSLINE_PY"
chmod +x "$STATUSLINE_PY"
echo -e "${GREEN}✓${NC} Installed: $STATUSLINE_PY"

# Configure settings.json
echo -e "${YELLOW}[4/5]${NC} Configuring settings.json..."
if [ ! -f "$SETTINGS_JSON" ]; then
    # Create new settings.json
    cat > "$SETTINGS_JSON" << EOF
{
  "statusLine": {
    "type": "command",
    "command": "$PYTHON_CMD $STATUSLINE_PY"
  }
}
EOF
    echo -e "${GREEN}✓${NC} Created new settings.json"
else
    # Check if statusLine already configured
    if grep -q '"statusLine"' "$SETTINGS_JSON"; then
        echo -e "${YELLOW}⚠${NC} statusLine already configured in settings.json"
        echo -e "${YELLOW}  Please manually update if needed:${NC}"
        echo -e "${BLUE}  \"statusLine\": {${NC}"
        echo -e "${BLUE}    \"type\": \"command\",${NC}"
        echo -e "${BLUE}    \"command\": \"$PYTHON_CMD $STATUSLINE_PY\"${NC}"
        echo -e "${BLUE}  }${NC}"
    else
        # Add statusLine configuration
        # Create backup
        cp "$SETTINGS_JSON" "$SETTINGS_JSON.backup.$(date +%Y%m%d_%H%M%S)"

        # Use Python to add statusLine to existing JSON
        $PYTHON_CMD << EOF
import json
with open('$SETTINGS_JSON', 'r') as f:
    settings = json.load(f)
settings['statusLine'] = {
    'type': 'command',
    'command': '$PYTHON_CMD $STATUSLINE_PY'
}
with open('$SETTINGS_JSON', 'w') as f:
    json.dump(settings, f, indent=2)
EOF
        echo -e "${GREEN}✓${NC} Updated settings.json"
    fi
fi

# Test installation
echo -e "${YELLOW}[5/5]${NC} Testing installation..."
TEST_INPUT='{"model":{"display_name":"Test"},"workspace":{"current_dir":"."},"transcript_path":"","cost":{}}'
TEST_OUTPUT=$(echo "$TEST_INPUT" | $PYTHON_CMD "$STATUSLINE_PY" 2>&1)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Test passed!"
    echo -e "${BLUE}  Output:${NC} $TEST_OUTPUT"
else
    echo -e "${RED}✗${NC} Test failed!"
    echo -e "${RED}  Error:${NC} $TEST_OUTPUT"
    exit 1
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Installation Complete! ✓              ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Restart Claude Code to see your new statusline"
echo -e "  2. (Optional) Install ccusage for full features:"
echo -e "     ${YELLOW}npm install -g ccusage${NC}"
echo ""
echo -e "${GREEN}Happy coding with Claude! 🤖${NC}"
