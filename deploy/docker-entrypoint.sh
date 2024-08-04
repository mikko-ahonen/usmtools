#!/bin/bash

cd /src
source /src/.env-local

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Start server
python manage.py runserver 0.0.0.0:8000
