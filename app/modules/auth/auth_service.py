from jose import JWTError, jwt
from passlib.context import CryptContext
import datetime
from datetime import datetime, timedelta, timezone

from os import environ as env

from app.models import User
from starlette.responses import JSONResponse, Response

secret_key = env.get("JWT_SECRET_KEY", default="secret-key")
token_expire_min = int(env.get("JWT_EXPIRE_MIN", default="30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_create(password: str) -> str:
  return pwd_context.hash(password)


def hash_verify(password: str, hash: str) -> bool:
  return pwd_context.verify(password, hash)


def create_access_token(data: dict, expires_delta: timedelta):
  """Create a JWT access token"""
  to_encode = data.copy()
  expire = datetime.now(timezone.utc) + expires_delta
  
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
  return encoded_jwt


def verify_token(token: str, credentials_exception):
  """Verify and decode a JWT token"""
  try:
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    username = payload.get("sub")
    if username is None:
      raise credentials_exception
    token_data = {"username": username}
    return token_data
  except JWTError:
    raise credentials_exception 


def authenticate(user: User) -> Response:
  access_token_expires = timedelta(minutes=token_expire_min)
  access_token = create_access_token(
    data={"sub": user.email}, 
    expires_delta=access_token_expires
  )

  response = JSONResponse({
    access_token: access_token,
  })

  response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    max_age=60 * token_expire_min,
    expires=60 * token_expire_min,
  )

  return response


