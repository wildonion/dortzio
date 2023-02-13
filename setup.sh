#!/bin/sh
sudo chown -R root:root . && sudo chmod -R 777 .
sudo chmod +x /root && sudo chown -R root:root /root && sudo chmod -R 777 /root
crontab cron 
sudo apt update
sudo apt upgrade -y
curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt-get install -y nodejs
npm install pm2@latest -g
sudo apt install -y nginx
sudo apt install -y snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo cp config/api.auth.dortzio.com /etc/nginx/sites-available/
sudo cp config/api.market.dortzio.com /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/api.auth.dortzio.com /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/api.market.dortzio.com /etc/nginx/sites-enabled/
echo "[?] SSL APIs? (you must have a registered domain)"
read SSLAnswer
if [[ $SSLAnswer == "yes" ]]; then
    sudo certbot --nginx
else
    echo "continue without SSL"
fi
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
sudo apt-get install gnupg
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update -y && sudo apt-get install -y mongodb-org
sudo mkdir -p /data/db && sudo chown -R $USER /data/db && sudo systemctl restart nginx
curl https://bootstrap.pypa.io/get-pip.py | python
sudo apt install python3-pip
sudo pip3 install virtualenv
sudo rm -r dortzioenv
sudo virtualenv dortzioenv
sudo pm2 delete dortzio-server-auth
sudo pm2 delete dortzio-server-market
source dortzioenv/bin/activate
pip install django djangorestframework django-cors-headers mongoengine Pillow pymongo
pip install -r  requirements.txt
cd auth && python manage.py makemigrations && python manage.py migrate && python manage.py createsuperuser
sudo pm2 start auth/auth.sh --name=dortzio-server-auth
sudo pm2 start market/market.sh --name=dortzio-server-market
