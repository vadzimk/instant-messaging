docker.up.dev:
	docker-compose -f docker-compose.dev.yml up -d

backend.test:
	pipenv run python -m pytest -vv -s

backend.dev:
	ENV=development pipenv run uvicorn src.main:app --reload

# generate public private key pair
jwt.keys:
	mkdir -p jwt_keys \
	&& openssl req -x509 -nodes -newkey rsa:2048 -keyout jwt_keys/private_key.pem \
	-out jwt_keys/public_key.pem \
    -days 365 \
    -subj "/CN=messaging.vadzimk.com"

# pre-commit is running at ../.git/hooks/pre-commit
# will not allow commit if tests inside /backend did not pass
