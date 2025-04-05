#!/bin/bash

# === CONFIGURABLE VARIABLES ===
DB_NAME="google_news"
DB_USER="postgres"
DB_PASSWORD="1234"
DB_PORT="5432"
APP_DIR="/home/ubuntu/google_news_copy/google_new_scripts"
SCRAPER_SERVICE="/etc/systemd/system/scraper.service"
FLASK_SERVICE="/etc/systemd/system/flaskapi.service"
DOMAIN="heyheynews.work.gd"  # Replace with your actual domain
EMAIL="abhishek791996@gmail.com"      # Replace with a valid email
APP_MODULE="run:app"         # Adjust if your Flask app uses a different name

# === UPDATE SYSTEM ===
echo "🔄 Updating system..."
sudo apt update -y
sudo apt upgrade -y
sudo apt install -y postgresql postgresql-contrib python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# === SET UP POSTGRESQL DATABASE IF NEEDED ===
echo "🗄️  Setting up PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

sudo -u postgres psql <<EOF
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME') THEN
      CREATE DATABASE $DB_NAME;
   END IF;

   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
      CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';
   END IF;

   GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
END
\$\$;
EOF

# === SET UP PYTHON ENVIRONMENT ===
echo "🐍 Setting up Python virtual environment..."
cd "$APP_DIR"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# === SCRAPER SYSTEMD SERVICE ===
echo "⚙️ Creating scraper systemd service..."
sudo tee "$SCRAPER_SERVICE" > /dev/null <<EOF
[Unit]
Description=Run Python Scraper
After=network.target postgresql.service

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/run.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# === FLASK API SYSTEMD SERVICE ===
echo "⚙️ Creating Flask API systemd service..."
sudo tee "$FLASK_SERVICE" > /dev/null <<EOF
[Unit]
Description=Gunicorn Flask API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 $APP_MODULE
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# === ENABLE AND START SERVICES ===
echo "🚀 Enabling and starting systemd services..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable scraper.service flaskapi.service
sudo systemctl restart scraper.service flaskapi.service

# === NGINX CONFIGURATION ===
echo "🌐 Configuring Nginx for $DOMAIN..."
NGINX_CONF="/etc/nginx/sites-available/$DOMAIN"

sudo tee "$NGINX_CONF" > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# === LET'S ENCRYPT SSL ===
echo "🔐 Setting up HTTPS with Let's Encrypt..."
sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL" || echo "⚠️ Certbot failed. You may need to check domain DNS settings."

echo "✅ Deployment complete!"
echo "Flask API: https://$DOMAIN"
