from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLAEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database.db import Base
from database.enums import UserGroupEnum, GenderEnum


class UserGroup(Base):
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(SQLAEnum(UserGroupEnum), unique=True, nullable=False)

    users = relationship("User", back_populates="group")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    group_id = Column(Integer, ForeignKey("user_groups.id"), nullable=False)

    group = relationship("UserGroup", back_populates="users")
    profile = relationship("UserProfile", uselist=False, back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    gender = Column(SQLAEnum(GenderEnum), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    info = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")
