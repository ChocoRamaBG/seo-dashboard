#!/usr/bin/env bash
set -ex

# Go to repo root
cd /opt/render/project/src

# Upgrade pip
pip install --upgrade pip

# Install greenlet compatible with Python 3.13 first
pip install greenlet==3.2.4

# Then install all other requirements but ignore greenlet
pip install --ignore-installed=greenlet -r backend/requirements.txt

# Install Chromium for Playwright
python -m playwright install chromium
