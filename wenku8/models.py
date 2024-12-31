from typing import Optional

from sqlmodel import SQLModel, create_engine, Field, Relationship
from sqlalchemy import Text as TextType
class BookTagLink(SQLModel, table=True):
    book_pk: Optional[int] = Field(default=None, foreign_key="book.id", primary_key=True)
    tag_pk: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    query_id: Optional[int] = Field(default=None, index=True)
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
    id: Optional[int] = Field(default=None, primary_key=True, foreign_key="book.query_id")
    content: bytes = Field(default=None)
class Text(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, foreign_key="book.query_id")
    content: bytes = Field(default=None, sa_type=TextType)
__engine_url = r"mysql+pymysql://yixin:13767631251Fan!@122.51.138.48:3306/wenku8"
engine = create_engine(__engine_url)
SQLModel.metadata.create_all(engine)
