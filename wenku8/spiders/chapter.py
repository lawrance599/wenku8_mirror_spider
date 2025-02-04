import scrapy.linkextractors
from wenku8.models import engine, Book
import scrapy
from sqlmodel import Session, select
import re
from wenku8.items import ChapterItem
import sys

class ChapterSpider(scrapy.Spider):
    name="chapter"
    def start_requests(self):
        """
        发送登录请求。
        
        该方法使用Scrapy框架的FormRequest来发送一个登录请求。请求的URL是登录表单的提交地址，
        包含用户名、密码和其他登录所需的数据。登录成功后，将调用after_login方法处理响应。
        """
        yield scrapy.FormRequest(
            url="https://www.wenku8.net/login.php?do=submit",
            formdata={
                "username": "zlawrance",
                "password": "13767631251Fan!",
                "usecookie":"315360000",
                "action": "login",
                "submit": " 登  录 "
            },
            callback=self.after_login
        )
    def after_login(self, response):
        with Session(engine) as session:
            book_ids = session.exec(select(Book.query_id)).all()
        for book_id in book_ids:
            yield scrapy.Request(
            url=f"https://www.wenku8.net/modules/article/packshow.php?id={book_id}&type=txt",
            callback=self.parse_link,
        )
    
    def parse_link(self, response):
        """
        解析响应以获取章节链接和名称，并发起新的请求。
    
        :param response: Scrapy的响应对象，包含待解析的网页内容
        :type response: scrapy.http.Response
        """
        # 定义章节链接的正则表达式模式
        link_pattern: str = r"https://dl.wenku8.com/packtxt.php\?aid=([0-9]{1,})&vid=([0-9]{1,})&charset=utf-8"
        
        # 提取网页中所有<a>标签的href属性值，即原始链接列表
        raw_links: list = response.xpath('//a/@href').all()
        
        # 过滤并保留匹配link_pattern的链接，即章节链接
        chapter_links = filter(lambda x: re.match(link_pattern, x), raw_links)
        
        # 提取网页中所有章节名称，假设章节名称位于特定<td>标签内
        chapter_names = response.xpath("//td[@class='odd']/text()").all()
        
        # 遍历章节名称和链接，生成新的请求以下载章节内容
        try:
            for name, link in zip(chapter_names, chapter_links):
                # 从链接中提取书ID和章节ID
                book_id, chapter_id = extract_id(link, link_pattern)
                
                # 发起请求，传递额外的元数据用于后续处理
                yield scrapy.Request(
                    url=link,
                    callback=self.download_chapter,
                    meta={
                        "book_id": book_id,
                        "chapter_id": chapter_id,
                        "chapter_name": name
                    }
                )
        except ValueError:
            # 如果章节链接和名称的数量不匹配，记录错误并退出
            self.log("链接长度和章节名字不同", 50)
            sys.exit(1)

    def download_chapter(self, response):
        book_id = response.meta["book_id"]
        chapter_id = response.meta["chapter_id"]
        chapter_name = response.meta["chapter_name"]
        yield ChapterItem(
            book_id=book_id,
            id=chapter_id,
            title=chapter_name,
            content=response.body
        )
    
def extract_id(link: str, link_pattern: str):
        return re.match(link_pattern, link).groups(1), re.match(link_pattern, link).groups(2)