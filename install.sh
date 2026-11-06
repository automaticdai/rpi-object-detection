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

echo "Installing system dependencies (libopencv-dev, python3-venv, python3-pip)..."
sudo apt-get install -y libopencv-dev python3-venv python3-pip

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

if is_raspberry_pi; then
    # The default PyPI torch wheels for aarch64 pull in several GB of CUDA
    # packages, which are useless on a Raspberry Pi. Install the CPU-only
    # build first so that ultralytics reuses it.
    echo "Installing CPU-only PyTorch ..."
    ./venv/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
fi

echo "Installing Python dependencies from requirements.txt ..."
./venv/bin/pip install -r requirements.txt

# Ultralytics depends on opencv-python, which installs into the same cv2/
# folder as opencv-contrib-python. Whichever is installed last wins, and with
# OpenCV 5 only the contrib build has CascadeClassifier (face detection).
# Remove opencv-python and reinstall the contrib build so that it owns cv2/.
# ("pip check" will then report that ultralytics requires opencv-python; this
# is expected, as ultralytics only imports cv2.)
echo "Making sure cv2 comes from opencv-contrib-python ..."
./venv/bin/pip uninstall -y opencv-python
OPENCV_VERSION=$(./venv/bin/pip show opencv-contrib-python | sed -n 's/^Version: //p')
./venv/bin/pip install --force-reinstall --no-deps "opencv-contrib-python==${OPENCV_VERSION}"

echo ""
echo "Installation complete."
echo ""
echo "To activate the virtual environment in your shell, run:"
echo "    source venv/bin/activate"
