import logging

import scrapy

from wenku8.items import CoverItem
from wenku8.models import get_miss_on_query_id_of, Cover


class CoverSpider(scrapy.Spider):
    name = "cover"

    def start_requests(self):
        targets = get_miss_on_query_id_of(Cover)
        for i in targets:
            cover_url = f"http://img.wenku8.com/image/{int(i / 1000)}/{i}/{i}s.jpg"
            self.log(f"cover request of {i} send", logging.INFO)
            yield scrapy.Request(url=cover_url, callback=self.parse_cover, cb_kwargs={"id": i})

    def parse_cover(self, response, id: int):
        self.log(f"cover request of {id} received", logging.INFO)
        yield CoverItem(
            id=id,
            content=response.body
        )
