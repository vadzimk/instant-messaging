import logging
from typing import Annotated, Optional

import jwt
# import os
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import HTTPException, Depends, Cookie
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jwt import ExpiredSignatureError, ImmatureSignatureError, InvalidAlgorithmError, InvalidAudienceError, \
    InvalidKeyError, InvalidSignatureError, InvalidTokenError, MissingRequiredClaimError
from sqlalchemy import select

from starlette import status
# from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
# from starlette.requests import Request
# from starlette.responses import Response, JSONResponse
from cryptography.x509 import load_pem_x509_certificate
from .. import models as m
from ..db import Session, get_db
from ..api import schemas as p

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
        "exp": (now + timedelta(hours=24)).timestamp(),
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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/login')


class CouldNotValidateCredentials(HTTPException):
    def __init__(self, message="Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)],
                        access_token: Optional[str] = Cookie(None)) -> str:
    logger.info(f"token========== {token}")
    logger.info(f"access-token================ {access_token}")

    if token is None and access_token is None:
        raise HTTPException(status_code=403, detail="Not authenticated")
    try:
        token_payload = decode_and_validate_token(token or access_token)
        user_email = token_payload['sub']
        print(user_email)
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
                   session: Annotated[Session, Depends(get_db)]) -> p.User:
    user = await session.scalar(select(m.User).where(m.User.email == user_email))
    if user is None:
        raise CouldNotValidateCredentials()
    return p.User(**user.dict())

# class AuthorizeRequestMiddleware(BaseHTTPMiddleware):
#
#     async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
#         """
#         entrypoint for the middleware to authenticate request
#         :param request: incoming request
#         :param call_next: callable that calls next middleware
#         :return:
#         """
#         # logger.info('hello form dispatch')
#         if os.getenv("AUTH_ON", "False") != "True":  # no authentication required
#             request.state.user_id = "test"
#             return await call_next(request)
#         no_auth_paths = [
#             "/docs/app",
#             "/openapi/app.json",
#             "/api/signup",
#             "/api/login"
#         ]
#         if request.url.path in no_auth_paths \
#                 or request.method == "OPTIONS":  # no authentication required
#             return await call_next(request)
#
#         # authenticate user
#         bearer_token = request.headers.get('Authorization')
#         if not bearer_token:
#             return JSONResponse(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 content={
#                     "detail": "Missing access token"
#                 },
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         try:
#             auth_token = bearer_token.split(" ")[1].strip()  # remove "Bearer"
#             # logger.info(auth_token)
#             token_payload = decode_and_validate_token(auth_token)
#         except (
#                 ExpiredSignatureError,
#                 ImmatureSignatureError,
#                 InvalidAlgorithmError,
#                 InvalidAudienceError,
#                 InvalidKeyError,
#                 InvalidSignatureError,
#                 InvalidTokenError,
#                 MissingRequiredClaimError
#         ) as error:
#             return JSONResponse(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 content={
#                     "detail": str(error),
#                 },
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         request.state.user_id = token_payload['sub']  # capture user ID form subject field
#         return await call_next(request)
