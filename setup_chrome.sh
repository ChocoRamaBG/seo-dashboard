#!/usr/bin/env bash
set -ex

# create chrome folder
mkdir -p /tmp/chrome
cd /tmp/chrome

# lightweight version of Chrome for testing
wget -O chrome-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.84/linux64/chrome-linux64.zip
unzip chrome-linux64.zip

wget -O chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.84/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip

# export vars
export GOOGLE_CHROME_BIN="/tmp/chrome/chrome-linux64/chrome"
export CHROMEDRIVER_PATH="/tmp/chrome/chromedriver-linux64/chromedriver"

# lighter Python deps
pip install --upgrade pip
pip install --no-cache-dir fastapi uvicorn selenium beautifulsoup4
