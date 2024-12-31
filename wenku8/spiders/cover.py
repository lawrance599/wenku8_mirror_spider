import scrapy
from wenku8.items import CoverItem

class CoverSpider(scrapy.Spider):
    name = "cover"
    max_index = 10
    def start_requests(self):
        for i in range(1, self.max_index + 1):
            cover_url = f"http://img.wenku8.com/image/{int(i/1000)}/{i}/{i}s.jpg"
            self.log(f"cover request of {i} send")
            yield scrapy.Request(url=cover_url, callback=self.parse_cover, cb_kwargs={"id":i})

    def parse_cover(self, response, id: int):
        self.log(f"cover response of {id} ")
        yield CoverItem(
        id=id,
        content=response.body
    )

