#!/usr/bin/env bash
# install chromium and chromedriver locally inside your repo
mkdir -p /tmp/chrome
cd /tmp/chrome

# download Chromium
wget https://commondatastorage.googleapis.com/chromium-browser-snapshots/Linux_x64/1161234/chrome-linux.zip
unzip chrome-linux.zip
CHROME_BIN=$(pwd)/chrome-linux/chrome

# download matching chromedriver
wget https://chromedriver.storage.googleapis.com/116.0.5845.96/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
CHROMEDRIVER_BIN=$(pwd)/chromedriver

# export env vars for your app
export GOOGLE_CHROME_BIN="$CHROME_BIN"
export CHROMEDRIVER_PATH="$CHROMEDRIVER_BIN"

# install python deps
pip install -r backend/requirements.txt
