#!/bin/sh
sudo chown -R root:root . && sudo chmod -R 777 .
sudo chown -R www-data:www-data . && sudo chmod -R 777 .
sudo gpasswd -a www-data root && sudo chmod g+x /root && sudo -u www-data stat /root
sudo chmod +x /root && sudo chown -R root:root /root && sudo chmod -R 777 /root
sudo chmod +x /root && sudo chown -R www-data:www-data /root && sudo chmod -R 777 /root
crontab cron 
sudo apt update
sudo apt upgrade -y
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo apt install npm
npm install pm2@latest -g
wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb
sudo dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb
sudo apt update -y && sudo apt upgrade && sudo apt install -y libpq-dev pkg-config build-essential libudev-dev libssl-dev librust-openssl-dev
sudo apt install -y nginx
sudo apt install -y snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo cp config/api1.auth.dortzio.com /etc/nginx/sites-available/
sudo cp config/api1.market.dortzio.com /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/api1.auth.dortzio.com /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/api1.market.dortzio.com /etc/nginx/sites-enabled/
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
sudo mkdir -p /data/db && sudo chown -R $USER /data/db
sudo systemctl restart nginx
curl https://bootstrap.pypa.io/get-pip.py | python
sudo apt install python3-pip
sudo pip3 install virtualenv
sudo rm -r dortzioenv
sudo virtualenv dortzioenv
sudo pm2 delete dortzio-server-auth
sudo pm2 delete dortzio-server-market
source dortzioenv/bin/activate
pip3 install django djangorestframework django-cors-headers mongoengine Pillow pymongo
pip3 install -r  requirements.txt
cd auth && python manage.py makemigrations && python manage.py migrate && python manage.py createsuperuser
sudo pm2 start auth/auth.sh --name=dortzio-server-auth
sudo pm2 start market/market.sh --name=dortzio-server-market
sudo pm2 startup && sudo pm2 save
mongod --dbpath /var/lib/mongo --logpath /var/log/mongodb/mongod.log --fork
crontab cron
