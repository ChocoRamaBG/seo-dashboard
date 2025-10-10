#!/usr/bin/env bash
set -e  # stop if any command fails

# Install Chrome + Chromedriver
apt-get update
apt-get install -y chromium chromium-driver

# Just to confirm paths
which chromium || echo "Chromium not found!"
which chromedriver || echo "Chromedriver not found!"

# Install Python dependencies
pip install -r backend/requirements.txt
