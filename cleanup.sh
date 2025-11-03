#!/bin/bash

# Cleanup script 

echo "=========================================="
echo "Cleanup Script for rpi-object-detection"
echo "=========================================="
echo ""
echo "This will remove:"
echo "  - Python virtual environment (.venv/)"
echo "  - Downloaded YOLO models (*.pt files)"
echo "  - UV cache (optional)"
echo ""

# Check if .venv exists
if [ -d ".venv" ]; then
    read -p "Remove .venv directory? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing .venv directory..."
        rm -rf .venv
        echo "✓ Virtual environment removed"
    else
        echo "Skipped .venv removal"
    fi
else
    echo "No .venv directory found"
fi

# Check for YOLO model files
if ls *.pt 1> /dev/null 2>&1; then
    read -p "Remove downloaded YOLO models (*.pt)? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing YOLO model files..."
        rm -f *.pt
        echo "✓ YOLO models removed"
    else
        echo "Skipped YOLO model removal"
    fi
else
    echo "No YOLO model files found"
fi

# Check for __pycache__ directories
if find . -type d -name "__pycache__" 2>/dev/null | grep -q .; then
    read -p "Remove Python cache (__pycache__)? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing __pycache__ directories..."
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
        echo "✓ Python cache removed"
    else
        echo "Skipped cache removal"
    fi
fi

# Optional: UV cache cleanup
echo ""
read -p "Clear UV cache? (this affects all UV projects) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Clearing UV cache..."
    uv cache clean
    echo "✓ UV cache cleared"
else
    echo "Skipped UV cache cleanup"
fi

echo ""
echo "=========================================="
echo "Cleanup complete!"
echo "=========================================="
echo ""
echo "To reinstall everything, run:"
echo "  uv venv"
echo "  uv pip install -r requirements.txt"
echo ""
