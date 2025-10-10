#!/usr/bin/env bash
set -o errexit

echo "🚀 Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "🧠 Installing Chromium & Chromedriver manually..."
mkdir -p /opt/render/project/chrome
cd /opt/render/project/chrome

wget https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.84/linux64/chrome-linux64.zip
wget https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.84/linux64/chromedriver-linux64.zip

unzip chrome-linux64.zip
unzip chromedriver-linux64.zip

mv chrome-linux64 /opt/render/project/chrome/chrome
mv chromedriver-linux64/chromedriver /opt/render/project/chrome/chromedriver

chmod +x /opt/render/project/chrome/chromedriver

echo "✅ Chromium setup done!"
