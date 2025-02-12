import os
from scrapy import cmdline as cmd
if __name__ == '__main__':
    print("爬虫列表：")
    os.system("scrapy list")
    spider = input("请输入爬虫名：").strip()
    os.system(f"nohup scrapy crawl {spider} > /dev/null & echo $! > run.pid")
    with open("run.pid") as f:
        pid = f.read()
    print(f"爬虫{spider}已启动， pid为{pid}")