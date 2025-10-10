#!/usr/bin/env bash

# update apt and install chromium + chromedriver
sudo apt-get update
sudo apt-get install -y chromium chromium-driver unzip

# set env vars for undetected_chromedriver
export GOOGLE_CHROME_BIN=/usr/bin/chromium
export CHROMEDRIVER_PATH=/usr/bin/chromedriver

# install python deps (make sure the path exists)
pip install -r backend/requirements.txt
