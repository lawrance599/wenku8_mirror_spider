import logging

import scrapy

from wenku8.dependence import get_max_id_of_cover
from wenku8.items import CoverItem


class CoverSpider(scrapy.Spider):
    name = "cover"
    max_index = 3740

    def start_requests(self):
        start = get_max_id_of_cover() + 1
        self.log(f"cover spider start at id:{start}", logging.INFO)
        for i in range(start, self.max_index + 1):
            cover_url = f"http://img.wenku8.com/image/{int(i / 1000)}/{i}/{i}s.jpg"
            self.log(f"cover request of {i} send", logging.INFO)
            yield scrapy.Request(url=cover_url, callback=self.parse_cover, cb_kwargs={"id": i})

    def parse_cover(self, response, id: int):
        self.log(f"cover request of {id} received", logging.INFO)
        yield CoverItem(
            id=id,
            content=response.body
        )
