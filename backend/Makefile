# generate public private key pair
jwt.keys:
	mkdir -p jwt_keys \
	&& openssl req -x509 -nodes -newkey rsa:2048 -keyout jwt_keys/private_key.pem \
	-out jwt_keys/public_key.pem \
    -days 365 \
    -subj "/CN=messaging.vadzimk.com"

# pre-commit is running at ../.git/hooks/pre-commit
# will not allow commit if tests inside /backend did not pass


docker.up.dev:
	docker-compose -f docker-compose.dev.yml up -d

backend.test:
	ENV=development pipenv run pytest -vv -s

backend.coverage:
	ENV=development pipenv run pytest -v --cov=src --cov-report=term-missing

backend.coverage.report:
	coverage report --show-missing

backend.dev:
	ENV=development pipenv run uvicorn src.main:app --reload

celery.start:
	celery -A src.celery_app.worker.celery worker --loglevel=info
