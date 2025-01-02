from typing import Optional

from sqlalchemy import LargeBinary
from sqlmodel import SQLModel, create_engine, Field, Relationship, Session, select


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
    content: bytes = Field(default=None, sa_type=LargeBinary(16777216))


__engine_url = None
if __engine_url is None:
    raise Exception("Please imply the engine url, which is a must to save data"
                    " u can look for https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls "
                    "or https://docs.sqlalchemy.org.cn/en/20/core/engines.html#backend-specific-urls for the chinese translation")
engine = create_engine(__engine_url)
SQLModel.metadata.create_all(engine)


def get_miss_on_query_id_of(model: SQLModel):
    with Session(engine) as session:
        cover_ids = session.exec(select(model.query_id)).all()
        book_ids = session.exec(select(Book.query_id).where(Book.words != 0)).all()
        for book_id in book_ids:
            if book_id not in cover_ids:
                yield book_id

def get_max_query_id_of(model: SQLModel):
    with Session(engine) as session:
        query_ids = session.exec(select(model.query_id)).all()
        return max(query_ids)