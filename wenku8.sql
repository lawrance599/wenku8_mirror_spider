CREATE DATABASE IF NOT EXISTS wenku8;
USE wenku8;
CREATE TABLE IF NOT EXISTS book(
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(512),
    writer VARCHAR(255),
    description VARCHAR(1024),
    last_updated DATETIME,
    words INT,
    status VARCHAR(255),
    has_cover BOOLEAN
); 

CREATE TABLE IF NOT EXISTS tag(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS booktaglink(
    book_pk INT,
    tag_pk int,
    PRIMARY KEY (book_pk, tag_pk),
    FOREIGN KEY (book_pk) REFERENCES book(id),
    FOREIGN KEY (tag_pk) REFERENCES tag(id)
);

CREATE TABLE IF NOT EXISTS cover(
    id INT PRIMARY KEY ,
    content BLOB
);

CREATE TABLE IF NOT EXISTS chapter(
    id INT PRIMARY KEY AUTO_INCREMENT,
    book_id INT,
    title VARCHAR(255),
    serial INT,
    content TEXT,
    FOREIGN KEY (book_id) REFERENCES book(id)
);

CREATE VIEW IF NOT EXISTS book_view AS
SELECT 
    book.id AS id,
    book.title AS title,
    book.status AS status,
    book.writer AS writer,
    COUNT(*) as chapter_count
FROM book
JOIN chapter ON book.id = chapter.book_id
GROUP BY book.id;