from scrapy import spiders, Request

class CoverSpider(spiders.Spider):
    name="cover"
    custom_settings = {
        "ITEM_PIPELINES": {
            "wenku8.pipelines.CoverPipeline": 300,
        }
    }
    def start_requests(self):
        for id in get_cover_id():
            prefix = int(id)//1000
            yield Request(
                url=f"http://img.wenku8.com/image/{prefix}/{id}/{id}s.jpg",
                callback=self.download_cover,
                errback=self.handle_404,
                meta={"id": id},
            )

    def download_cover(self, response):
        from wenku8.items import CoverItem
        yield CoverItem(
            id=response.meta["id"],
            content=response.body,
        )
    
    def handle_404(self, failure):
        """
        处理404错误。
    
        当请求的页面不存在时，执行此函数以更新数据库中的书籍封面状态。
    
        参数:
        - failure: 包含请求失败信息的对象，用于访问失败请求的相关数据。
    
        返回值:
        无返回值。
        """
        if failure.value.response.status != 404:
            return None
        # 导入必要的模块和类
        from wenku8.models import Book, engine
        from sqlmodel import Session, select
        # 创建数据库会话
        with Session(engine) as session:
            # 构建查询语句，根据请求中的id查找书籍
            statement = select(Book).where(Book.id == failure.request.meta["id"])
            
            # 执行查询并获取唯一结果
            book = session.exec(statement).one()
            
            # 更新书籍的封面状态为False
            book.has_cover = False
            
            # 将更新后的书籍对象添加到会话中
            session.add(book)
            
            # 提交会话以持久化更改
            session.commit()
            self.log(f"《{book.title}》不存在可用封面")
def get_cover_id():
    from wenku8.models import Cover, Book, engine
    from sqlmodel import Session, select
    with Session(engine) as session:
        statement = select(Book.id).where(Book.has_cover == True)
        book_ids = session.exec(statement).all()
        
        statement = select(Cover.id).where(Cover.id.not_in(book_ids))
        return session.exec(statement).all()