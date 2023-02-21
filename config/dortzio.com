





server {
    root /home/dortzio/build;
    index index.html; index.htm;
    server_name dortzio.com www.dortzio.com;
    location / {
        try_files $uri /index.html;
    }
}
