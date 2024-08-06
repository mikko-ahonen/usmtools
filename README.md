# Running in local container

docker compose --project-directory dev up

docker compose --project-directory dev run -it web /bin/bash

# Generating the db structure for certain compliance domain

python manage.py xref --domain=iso27001 --tenant=9e3e5587-bbc1-4848-9b2d-e827431d4455 --update-structure
