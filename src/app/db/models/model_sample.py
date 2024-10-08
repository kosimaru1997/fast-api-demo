from typing import Optional, List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship
from sqlmodel import SQLModel, Field, Relationship

from src.app.db.database import Base


class User(SQLModel, AsyncAttrs, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=100, unique=True, index=True)
    hashed_password: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    added_column: str = Field(default="default_value", max_length=255)

    items: List["ItemSecond"] = Relationship(back_populates="owner")


class Item(SQLModel, AsyncAttrs, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=100, index=True)
    description: str = Field(max_length=255, index=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")
    add_column_test: str = Field(default="default_value", max_length=255)

    owner: Optional[User] = Relationship(back_populates="items")
