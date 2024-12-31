import scrapy

from wenku8.items import CoverItem, TextItem


class DownloadSpider(scrapy.Spider):
    name = "text"
    max_index = 2
    def start_requests(self):
        for i in range(1,self.max_index):
            text_url = f"https://dl.wenku8.com/down.php?type=utf8&node=1&id={i}"
            yield scrapy.Request(url=text_url, callback=self.parse_text, cb_kwargs={'id':i})
            self.log(f"text request of {i} send")

    def parse_text(self, response, id: int):
        yield TextItem(
            id=id,
            content=response.body
        )
