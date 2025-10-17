#!/usr/bin/env bash
set -ex

# Go to repo root
cd /opt/render/project/src

# Upgrade pip
pip install --upgrade pip

# Force install greenlet first to avoid build issues
pip install greenlet==3.3.3

# Install all other dependencies
pip install -r backend/requirements.txt

# Install Chromium for Playwright
python -m playwright install chromium
