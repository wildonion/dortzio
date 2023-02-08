




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
    
}
