#!/usr/bin/env bash
set -ex

# Go to repo root
cd /opt/render/project/src

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install Chromium for Playwright
python -m playwright install chromium
