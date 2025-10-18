#!/usr/bin/env bash
set -ex

cd /opt/render/project/src

# Update & install dependencies required by Chromium
apt-get update
apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libdrm2 \
    libgbm1 \
    libasound2 \
    libxrandr2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxdamage1 \
    libxcomposite1 \
    libxext6 \
    libxfixes3 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgtk-3-0 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    libu2f-udev

# Upgrade pip
pip install --upgrade pip

# Install greenlet (must be compatible)
pip install greenlet==3.2.4

# Install all Python deps
pip install -r backend/requirements.txt

# Install Chromium for Playwright
python -m playwright install chromium
