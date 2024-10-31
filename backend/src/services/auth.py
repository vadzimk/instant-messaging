import logging
import jwt
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from pathlib import Path
from passlib.context import CryptContext

from cryptography.x509 import load_pem_x509_certificate

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def generate_jwt(data):
    now = datetime.utcnow()
    payload = {
        "iss": "https://messaging.vadzimk.com",
        "sub": data.get('sub'),
        "aud": "http://127.0.0.1:8000/",
        "iat": now.timestamp(),
        "exp": (now + timedelta(days=30)).timestamp(),
        "scope": "openid"
    }
    private_key_path = Path(__file__).parent.parent.parent / 'jwt_keys/private_key.pem'
    private_key_text = private_key_path.read_text()
    private_key = serialization.load_pem_private_key(
        private_key_text.encode(encoding='utf-8'),  # utf-8 is default
        password=None
    )
    return jwt.encode(payload=payload, key=private_key, algorithm="RS256")


public_key_text = (Path(__file__).parent.parent.parent / "jwt_keys/public_key.pem").read_text()
public_key = load_pem_x509_certificate(public_key_text.encode()).public_key()


def decode_and_validate_token(access_token: str) -> dict:
    """
    validate access_token and return payload
    :param access_token:
    :return: payload i.e. dict containing decoded jwt claims, if token is valid
    """
    return jwt.decode(
        access_token,
        key=public_key,
        algorithms=["RS256"],
        audience=["http://127.0.0.1:8000/"]
    )
