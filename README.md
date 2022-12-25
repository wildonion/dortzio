
> © API Design and Code Credit Goes To [o-O-MidNight-O-o](https://github.com/o-O-MidNight-O-o). The extended parts by me are mentioned in the code.

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

# ☣️ Production Usage

> Remember to set `Debug` variable inside `settings.py` files to `False` in production.

> Remember to add the domain name or the host inside `ALLOWED_HOSTS`.

```sudo chmod +x setup.sh && sudo bash setup.sh```

# 📟 Development Setup

> Run `setup.sh` on Linux Only.

> Also Install mongodb before going any further.

* ```sudo npm install pm2 -g```

* ```curl https://bootstrap.pypa.io/get-pip.py | python```

* ```pip install --upgrade virtualenv```

* ```virtualenv dortzioenv```

* ```dortzioenv\Scripts\activate```

* ```pip install -r requirements.txt```

* cd to `auth` then create `dev` and `dortzio` superuser:
    - ```python manage.py makemigrations```
    - ```python manage.py migrate```
    - ```python manage.py createsuperuser```

# 📌 WIP

* nft trait percentage in `NFT.get` method

* `get_trendings` API

* Eth smart contracts in [smarties](https://github.com/wildonion/smarties) repo

* `check_auction` API

* Shopping Basket APIs

* postman collection

* crontab setup to end auction on behalf of the creator

* cluster docker containers using k8s

* secure mongodb with username and password 

* reverse proxy
