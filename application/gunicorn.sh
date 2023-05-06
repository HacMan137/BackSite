#!/bin/sh
python3 -m gunicorn --chdir app app:app -w 2 --threads 2 -b 0.0.0.0:80