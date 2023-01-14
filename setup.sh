#!/bin/sh
sudo crontab -e
crontab cron 
sudo apt update
sudo apt upgrade -y
curl https://bootstrap.pypa.io/get-pip.py | python
sudo pip3 install virtualenv
sudo rm -r dortzio
sudo virtualenv dortzio
sudo pm2 delete dortzio-server-auth
sudo pm2 delete dortzio-server-market
source dortzio/bin/activate
pip install -r requirements.txt
cd auth && python manage.py makemigrations && python manage.py migrate
cd .. && 
sudo pm2 start auth/auth.sh --name=dortzio-server-auth
sudo pm2 start market/market.sh --name=dortzio-server-market
