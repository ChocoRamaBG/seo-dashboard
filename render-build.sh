#!/usr/bin/env bash
set -ex

# Go to repo root
cd /opt/render/project/src

# Upgrade pip
pip install --upgrade pip

# Install latest greenlet compatible with Python 3.13
pip install greenlet==3.2.4

# Install all other dependencies
pip install -r backend/requirements.txt

# Install Chromium for Playwright
python -m playwright install chromium
