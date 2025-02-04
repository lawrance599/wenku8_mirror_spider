from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import LargeBinary
from sqlmodel import SQLModel, create_engine, Field, Relationship, Session, select

load_dotenv(".env")
from os import getenv

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

class Chapter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: Optional[int] = Field(default=None, foreign_key="book.id")
    title: Optional[str] = Field(default=None)
    serial: Optional[int] = Field(default=None)
    content: bytes = Field(default=None, sa_type=LargeBinary(16777216))

__engine_url = getenv("database_url".upper(), None)
if __engine_url is None:
    raise Exception("imply .env file with database_url to use database or change the settings.py to prevent using database"
                    "more info about database_url  please look for https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls "
                    "or https://docs.sqlalchemy.org.cn/en/20/core/engines.html#backend-specific-urls for the chinese translation")
engine = create_engine(__engine_url)
SQLModel.metadata.create_all(engine)


def get_miss_on_query_id_of(model: SQLModel):
    """
    获取未在指定模型中查询到的书籍ID。

    此函数用于比较两种查询结果：指定模型中的query_id和Book表中words不为0的记录的query_id。
    它会找出在Book表中存在但不在指定模型中出现的query_id，并将其生成并返回。

    参数:
    - model: SQLModel, 用于指定要进行查询对比的模型类。

    返回:
    - 生成器，产生未在指定模型中查询到的书籍ID。
    """
    # 创建数据库会话
    with Session(engine) as session:
        # 查询指定模型中的所有query_id
        cover_ids = session.exec(select(model.query_id)).all()
        # 查询Book表中words不为0的所有query_id
        book_ids = session.exec(select(Book.query_id).where(Book.words != 0)).all()
        # 遍历Book表中的每个query_id
        for book_id in book_ids:
            # 如果当前query_id不在指定模型的query_id列表中，则生成
            if book_id not in cover_ids:
                yield book_id

from sqlalchemy import select, func

def get_max_query_id_of(model: SQLModel):
    """
    获取指定模型的最大查询ID。

    该函数通过查询数据库中的所有查询ID，并返回其中的最大值，用于在不执行新查询的情况下，
    确定某个模型的最大查询ID。这对于优化查询性能和避免不必要的数据库访问非常有用。

    参数:
    - model: SQLModel 类的一个实例，表示要查询的数据库模型。

    返回:
    - int: 模型表中的最大查询ID。
    """
    # 创建一个数据库会话，用于执行查询操作。
    with Session(engine) as session:
        # 使用数据库的 MAX 函数直接计算最大 query_id
        max_query_id = session.scalar(select(func.max(model.query_id)))
        # 如果查询结果为空，返回 0
        return max_query_id if max_query_id is not None else 0