import logging
import re

from wenku8.dependence import get_max_id_of_book
from wenku8.items import *


class WenkuSpider(scrapy.Spider):
    name = "book"
    max_index = 3740

    def start_requests(self):
        root_url = "https://www.wenku8.net/book/"
        cookie = {
            "Cookie": "jieqiUserCharset=utf-8;"
        }
        max_id = get_max_id_of_book()
        self.log(f"start from {max_id + 1}", logging.WARNING)
        for index in range(max_id + 1, self.max_index + 1):
            request = scrapy.Request(
                root_url + str(index) + ".htm",
                callback=self.parse,
                cb_kwargs={"query_id": index},
                cookies=cookie,
            )
            yield request

    def parse(self, response, query_id: int):
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
        last_chapter = res('//div[@id="content"]//table[2]//tr//span[4]/a/text()')
        last_updated = res(
            '//table[1]//tr[2]/td[4]/text()',
            r"最后更新：((.*){1,})",
        )
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
            query_id=query_id,
            title=title,
            writer=writer,
            description=description,
            last_chapter=last_chapter,
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
