





server {
    root /home/dortzio/build;
    index index.html; index.htm;
    server_name dortzio.com www.dortzio.com;
    location / {
        try_files $uri $uri/ index.html;
    }


    listen [::]:443 ssl ipv6only=on; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/dortzio.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/dortzio.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot


}








server {
    if ($host = www.dortzio.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    if ($host = dortzio.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


	listen 80 default_server;
	listen [::]:80 default_server;

	server_name dortzio.com www.dortzio.com;
    return 404; # managed by Certbot




}