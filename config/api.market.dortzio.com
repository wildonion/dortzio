



server {
    listen 8435 ssl default_server;
    server_name api.collection.dortzio.com;
    client_max_body_size 2G;

    location / {
        proxy_pass http://localhost:3435;
    }

    location /media {
        autoindex off;
        alias /home/dortzio/market/media/;
    }

    location /static {
        alias /home/dortzio/market/static/;
    }


    # listen [::]:443 ssl; # managed by Certbot
    # listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/api.collection.dortzio.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/api.collection.dortzio.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}
