#!/usr/bin/env bash
set -ex

# Create a folder for Chrome + driver
mkdir -p /tmp/chrome
cd /tmp/chrome

# Download Chrome
wget -O chrome-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.84/linux64/chrome-linux64.zip
unzip chrome-linux64.zip

# Download ChromeDriver
wget -O chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.84/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip

# Export env vars
export GOOGLE_CHROME_BIN="/tmp/chrome/chrome-linux64/chrome"
export CHROMEDRIVER_PATH="/tmp/chrome/chromedriver-linux64/chromedriver"  # <-- FIXED

# Go back to repo root before installing deps
cd /opt/render/project/src

# Install python deps
pip install --upgrade pip
pip install -r backend/requirements.txt
