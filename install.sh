#!/bin/bash

echo "Update packages"
sudo apt-get update

echo "Installing libopencv-dev and libatlas-base-dev..."
sudo apt-get install -y libopencv-dev libatlas-base-dev

if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Installing pip3..."
    sudo apt-get install -y python3-pip
fi

echo "Installing virtualenv, Pillow, numpy, scipy, matplotlib..."
pip3 install virtualenv Pillow numpy scipy matplotlib

echo "Installing opencv-python e opencv-contrib-python..."
pip3 install opencv-python opencv-contrib-python

echo "Installation of dependencies completed!"