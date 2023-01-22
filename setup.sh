#!/bin/sh
sudo chown -R root:root . && sudo chmod -R 777 .
crontab cron 
sudo apt update
sudo apt upgrade -y
curl https://bootstrap.pypa.io/get-pip.py | python
sudo apt install python3-pip
sudo pip3 install virtualenv
sudo rm -r dortzioenv
sudo virtualenv dortzioenv
sudo pm2 delete dortzio-server-auth
sudo pm2 delete dortzio-server-market
source dortzioenv/bin/activate
pip install -r requirements.txt
cd auth && python manage.py makemigrations && python manage.py migrate
cd .. && 
sudo pm2 start auth/auth.sh --name=dortzio-server-auth
sudo pm2 start market/market.sh --name=dortzio-server-market
