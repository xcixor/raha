ci-test:
	docker-compose up -d
	docker-compose exec -T -e PYTHONPATH=. -e DJANGO_SETTINGS_MODULE=config.settings web python3 manage.py test apps.accounts apps.models_app
	docker-compose down
