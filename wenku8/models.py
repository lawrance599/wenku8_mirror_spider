from typing import Optional
from datetime import date
from dotenv import load_dotenv
from sqlalchemy import LargeBinary, text
from sqlmodel import SQLModel, create_engine, Field, Relationship, Session, Column, TEXT
from os import getenv
load_dotenv(".env")


class BookTagLink(SQLModel, table=True):
    book_pk: Optional[int] = Field(
        default=None, foreign_key="book.id", primary_key=True
    )
    tag_pk: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = Field(default=None, unique=True)
    writer: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None, max_length=1024)
    last_updated: Optional[date] = Field(default=None)
    words: Optional[int] = Field(default=0)
    status: Optional[str] = Field(default=None)
    tags: list["Tag"] = Relationship(back_populates="books", link_model=BookTagLink)
    has_cover: Optional[bool] = Field(default=True)


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    books: list[Book] = Relationship(back_populates="tags", link_model=BookTagLink)


class Cover(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, foreign_key="book.id")
    content: bytes = Field(default=None, sa_type=LargeBinary(2048))


class Chapter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: Optional[int] = Field(default=None, foreign_key="book.id")
    title: Optional[str] = Field(default=None)
    serial: Optional[int] = Field(default=None)
    content: Optional[str] = Field(default=None, sa_column=Column(TEXT(300000)))


__engine_url = getenv("database_url".upper(), None)
if __engine_url is None:
    raise Exception(
        "imply .env file with database_url to use database or change the settings.py to prevent using database"
        "more info about database_url  please look for https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls "
        "or https://docs.sqlalchemy.org.cn/en/20/core/engines.html#backend-specific-urls for the chinese translation"
    )
engine = create_engine(__engine_url)
SQLModel.metadata.create_all(engine)


# 创建一些必要的视图
def create_chapters_view():
    with Session(engine) as session:
        statement = """
CREATE VIEW IF NOT EXISTS chapters AS
SELECT
    book_id AS id,
    COUNT(*) as chapters
FROM
    chapter
GROUP BY
    book_id
ORDER BY
    book_id;
        """
    session.exec(text(statement))
    session.commit()


def add_fulltext_index():
    check_index_query = """
    SELECT COUNT(1) IndexIsThere FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE table_schema=DATABASE() AND table_name='book' AND index_name='idx_fulltext';
    """
    create_index_query = """
    CREATE FULLTEXT INDEX idx_fulltext
    ON book (title, writer, description) 
    WITH PARSER ngram;
    """
    with Session(engine) as session:
        result = session.exec(text(check_index_query)).one()
        if result.IndexIsThere == 0:
            session.exec(text(create_index_query))
            session.commit()


# add_fulltext_index()
create_chapters_view()
