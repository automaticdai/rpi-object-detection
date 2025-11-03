#!/bin/bash
# ------------------------------------------------------------------------------
# Quick Start Script for Navigation System
# ------------------------------------------------------------------------------

echo "=================================================="
echo "Navigation System for Visually Impaired Users"
echo "=================================================="
echo ""

# Check if espeak is installed
if ! command -v espeak &> /dev/null && ! command -v espeak-ng &> /dev/null; then
    echo "⚠️  Warning: espeak/espeak-ng not found!"
    echo "   Audio announcements will not work."
    echo ""
    echo "   Install with:"
    echo "   - Arch Linux: sudo pacman -S espeak-ng"
    echo "   - Debian/Ubuntu: sudo apt-get install espeak-ng"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check camera
echo "Checking camera availability..."
if [ ! -e /dev/video0 ]; then
    echo "⚠️  Warning: No camera found at /dev/video0"
    echo "   You may need to specify a different camera with --camera N"
    echo ""
fi

echo ""
echo "Starting navigation system..."
echo "Press Ctrl+C to stop"
echo ""
echo "Controls:"
echo "  q or ESC - Quit"
echo "  m        - Toggle mute/unmute"
echo ""

# Set PYTHONPATH and run
export PYTHONPATH=/home/shanu/Projects/Python/rpi-object-detection
uv run python -m src.navigation.navigation_system "$@"
