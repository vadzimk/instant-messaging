import jwt
import os
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from pathlib import Path
from passlib.context import CryptContext

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
        "exp": (now + timedelta(hours=24)).timestamp(),
        "scope": "openid"
    }
    private_key_path = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / 'jwt_keys/private_key.pem'
    private_key_text = private_key_path.read_text()
    private_key = serialization.load_pem_private_key(
        private_key_text.encode(encoding='utf-8'),  # utf-8 is default
        password=None
    )
    return jwt.encode(payload=payload, key=private_key, algorithm="RS256")
