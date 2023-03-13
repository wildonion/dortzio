#!/bin/sh
source /home/$USER/dortzio/dortzioenv/bin/activate 
cd /home/$USER/dortzio/auth
python manage.py runserver 0.0.0.0:3434
