# Django Cours

Objectifs : écosystème Python & Django, environnement isolé, projet pro, ORM, migrations, Admin, DBeaver.

## Démarrage rapide
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "Django>=4.2,<6"
django-admin startproject config .
python manage.py migrate
python manage.py runserver
