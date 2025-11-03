PROJECT = web_dev
APP = app

VENV = venv

PROJECT_DIR = .
PROJECT_ENV = development


.PHONY: run clean

### Setup ###

virtualenv:
	python -m venv $(VENV)

activate_venv:
	$(VENV)\Scripts\activate

clean: # Remove cache and build files
	rm -rf __pycache__
	rm -rf coverage.xml
	rm -rf pytest.html
	rm -rf pytest.xml

clean_venv:
	rm -rf $(VENV)

requirements:
	pip install -r requirements.txt

pip_update:
	python -m pip install --upgrade pip


### Website ###

django_init:
	django-admin startproject ${PROJECT}

run:
	@python manage.py runserver

static:
	python manage.py collectstatic

### Tailwind ###
tailwind_init:
	npm install tailwindcss @tailwindcss/postcss postcss

build_style:
	npm run build

dev_style:
	npm run dev
