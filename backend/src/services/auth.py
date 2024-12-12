import logging
import os
from typing import Tuple

import jwt
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from passlib.context import CryptContext
from cryptography.x509 import load_pem_x509_certificate
from src.settings import server_settings
from src import exceptions as e

from src.logger import logger

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
DEV_KEYS_DIR = Path(__file__).parent.parent.parent / 'jwt_keys'


def hash_password(password: str):
    """Hashes the provided password."""
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """Verifies the plain password against the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def load_keys() -> Tuple[RSAPublicKey, RSAPrivateKey]:
    """
    Loads RSA public and private keys from environment or files.
    @return: (public_key, private_key)
    """
    if os.getenv('ENV') == 'development':
        private_key_path = DEV_KEYS_DIR / 'private_key.pem'
        private_key_text = private_key_path.read_text()
        public_key_path = DEV_KEYS_DIR / "public_key.pem"
        public_key_text = public_key_path.read_text()
    else:
        private_key_text = server_settings.JWT_PRIVATE_KEY
        public_key_text = server_settings.JWT_PUBLIC_KEY
    private_key = serialization.load_pem_private_key(
        private_key_text.encode(encoding='utf-8'),  # utf-8 is default
        password=None
    )
    public_key = load_pem_x509_certificate(public_key_text.encode()).public_key()
    return public_key, private_key


public_key, private_key = load_keys()


def generate_jwt(data: dict) -> str:
    """ Generates a JWT token with the provided data. """
    if not data.get('sub'):
        raise e.CouldNotValidateCredentials('The "sub" claim must be provided in the data')

    now = datetime.utcnow()
    payload = {
        "iss": server_settings.JWT_ISSUER,
        "sub": data.get('sub'),
        "aud": server_settings.JWT_AUDIENCE,
        "iat": now.timestamp(),
        "exp": (now + timedelta(days=30)).timestamp(),
        "scope": server_settings.JWT_SCOPE
    }
    try:
        token = jwt.encode(payload=payload, key=private_key, algorithm="RS256")
        return token
    except Exception as err:
        logger.error(f"Error generating JWT: {err}")
        raise


def decode_and_validate_token(access_token: str) -> dict:
    """
    Decodes and validates the JWT token.
    Returns the payload if the token is valid.
    :param access_token:
    :return: payload i.e. dict containing decoded jwt claims, if token is valid
    """
    try:
        payload = jwt.decode(
            access_token,
            key=public_key,
            algorithms=["RS256"],
            audience=[server_settings.JWT_AUDIENCE]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise e.CouldNotValidateCredentials('Token expired')
    except jwt.InvalidTokenError:
        raise e.CouldNotValidateCredentials('Invalid token')
