#!/bin/bash
# Deploy Shadow Guide to VPS

echo "🖤 Deploying Shadow Guide..."
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart shadowguide
echo "✅ Deployment complete."