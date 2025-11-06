PY ?= python
MANAGE := $(PY) manage.py

.PHONY: run migrate makemigrations superuser schema-json schema-yaml test

run:
	$(MANAGE) runserver

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

superuser:
	$(MANAGE) createsuperuser

schema-json:
	$(MANAGE) spectacular --file schema.json --format openapi-json

schema-yaml:
	$(MANAGE) spectacular --file schema.yaml --format openapi

test:
	$(MANAGE) test -v 2
