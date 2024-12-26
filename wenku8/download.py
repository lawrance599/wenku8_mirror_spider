import subprocess as sp
from time import sleep

from sqlmodel import Session, select
from settings import DOWNLOAD_PATH

from models import *
with Session(engine) as session:
    results = session.exec(select(Book).where(Book.download_url!="无版权")).all()
    for book in results:
        if not book.download_url:
            continue
        sp.run(["curl", book.download_url.replace("txt", "utf8"), "-o", DOWNLOAD_PATH+book.title+".txt"])
        print(book.title)
        sleep(100)
