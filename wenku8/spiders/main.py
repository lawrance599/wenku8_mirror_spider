import scrapy
from wenku8.models import Book, engine, Chapter, Cover
from sqlmodel import Session, select, and_
from datetime import date, timedelta
from wenku8.util import get_max_id_of
from os import getenv
from typing import List
from wenku8.items import BookItem, ChapterItem, CoverItem
from re import search

class Task:
    def __init__(self,id, url, cb):
        self.id = id
        self.url = url
        self.cb = cb
        
class MainSpider(scrapy.Spider):
    name = "main"
    COLLECT_LIMIT= 10 #每次开启向后爬取的次数
    # 更新日期的区间(天)，只爬取上次更新位于600-180之前的书
    UPDATE_DAYS_INTERVAL = (400,180) 
    
    custom_settings = {
        "ITEM_PIPELINES": {
            "wenku8.pipelines.BookPipeline": 100,
            "wenku8.pipelines.CoverPipeline": 200,
            "wenku8.pipelines.ChapterPipeline": 300,
        },
    }
    def start_requests(self):
        username, password = getenv("WENKU8USER").split(":")
        print(f"登录用户 {username}, 密码 {password}")
        yield scrapy.FormRequest(
            url="https://www.wenku8.net/login.php?do=submit",
            formdata={
                "username": username,
                "password": password,
                "usecookie":"315360000",
                "action": "login",
                "submit": " 登  录 "
            },
            callback=self.distribute_requests
        )
    
    def distribute_requests(self, response):
        # 更新已经存入数据库的书
        update_stat = select(Book.id).where(
            and_(
                Book.last_updated <= date.today() - timedelta(self.UPDATE_DAYS_INTERVAL[1]),
                Book.last_updated >= date.today() - timedelta(self.UPDATE_DAYS_INTERVAL[0]),
                Book.status == "连载中"
            )
        )
        # 新书爬取
        start_id= get_max_id_of(Book)+1 or 1
        self.log(f"新增任务将从{start_id}开始", 20)
        with Session(engine) as session:
            # 更新书籍的Task创建
            update_ids = session.exec(update_stat).all()
            update_urls = map(lambda x: f"https://www.wenku8.net/modules/article/packshow.php?id={x}&type=txt", update_ids)
            update_tasks = list(map(lambda x: Task(id=x[0],url=x[1], cb=self.parse_chapters), zip(update_ids, update_urls)))
            
            # 新增书籍的Task创建
            new_ids = range(start_id, start_id + self.COLLECT_LIMIT)
            new_urls = map(lambda x: f"https://www.wenku8.net/book/{x}.htm", new_ids)
            new_tasks: List[Task] = list(map(lambda x: Task(id=x[0],url=x[1], cb=self.parse_main), zip(new_ids, new_urls)))
            
            self.log(f"将要更新{len(update_tasks)}本书", level=20)
            self.log(f"将要新增{len(new_tasks)}本书", level=20)
            for task in update_tasks + new_tasks:
                yield scrapy.Request(url=task.url, callback=task.cb, meta={"id": task.id})
            
            
    def parse_main(self, response):
        """
        处理书籍主页面，这通常只来自新书
        传递新书的基本信息，下载新书封面，传递新书的章节下载页面的链接
        """
        id = response.meta["id"]
        # 原始数据的提取
        title = response.css("td td b").get() or None
        writer = response.css("#content > div > table tr+ tr td:nth-child(2)::text").get()
        status = response.css("#content > div > table tr+ tr td:nth-child(3)::text").get()
        last_updated = response.css("#content > div > table tr+ tr td:nth-child(4)::text").get()
        words = response.css("#content > div > table tr+ tr td:nth-child(5)::text").get()
        description = response.css("#content > div > table tr+ tr td:nth-child(6)::text").get()
        tags: str = response.css(".hottext:nth-child(1) b::text").get()
        if title is None:
            self.log(f"<{id}> 未搜索到基本信息", level=30)
            return
        # 传递新书信息
        self.log(f"<{id}> 信息已经提取", level=20)
        yield BookItem(
            id=id,
            title=title,
            writer=writer[5:],
            status=status[5:],
            last_updated=last_updated[5:],
            words=int(words[5:]),
            description=description,
            tags=list(tags[7].split(","))
        )
        
        # 下载封面
        img_url = response.css("div+ table img::attr(src)").get() or None
        if img_url is not None:
            yield scrapy.Request(
                url=img_url,
                callback=self.download_cover,
                meta={"id": id}
            )
        else:
            self.log(f"<{id}> 未搜索到封面链接", 20)
            
            
        chapter_page_url = response.xpath("//div[@id='content']//div[6]//div[1]/a/@href").get()
        if chapter_page_url is not None: 
            yield scrapy.Request(
                url=chapter_page_url,
                callback=self.parse_chapters,
                meta={"id": id}
            )
        else:
            self.log(f"<{id}> 未搜索到章节下载页面链接", 20)
    def parse_chapters(self, response):
        """
        处理章节页面，传递章节下载链接
        """
        book_id = response.meta["id"]
        titles = response.xpath("//td[@class='odd']/text()").getall()
        chapter_urls = response.xpath("//td[@class='even'][1]/a[2]/@href").getall()
        
        if chapter_urls is None:
            self.log(f"<{book_id}> 未搜索到章节下载链接", 30)
            return
        
        # 从章节下载链接中提取章节的id
        def extract_cid(url):
            pattern = r"https://dl.wenku8.com/packtxt.php\?aid=\d+&vid=(\d+)&charset=utf-8"
            return int(search(pattern, url)[1])
        
        # 所有章节的id
        chapter_ids = list(map(extract_cid, chapter_urls))
        
        # 查询已经存在的章节并过滤
        with Session(engine) as session:
            exists_chapter_ids = session.exec(select(Chapter.id).where(Chapter.book_id == book_id)).all()
        
        # 若所有章节已经存在则跳过
        if len(exists_chapter_ids) == len(chapter_ids):
            self.log(f"{book_id} 未更新章节", 20)
            return
        # 传递未下载的章节
        for serial, cid in enumerate(chapter_ids):
            if cid in exists_chapter_ids:
                continue
            self.log(f"<{book_id}> 新增章节: {titles[serial]} ", 20)
            yield scrapy.Request(
                url=f"https://dl.wenku8.com/packtxt.php?aid={book_id}&vid={cid}&charset=utf-8",
                callback=self.download_chapter,
                meta={
                    "title": titles[serial],
                    "bid": book_id,
                    "cid": cid,
                    "serial": serial
                },
            )
        
    def download_chapter(self, response):
        text = response.text
        book_id = response.meta["bid"]
        id = response.meta["cid"]
        serial = response.meta["serial"]
        title = response.meta["title"]
        self.log(f"<{book_id}> 章节<{id}>下载完成", 20)
        yield ChapterItem(
            id=id,
            book_id=book_id,
            serial=serial,
            title=title,
            content=text
        )
    def download_cover(self, response):
        content = response.body
        id = response.meta["id"]
        self.log(f"<{id}> 封面下载完成", 20)
        yield CoverItem(
            id=id,
            content=content
        )