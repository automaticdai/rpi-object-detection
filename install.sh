#!/bin/bash

is_raspberry_pi() {
    if grep -q "Raspberry" /proc/cpuinfo || grep -q "BCM" /proc/cpuinfo; then
        return 0  # Is raspberry Pi
    else
        return 1
    fi
}

if is_raspberry_pi; then
    echo "Raspberry Pi detected. Running Raspberry-specific script..."

    echo "Update packages"
    sudo apt-get update

    echo "Installing libopencv-dev and libatlas-base-dev..."
    sudo apt-get install -y libopencv-dev libatlas-base-dev

    if ! command -v pip3 &> /dev/null; then
        echo "pip3 not found. Installing pip3..."
        sudo apt-get install -y python3-pip
    fi

    echo "Installing Pillow, numpy, scipy, matplotlib..."
    pip3 install Pillow numpy scipy matplotlib

    echo "Installing opencv-python and opencv-contrib-python..."
    pip3 install opencv-python opencv-contrib-python

    echo "Installation of dependencies completed for Raspberry Pi!"

else
    echo "Non-Raspberry Pi system detected. Running standard script..."

    echo "Updating package list..."
    sudo apt-get update

    echo "Installing libopencv-dev and libatlas-base-dev..."
    sudo apt-get install -y libopencv-dev libatlas-base-dev

    if ! command -v pip3 &> /dev/null; then
        echo "pip3 not found. Installing pip3..."
        sudo apt-get install -y python3-pip
    fi

    if ! command -v virtualenv &> /dev/null; then
        echo "virtualenv not found. Installing virtualenv..."
        pip3 install virtualenv
    fi

    echo "Creating a virtual environment..."
    virtualenv venv

    echo "Activating virtual environment..."
    source venv/bin/activate

    echo "Installing dependencies: Pillow, numpy, scipy, matplotlib, opencv-python, and opencv-contrib-python..."
    pip install Pillow numpy scipy matplotlib opencv-python opencv-contrib-python

    if [ -f requirements.txt ]; then
        echo "Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
    else
        echo "requirements.txt not found. Skipping installation from requirements file."
    fi

    echo "Installation of dependencies completed for non-Raspberry Pi system!"
fi