from wenku8.models import engine
from sqlmodel import Session, select, SQLModel


def get_max_id_of(table: SQLModel):
    with Session(engine) as session:
        statement = select(table.id).order_by(table.id.desc()).limit(1)
        result = session.exec(statement)
        return result.one_or_none()
