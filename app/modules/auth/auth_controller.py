from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute, Route
from sqlalchemy.exc import IntegrityError

from app.state import AppState
from app.models import User
from .auth_models import UserCreate, UserLogin

from jose import JWTError, jwt
from passlib.context import CryptContext
import datetime
from datetime import datetime, timedelta, timezone

from os import environ as env

secret_key = env.get("JWT_SECRET_KEY", default="secret-key")
token_expire_min = int(env.get("JWT_EXPIRE_MIN", default="30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


async def handle_register(request: Request) -> Response:
  state = AppState.get(request)
  with state.get_db() as db:
    try:
      payload = await request.json()
      user_create = UserCreate(**payload)
      password_hash = pwd_context.hash(user_create.password)
      user_db = User(
        email=user_create.email,
        password_hash=password_hash,
      )

      db.add(user_db)
      db.commit()
      db.refresh(user_db)

      return authenticate(user_db)
    except ValueError as e:
      return Response(str(e), status_code=400)
    except IntegrityError:
      db.rollback()
      return Response("Username or email already registered", status_code=400)


async def handle_login(request: Request) -> Response:
  state = AppState.get(request)
  with state.get_db() as db:
    try:
      payload = await request.json()
      user_login = UserLogin(**payload)

      user = db.query(User).filter(
        (User.email == user_login.email)
      ).first()

      if user is None:
        return Response("Invalid credentials", status_code=401)

      if not pwd_context.verify(user_login.password, str(user.password_hash)):
        return Response("Invalid credentials", status_code=401)

      return authenticate(user)

    except ValueError as e:
      return Response(str(e), status_code=400)


routes: list[BaseRoute] = [
  Route("/register", handle_register),
  Route("/login", handle_login),
]
