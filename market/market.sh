#!/bin/sh
source /$USER/dortzio/dortzioenv/bin/activate 
cd /$USER/dortzio/market
python manage.py runserver 0.0.0.0:3435
