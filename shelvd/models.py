import datetime
import os

from amazon.api import AmazonAPI, AsinNotFound

from shelvd import db


class Book(db.Model):

    isbn = db.Column(db.String(13), primary_key=True, index=True, unique=True)
    nickname = db.Column(db.String(100), nullable=True)
    page_count = db.Column(db.Integer, default=350)
    title = db.Column(db.String(200), default="Unknown")
    image_url = db.Column(db.String(500), nullable=True)
    last_action_date = db.Column(db.DateTime, default=datetime.datetime.now(),
                                 index=True)
    authors = db.relationship('Author', backref='book', lazy='dynamic')
    readings = db.relationship('Reading', backref='book', lazy='dynamic')

    def __repr__(self):
        return '<Book {0} ({1})>'.format(self.title[0:30], self.isbn)

    @classmethod
    def find_or_create(cls, message):
        book = Book.find(message)
        if not book:
            book = Book.create(message)
        return book

    @classmethod
    def create(cls, message):
        book = Book()
        book.isbn = message.isbn
        book.get_amazon_data()
        db.session.add(book)
        db.session.commit()
        return book

    @classmethod
    def find(cls, message):
        if message.isbn:
            return Book.query.filter_by(isbn=message.isbn).first()
        elif message.nickname:
            book = Book.query.filter_by(nickname=message.nickname).first()
            if not book:
                raise MessageException("This nickname doesn't match a book "
                    "that I know about already. Use an ISBN to start reading "
                    "a brand new book.")
            return book
        else:
            raise MessageException("I don't recognise this book. Please use "
                                   "the 13-digit ISBN.")

    def set_nickname(self, message):
        existing_nickname = Book.query.filter_by(nickname=message.nickname).all()
        if not existing_nickname:
            self.nickname = message.nickname
            db.session.add(self)
            db.session.commit()
            return "'{0}' (ISBN {1}) is now nicknamed '{2}'".format(
                    self.title, self.isbn, self.nickname)
        else:
            raise MessageException("This nickname has already been used. "
                                   "Try another.")

    def get_amazon_data(self):
        try:
            amazon_client = AmazonAPI(os.environ['AWS_ACCESS_KEY_ID'],
                                      os.environ['AWS_SECRET_ACCESS_KEY'],
                                      os.environ['AWS_ASSOCIATE_TAG'],
                                      region='UK')
            book_or_books = amazon_client.lookup(ItemId=self.isbn,
                                                 IdType='ISBN',
                                                 SearchIndex='Books')
            if type(book_or_books) is list:
                book = book_or_books[0]
            else:
                book = book_or_books
            self.title = book.title
            self.page_count = book.pages
            if hasattr(book, "large_image_url"):
                self.image_url = book.large_image_url
            elif hasattr(book, "medium_image_url"):
                self.image_url = book.medium_image_url
            self.authors = [author for author
                            in Author.create_from_amazon_data(book)]
        except AsinNotFound as e:
            pass


class Author(db.Model):

    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    name = db.Column(db.String(150), default="Unknown")
    nationality = db.Column(db.String(100), default="Unknown")
    ethnicity = db.Column(db.String(100), default="Unknown")
    gender = db.Column(db.String(30), default="Unknown")
    books = db.Column(db.String(13), db.ForeignKey('book.isbn'))

    def __repr__(self):
        return '<Author {0} ({1})>'.format(self.name, self.id)

    @classmethod
    def find_or_create(cls, name_or_id):
        if type(name_or_id) == int:
            author = Author.query.filter_by(id=name_or_id).first()
        else:
            author = Author.query.filter_by(name=name_or_id).first()
        if author:
            return author
        else:
            return Author(name=name_or_id)

    @classmethod
    def create_from_amazon_data(cls, amazon_book_object):
        authors = []
        for author_name in amazon_book_object.authors:
            author = Author.find_or_create(author_name)
            db.session.add(author)
            authors.append(author)
        db.session.commit()
        return authors


class Reading(db.Model):

    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    start_date = db.Column(db.DateTime, default=datetime.datetime.now())
    end_date = db.Column(db.DateTime, nullable=True)
    ended = db.Column(db.Boolean, default=False)
    abandoned = db.Column(db.Boolean, default=False)
    format = db.Column(db.String(100), nullable=True)
    rereading = db.Column(db.Boolean, default=False)
    book_isbn = db.Column(db.String(13), db.ForeignKey('book.isbn'))

    def __repr__(self):
        return '<Reading of {0} (id {1})>'.format(self.book, self.id)

    @classmethod
    def start_reading(cls, message):
        book = Book.find_or_create(message)
        existing_reading = Reading.query.filter_by(
            book_isbn=book.isbn).filter_by(ended=False).first()
        if existing_reading:
            raise MessageException("You've already started reading this book")
        else:
            reading = Reading()
            now = datetime.datetime.now()
            book.last_action_date = now
            reading.start_date = now

            reading.book_isbn = book.isbn
            db.session.add(reading)
            db.session.add(book)
            db.session.commit()
            return "Started reading {0} (ISBN {1})".format(book.title,
                                                           book.isbn)

    @classmethod
    def end_reading(cls, message):
        book = Book.find(message)
        if book:
            existing_reading = Reading.query.filter_by(
                book_isbn=book.isbn).filter_by(ended=False).first()
            if existing_reading:
                now = datetime.datetime.now()
                book.last_action_date = now
                existing_reading.end_date = now
                existing_reading.ended = True
                if message.terminator == "abandoned":
                    existing_reading.abandoned = True
                db.session.add(book)
                db.session.add(existing_reading)
                db.session.commit()
                return "Finished reading {0} (ISBN {1})".format(book.title,
                                                                book.isbn)
            else:
                raise MessageException("You're not currently reading this "
                    "book. You need to start reading this book before you "
                    "finish it.")
        else:
            raise MessageException("You're not currently reading this book. "
                "You need to start reading this book before you finish it.")


class MessageException(Exception):
    pass
