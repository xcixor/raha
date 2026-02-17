ci-test:
	docker-compose up -d
	docker-compose exec -T web PYTHONPATH=. DJANGO_SETTINGS_MODULE=config.settings python3 manage.py test apps.accounts.tests apps.models_app.tests
	docker-compose down
