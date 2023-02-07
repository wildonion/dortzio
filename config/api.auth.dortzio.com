




server {
    listen 8434 ssl default_server;
    server_name api.auth.dortzio.com;
    client_max_body_size 2G;

    location / {
        proxy_pass http://localhost:3434;
    }

    location /media {
        autoindex off;
        alias /home/wildonion/dortzio/auth/media/;
    }

    location /static {
        alias /home/wildonion/dortzio/auth/static/;
    }

    # listen [::]:443 ssl; # managed by Certbot
    # listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/api.auth.dortzio.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/api.auth.dortzio.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}