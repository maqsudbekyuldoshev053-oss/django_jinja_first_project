mig:
	python manage.py makemigrations

up:
	python manage.py migrate

user:
	python manage.py createsuperuser

apps:
	python manage.py startapp apps

celery:
	celery -A root worker -l INFO
