#!/bin/sh
echo "Initializing DB..."
python3 -m backsite.db.management.initialize
echo "Starting Application"
python3 -m gunicorn -w 2 --threads 2 -b 0.0.0.0:80 'backsite.app:create_application()'