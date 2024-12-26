from time import sleep

from wenku8.settings import DEFAULT_REQUEST_HEADERS
from wenku8.models import Book, engine
from sqlmodel import Session, select
import os
import requests
with Session(engine) as session:
    try:
        os.mkdir("download")
    except FileExistsError:
        pass
    results = session.exec(select(Book)).all()
    for result in results:
        string = f"https://dl.wenku8.com/down.php?type=utf8&node=2&id={result.query_id}"
        res = requests.get(string, headers=DEFAULT_REQUEST_HEADERS)
        with open(fr"download/{result.title}.txt", "wb") as f:
            f.write(res.content)
        sleep(2)