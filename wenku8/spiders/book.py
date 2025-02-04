import logging
import re
from datetime import date
from wenku8.items import *
from wenku8.models import Book
from wenku8.util import get_max_id_of


class WenkuSpider(scrapy.Spider):
    name = "book"
    # 每次向后爬取的次数
    limit = 3000

    def start_requests(self):
        root_url = "https://www.wenku8.net/book/"
        max_id = get_max_id_of(Book) if get_max_id_of(Book) is not None else 0
        for index in range(max_id + 1, max_id + self.limit + 1):
            yield scrapy.Request(
                root_url + str(index) + ".htm",
                callback=self.parse,
                cb_kwargs={"id": index},
            )

    def parse(self, response, id: int):
        res = self.re_first(response)
        title = res('//table[1]//span/b/text()')
        writer = res(
            '//table[1]//tr[2]/td[2]/text()',
            r"小说作者：((.*){1,})",
        )

        normal_desc = response.xpath('//div[@id="content"]//table[2]//tr/td[2]/span[6]/text()').extract_first()
        if normal_desc is None:
            description = response.xpath("//div[@id='content']//table[2]//tr/td[2]/span[4]/text()").extract_first()
        else:
            description = normal_desc
        
        last_updated = res(
            '//table[1]//tr[2]/td[4]/text()',
            r"最后更新：((.*){1,})",
        )
        last_updated = date.fromisoformat(last_updated) if last_updated is not None else None
        
        words = res(
            '//table[1]//tr[2]/td[5]/text()',
            r"全文长度：((.*){1,})字",
        )
        status = res(
            '//table[1]//tr[2]/td[3]/text()',
            r"文章状态：((.*){1,})",
        )
        tags = res(
            '//div[@id="content"]//table[2]//tr/td[2]/span[1]//text()',
            r"作品Tags：((.*){1,})",
        )
        if tags is None:
            self.log(f"book {title} has no tags", logging.WARNING)
        else:
            tags = tags.strip().split(" ")
        yield BookItem(
            id=id,
            title=title,
            writer=writer,
            description=description,
            last_updated=last_updated,
            words=words,
            status=status,
            tags=tags,
        )

    def re_first(self, res):
        res = res

        def inner(xpath: str, pattern: str = None):
            value = res.xpath(xpath).extract_first()
            if pattern is not None and value is not None:
                try:
                    return re.match(pattern, value).group(1) if value else None
                except AttributeError:
                    self.log(f"Pattern {pattern} cant match {value}", logging.ERROR)
            else:
                return value

        return inner
