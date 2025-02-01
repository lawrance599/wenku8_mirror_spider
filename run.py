import sys

from scrapy import cmdline

if __name__ == '__main__':
    spider = sys.argv[1]
    cmdline.execute(f'scrapy crawl {spider}'.split())