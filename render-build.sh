#!/usr/bin/env bash
set -o errexit

# install Chrome and chromedriver
apt-get update && apt-get install -y chromium chromium-driver

# install python deps
pip install -r backend/requirements.txt
