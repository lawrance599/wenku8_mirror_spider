from time import sleep

import requests
from sqlmodel import Session, select
from settings import DOWNLOAD_PATH

from models import *
from wenku8.settings import DEFAULT_REQUEST_HEADERS

with Session(engine) as session:
    results = session.exec(select(Book).where(Book.download_url!="无版权")).all()
    for book in results:
        string = f"https://dl.wenku8.com/down.php?type=utf8&node=2&id={book.query_id}"
        res = requests.get(string, headers=DEFAULT_REQUEST_HEADERS)
        with open(fr"{DOWNLOAD_PATH}/{book.query_id}.txt", "wb") as f:
            f.write(res.content)
        sleep(5)
