
> © API Design and Code Credit Goes To [o-O-MidNight-O-o](https://github.com/o-O-MidNight-O-o). The extended parts by me are mentioned in the code.

> Also for the front-end code please contact [Narniii](https://github.com/Narniii).

# 📙 About

* For smart contracts please refer to the [smarties](https://github.com/wildonion/smarties) repo.

* This server consists of two main microservices, namely `auth` and `market`.

* Since this project is microservice based, each of this microservices occupies a unique port.

* `auth` and `market` can send HTTP requests to each other in order to fetch needed data from each other.

* Three bash files have been provided for this project, two for each mentioned microservices and one for running all of other bash files.

* Database engine for the django admin is `sqlite3`

* In this branch all communications between clients and server are based on HTTP protocol with mongodb as the data storage model. 

* We can't use websocket for realtime streaming like updating NFT events or activity since we must get those info from on-chain or the smart contract and there is no way to communicate with smart contract in realtime using websocket unless we use some kinda interval logic or third party library like moralis sync APIs which must be done from the front-end. The other reason of ignoring websocket is the performence issue.

* This marketplace supports both simple and generative NFT minting which is known by the minting and revealing calender feature.

* Front-end must call `end_auction` API if the NFT owner wants to cancel the **ACTIVE** auction on an NFT; Also front-end must call the contract method too.

* The DB schema is as follow

<p align="center">
    <img src="https://github.com/wildonion/dortzio/blob/main/models/schemas.PNG">
</p>

# ☣️ Usage and Stup

> Remember to 

* Use the `root` user for all setups since this project assumes that you are completely a root :)

* See the postman collection documents for the latest schema of the DB

* Get any image from the server in front-end like `https://api.market.dortzio.com:8435/media/<image_name.jpg>`

* Front-end must only use the image name from the fetched image using the server means it should uses the `<image_name.jpg>` in a url like: `/root/dortzio/market/media/<image_name.jpg>` 

* Add the VPS domain or IP to `ALLOWED_HOST` in `settings.py`

* Run `setup.sh` on Linux Only. 

* set `Debug` variable inside `settings.py` files to `False` in production.

* add the domain name or the host inside `ALLOWED_HOSTS`.

* setup a domain name before using certbot. 

* cd to `auth` then create `dev` and `dortzio` superuser:
    - ```python manage.py makemigrations```
    - ```python manage.py migrate```
    - ```python manage.py createsuperuser```

* ```sudo chmod +x setup.sh && sudo bash setup.sh```

* ```sudo certbot --nginx```

* In VPS make a new line in `cron` file then in this directory run ```crontab cron``` 

# 🍟 WIP Features

* reserve for specific buyer

* NFT bundle sell

* search bug

* check offer api and crontab

* Notification APIs

* Handle NFT copy on the contract side  

* Graphql supports for live streaming

* Elasticsearch and Docker setups
