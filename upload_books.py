import csv
import datetime

from shelvd import db
from shelvd.models import Book, Author


# with open('books_test.csv', 'r') as inputfile:
with open('books.csv', 'r') as inputfile:
    for line in csv.reader(inputfile):
        book = Book()
        book.isbn = line[0]
        if line[1]:
            book.nickname = line[1]
        book.page_count = line[2]
        book.title = line[3]
        if line[4]:
            book.last_action_date = line[4]
            book.image_url = line[5]
            for author_id in line[6].split(","):
                author = Author.find_or_create(int(author_id)+10000)
                book.authors.append(author)
            db.session.add(book)
            db.session.commit()