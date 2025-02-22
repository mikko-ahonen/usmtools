rm compliances/migrations/*.py stats/migrations/*.py projects/migrations/*.py workflows/migrations/*.py mir/migrations/*.py
python manage.py makemigrations workflows projects compliances mir stats
