import logging

from scrapy import Spider
from sqlalchemy.exc import NoResultFound

from wenku8.items import BookItem, CoverItem, ChapterItem
from wenku8.models import *
from sqlmodel import select
class BookPipeline:
    def open_spider(self, spider: Spider):
        self.log = spider.log
        self.session = Session(engine)

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        """
        处理抓取到的项目。

        如果项目是 BookItem 的实例，则执行以下操作：
        1. 检查书籍标题是否为 None，如果是，则记录警告并返回 None。
        2. 遍历书籍标签列表，对于每个标签，尝试查询数据库。
        如果标签不存在，则创建新标签并保存到数据库。
        3. 使用项目数据和处理后的标签创建 Book 实例，并保存到数据库。
        4. 记录书籍已成功保存的信息。

        参数:
            item: 抓取到的项目，预期为 BookItem 的实例。
            spider: 抓取该项目的爬虫，本方法中未使用该参数。

        返回值:
            返回处理后的项目。
        """
        if isinstance(item, BookItem):
            # 检查书籍标题是否存在
            if item['title'] is None:
                self.log(f"id {item['id']} 不存在！", logging.WARNING)
                return None

            # 初始化标签列表
            tags = [None for _ in range(len(item['tags']))]

            # 遍历标签，检查或创建标签
            for index, tag in enumerate(item['tags']):
                try:
                    result = self.session.exec(select(Tag).where(Tag.name == tag)).one()
                except NoResultFound:
                    self.log(f"标签 {tag} 未找到，创建新标签", logging.WARNING)
                    result = Tag(name=tag)
                    self.session.add(result)
                    self.session.commit()
                    self.session.refresh(result)
                tags[index] = result

            # 创建书籍对象并保存到数据库
            item['tags'] = tags
            book = Book(**item)
            self.session.add(book)
            self.session.commit()
            self.log(f"《{item['title']}》 成功保存", logging.INFO)

        return item


class CoverPipeline:
    def open_spider(self, spider):
        self.log = spider.log
        self.session = Session(engine)

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        """
        处理爬取的项目。

        该方法会在每个由爬虫抓取的项目上调用。它检查项目是否是 CoverItem 的实例，
        如果是，则尝试将其添加到数据库中。

        参数:
        - item: 抓取的项目，可能是 CoverItem 的实例。
        - spider: 抓取该项目的爬虫，用于日志记录。

        返回值:
        - item: 返回原始项目，未做任何修改。
        """
        # 检查项目是否为 CoverItem 实例
        if isinstance(item, CoverItem):
            # 根据项目创建 Cover 对象
            cover = Cover(id=item["id"], content=item['content'])
            try:
                # 将 Cover 对象添加到会话并提交到数据库
                self.session.add(cover)
                self.session.commit()
                # 记录成功保存的日志信息
                self.log(f"{item['id']} 封面成功保存", logging.INFO)
            except Exception as e:
                # 如果发生异常，记录保存失败的日志警告
                self.log(f"{item['id']} 封面保存失败", logging.WARNING)
        # 返回处理后的项目
        return item


class ChapterPipeline:
    def open_spider(self, spider):
        self.log = spider.log
        self.session = Session(engine)

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        if isinstance(item, ChapterItem):
            chapter = Chapter(**item)
            self.session.add(chapter)
            self.session.commit()
            self.log(f"章节{item['id']} 成功存入", logging.INFO)
        return item