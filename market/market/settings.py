"""
Django settings for market project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import mongoengine 
import os 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_URL = 'mongodb://localhost:27017/'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-e8-85)41xw6w&j1&24v)s_&jgh^xro%04ke$0mxnvrk_uzsk(b'


SERVER_PUBLIC_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
SERVER_PRIVATE_KEY = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
MARKET_CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
RPC_ENDPOINT = "http://localhost:8545"
CONTRACT_ABI = "/root/NFTMarketplace-Frontend/artifacts/contracts/Market.sol/NFTMarketplace.json"


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['localhost', '127.0.0.1']
ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'collection',
    'corsheaders',
    'rest_framework',
]


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'market.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'market.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# mongoengine.connect(host="mongodb://127.0.0.1:27017/dortzio_nft_marketplace")
mongoengine.connect(db="dortziomarket", 
                    username="doadmin", 
                    password="y0RxL681P9a352bt", 
                    authentication_source="admin", 
                    host="mongodb+srv://dortziodb-4992b220.mongo.ondigitalocean.com")

# mongoengine.connect(db="dortziomarket", 
#                     username="root", 
#                     password="56WxG17jyBFg2WChfD7whOfkUOP6bC10", 
#                     host="homa.ir.fing.ir",
#                     port=32130)
# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/home/dortzio/NFTMarketplace-Backend/market/media/"



USER_VERIFY='http://localhost:3434/auth/user/verify/'
USER_SEARCH='http://localhost:3434/auth/user/search/'
NFT_EDIT='http://localhost:3435/market/nft/edit/'
NFT_OFFERS='http://localhost:3435/market/nft/offers/'
NFT_ACTIVE_AUCTION='http://localhost:3435/market/nft/auc/active/'
CANCEL_USER_OFFER='http://localhost:3434/auth/user/offer/cancel/'
NFTS_ACTIVE_AUCTION='http://localhost:3435/market/nft/auc/active/all/'
CHECK_AUCTION='http://localhost:3435/market/nft/auc/check/'
COLLECTION_EDIT='http://localhost:3435/market/collection/edit/'
ADD_USER_OFFER='http://localhost:3434/auth/user/add/offer/'
GET_OFFER_COL_MS='http://localhost:3435/market/nft/get/offer/'
USER_NOT_OFFER='http://localhost:3434/auth/user/not/offer/'
NFT_DISABLE_OFFER='http://localhost:3435/market/nft/dis/offer/'
NFT_EDIT_OFFER='http://localhost:3435/market/nft/edit/offer/'
UPDATE_OFFER_STATUS='http://localhost:3434/auth/user/edit/offer/'
USER_EDIT_OFFER='http://localhost:3434/auth/user/stat/offer/'
GET_ALL_GENERATIVE_COLLECTION='http://localhost:3435/market/collection/gen/all/'
ALL_UNREVEALED_GENERATIVE_COLLECTION='http://localhost:3435/market/collection/gen/all/unrev/'
ASSIGN_METADATA='http://localhost:3435/market/collection/gen/asgn/meta/'
GET_GENERATIVE_COLLECTION_METADATA='http://localhost:3435/market/collection/gen/get/meta/'
GET_GENERATIVE_COLLECTION_MINTED_NFT='http://localhost:3435/market/collection/gen/get/mint/'
GET_COLLECTION_MINTED_NFT='http://localhost:3435/market/collection/get/mint/'
GET_NFT_ACTIVE_AUCTION_WAITING_BIDS='http://localhost:3435/market/nft/auc/active/bids/wait/'
GET_NFT_ACTIVE_AUCTION_BIDS='http://localhost:3435/market/nft/auc/active/bids/'
ACTIVE_AUCTION_WAITING_BIDS_MAX_PRICE='http://localhost:3435/market/nft/auc/active/bids/max/'
ACCEPT_ACTIVE_AUCTION_BID='http://localhost:3435/market/nft/auc/active/bids/acc/'
ACTIVE_AUCTION_DECLINE_BIDS = 'http://localhost:3435/market/nft/auc/active/bids/dec/'
DELETE_DB_KEY = '+Dez&]P<66/$@=&L>A.gxF=wz}54M1'
