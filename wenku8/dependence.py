from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, SQLModel, select

from wenku8.models import engine, Book, Text, Cover


def __get_max_id(model: SQLModel):
    with Session(engine) as session:
        try:
            statement = select(model)
            results = session.exec(statement).all()
            max_id = max(results, key=lambda x: x.query_id).query_id if results else 0
        except NoResultFound:
            max_id = 0
        return max_id


def get_max_id_of_cover():
    return __get_max_id(Cover)


def get_max_id_of_text():
    return __get_max_id(Text)


def get_max_id_of_book():
    return __get_max_id(Book)
