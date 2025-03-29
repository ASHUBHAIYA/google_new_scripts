#!/bin/bash

# Variables
DB_NAME="google_news"
DB_USER="postgres"
DB_PASSWORD="1234"
DB_PORT="5432"
APP_DIR="/home/ubuntu/google_news_copy/google_new_scripts/"
SERVICE_FILE="/etc/systemd/system/scraper.service"

# Update system and install dependencies
sudo apt update -y
sudo apt upgrade -y
sudo apt install -y postgresql postgresql-contrib python3 python3-pip python3-venv git

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

# Set up Python virtual environment
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create systemd service for the scraper
echo "[Unit]
Description=Run Python Scraper
After=network.target postgresql.service

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/run.py
Restart=always

[Install]
WantedBy=multi-user.target
" | sudo tee $SERVICE_FILE

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable and start the scraper service
sudo systemctl enable scraper.service
sudo systemctl start scraper.service

echo "Deployment complete. The scraper will run automatically on reboot."
