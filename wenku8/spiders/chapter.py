
import scrapy


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

        yield scrapy.Request(
            url="https://www.wenku8.net/modules/article/packshow.php?id=3802&type=txt",
            callback=self.parse_book,
        )
    
    def parse_book(self, response):
        