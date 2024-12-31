import logging

import scrapy

from wenku8.dependence import get_max_id_of_text
from wenku8.items import TextItem


class DownloadSpider(scrapy.Spider):
    name = "text"

    max_index = 3740  # current max id of wenku8, it will be automatically gen in the future version

    def start_requests(self):
        # download limit for the text
        # because text files are big files, which may cause much burden on the server
        # That's the reason why I give it a limit
        limit = 10
        start = get_max_id_of_text() + 1
        end = min(start + limit - 1, self.max_index) + 1
        for i in range(start, end):
            text_url = f"https://dl.wenku8.com/down.php?type=utf8&node=1&id={i}"
            yield scrapy.Request(url=text_url, callback=self.parse_text, cb_kwargs={'id': i})
            self.log(f"text request of {i} send", logging.INFO)

    def parse_text(self, response, id: int):
        self.log(f"text request of {id} received", logging.INFO)
        yield TextItem(
            id=id,
            content=response.body
        )
