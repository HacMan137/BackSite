#!/bin/sh
python3 -m backsite.db.management.initialize
python3 -m gunicorn -w 2 --threads 2 -b 0.0.0.0:80 'backsite.app:create_application()'