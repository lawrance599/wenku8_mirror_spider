import logging

import scrapy

from wenku8.items import TextItem
from wenku8.models import get_miss_on_query_id_of, Text


class DownloadSpider(scrapy.Spider):
    name = "text"

    def start_requests(self):
        # download limit for the text
        # because text files are big files, which may cause much burden on the server
        # That's the reason why I give it a limit
        targets = get_miss_on_query_id_of(Text)
        for i in targets:
            text_url = f"https://dl.wenku8.com/down.php?type=utf8&node=1&id={i}"
            yield scrapy.Request(url=text_url, callback=self.parse_text, cb_kwargs={'id': i})
            self.log(f"text request of {i} send", logging.INFO)

    def parse_text(self, response, id: int):
        self.log(f"text request of {id} received", logging.INFO)
        yield TextItem(
            id=id,
            content=response.body
        )
