import logging
from typing import Annotated
import jwt
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jwt import (ExpiredSignatureError, ImmatureSignatureError, InvalidAlgorithmError, InvalidAudienceError,
                 InvalidKeyError, InvalidSignatureError, InvalidTokenError, MissingRequiredClaimError)
from sqlalchemy import select
from starlette import status
from cryptography.x509 import load_pem_x509_certificate
from src import schemas as p

from src.db import models as m
from src.db.base import Session, get_db
from src.exceptions import CouldNotValidateCredentials

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
    private_key_path = Path(__file__).parent.parent.parent.parent / 'jwt_keys/private_key.pem'
    private_key_text = private_key_path.read_text()
    private_key = serialization.load_pem_private_key(
        private_key_text.encode(encoding='utf-8'),  # utf-8 is default
        password=None
    )
    return jwt.encode(payload=payload, key=private_key, algorithm="RS256")


public_key_text = (Path(__file__).parent.parent.parent.parent / "jwt_keys/public_key.pem").read_text()
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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/users/login')


def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    if token is None:
        raise HTTPException(status_code=403, detail="Not authenticated")
    try:
        token_payload = decode_and_validate_token(token)
        user_email = token_payload['sub']
    except (
            ExpiredSignatureError,
            ImmatureSignatureError,
            InvalidAlgorithmError,
            InvalidAudienceError,
            InvalidKeyError,
            InvalidSignatureError,
            InvalidTokenError,
            MissingRequiredClaimError,
    ) as error:
        raise CouldNotValidateCredentials(message=str(error))
    if user_email is None:
        raise CouldNotValidateCredentials()
    return user_email


async def get_user(user_email: Annotated[str, Depends(get_current_user_id)],
                   session: Annotated[Session, Depends(get_db)]) -> p.GetUserSchema:
    user = await session.scalar(select(m.User).where(m.User.email == user_email))
    if user is None:
        raise CouldNotValidateCredentials()
    return p.GetUserSchema(**user.dict())
