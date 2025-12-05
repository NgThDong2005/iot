from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
	pass


class User(Base):
	"""User model for authentication"""

	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String(100), unique=True, index=True, nullable=False)
	password_hash = Column(String(255), nullable=False)
	created_at = Column(DateTime(timezone=True), server_default=func.now())
	is_active = Column(Boolean, default=True)
