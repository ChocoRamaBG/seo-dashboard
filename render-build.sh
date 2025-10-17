#!/usr/bin/env bash
set -ex

cd /opt/render/project/src

# Upgrade pip
pip install --upgrade pip

# Install compatible greenlet first
pip install greenlet==3.2.4

# Then install everything else
pip install --ignore-installed -r backend/requirements.txt

# Install Chromium for Playwright
python -m playwright install chromium
