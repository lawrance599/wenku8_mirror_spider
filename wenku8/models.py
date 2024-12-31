from typing import Optional

from sqlalchemy import LargeBinary
from sqlmodel import SQLModel, create_engine, Field, Relationship


class BookTagLink(SQLModel, table=True):
    book_pk: Optional[int] = Field(default=None, foreign_key="book.id", primary_key=True)
    tag_pk: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    query_id: Optional[int] = Field(default=None, index=True, unique=True)
    title: Optional[str] = Field(default=None, unique=True)
    writer: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    last_chapter: Optional[str] = Field(default=None)
    last_updated: Optional[str] = Field(default=None)
    words: Optional[int] = Field(default=0)
    status: Optional[str] = Field(default=None)
    tags: list["Tag"] = Relationship(back_populates="books", link_model=BookTagLink)


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    books: list[Book] = Relationship(back_populates="tags", link_model=BookTagLink)


class Cover(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    query_id: Optional[int] = Field(default=None, index=True, unique=True)
    content: bytes = Field(default=None, sa_type=LargeBinary(2048))


class Text(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    query_id: Optional[int] = Field(default=None, index=True, unique=True)
    content: bytes = Field(default=None, sa_type=LargeBinary(65536))


__engine_url = None  # todo
if __engine_url is None:
    raise Exception("Please imply the engine url, which is a must to save data"
                    " u can look for https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls "
                    "or https://docs.sqlalchemy.org.cn/en/20/core/engines.html#backend-specific-urls for the chinese translation")
engine = create_engine(__engine_url)
SQLModel.metadata.create_all(engine)
