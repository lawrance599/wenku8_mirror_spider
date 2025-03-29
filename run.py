import os

if __name__ == "__main__":
    os.system("nohup scrapy crawl main > /dev/null & echo $! > run.pid")
    with open("run.pid") as f:
        pid = f.read()
    print(f"爬虫已启动， pid为{pid}")
