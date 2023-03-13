



server {
    listen 8435 ssl default_server;
    server_name api.collection.dortzio.com;
    client_max_body_size 2G;

    location / {
        proxy_pass http://localhost:3435;
    }

    location /media {
        autoindex on;
        alias /root/dortzio/market/media/;
    }

    location /static {
        autoindex on;
        alias /root/dortzio/market/static/;
    }

}
