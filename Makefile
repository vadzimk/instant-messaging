docker.up.dev:
	docker-compose -f docker-compose.dev.yml up -d

backend.test:
	@cd backend \
	&& pipenv run python -m pytest -vv -s