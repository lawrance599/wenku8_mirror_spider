import logging

from scrapy import Spider
from sqlalchemy.exc import NoResultFound
from sqlmodel import select, Session

from wenku8.items import BookItem
from wenku8.models import *


class Database:
    def open_spider(self, spider: Spider):
        self.log = spider.log
        self.session = Session(engine)

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            if item['title'] is None:
                self.log(f"query_id {item['query_id']} did not exists!", logging.WARNING)
                return None
            tags = [None for _ in range(len(item['tags']))]
            for index, tag in enumerate(item['tags']):
                try:
                    result = self.session.exec(select(Tag).where(Tag.name == tag)).one()
                except NoResultFound:
                    self.log(f"Tag {tag} not found, make a new one", logging.WARNING)
                    result = Tag(name=tag)
                    self.session.add(result)
                    self.session.commit()
                    self.session.refresh(result)
                tags[index] = result
            book = Book(
                query_id=item['query_id'],
                title=item['title'],
                writer=item['writer'],
                description=item['description'],
                download_url=item['download_url'],
                last_chapter=item['last_chapter'],
                last_updated=item['last_updated'],
                words=item['words'],
                status=item['status'],
                tags=tags,
            )
            self.session.add(book)
            self.session.commit()
            self.log(f"Book {item['title']} successfully saved", logging.INFO)
