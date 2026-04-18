#!/bin/bash
# ------------------------------------------------------------------------------
# rpi-object-detection: install script
#
# Creates a Python virtual environment in ./venv and installs the dependencies
# listed in requirements.txt.
#
# On Raspberry Pi, the venv is created with --system-site-packages so that
# libcamera and picamera2 (installed in the system Python by Raspberry Pi OS)
# remain accessible from inside the venv.
# ------------------------------------------------------------------------------
set -e

echo "Welcome to Raspberry Pi Real-Time Object Detection and Tracking"
echo "For more information: https://github.com/automaticdai/rpi-object-detection"

is_raspberry_pi() {
    grep -qE "Raspberry|BCM" /proc/cpuinfo
}

echo "Updating package list..."
sudo apt-get update

echo "Installing system dependencies (libopencv-dev, libatlas-base-dev, python3-venv, python3-pip)..."
sudo apt-get install -y libopencv-dev libatlas-base-dev python3-venv python3-pip

if is_raspberry_pi; then
    echo "Raspberry Pi detected."
    VENV_ARGS="--system-site-packages"
else
    echo "Non-Raspberry Pi system detected."
    VENV_ARGS=""
fi

if [ ! -d venv ]; then
    echo "Creating virtual environment in ./venv ..."
    python3 -m venv ${VENV_ARGS} venv
else
    echo "Virtual environment ./venv already exists — reusing it."
fi

echo "Upgrading pip tooling..."
./venv/bin/pip install --upgrade pip setuptools wheel

echo "Installing Python dependencies from requirements.txt ..."
./venv/bin/pip install -r requirements.txt

echo ""
echo "Installation complete."
echo ""
echo "To activate the virtual environment in your shell, run:"
echo "    source venv/bin/activate"
