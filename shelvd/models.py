import datetime

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
        if message.isbn:
            existing_book = Book.query.filter_by(isbn=message.isbn).first()
            if existing_book:
                return existing_book
            else:
                book = Book()
                book.isbn = message.isbn
                db.session.add(book)
                db.session.commit()
                return book
        elif message.nickname:
            existing_book = Book.query.filter_by(
                nickname=message.nickname).first()
            if existing_book:
                return existing_book
            else:
                raise MessageException("This nickname doesn't match a book "
                    "that I know about already. Use an ISBN to start reading "
                    "a brand new book.")

    @classmethod
    def set_nickname(cls, message):
        existing_nickname = cls.query.filter_by(nickname=message.nickname).all()
        if not existing_nickname:
            book = cls.query.filter_by(isbn=message.isbn).first()
            book.nickname = message.nickname
            db.session.add(book)
            db.session.commit()
            return book
        else:
            raise MessageException("This nickname has already been used. "
                "Try another.")



class Author(db.Model):

    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    name = db.Column(db.String(150), default="Unknown")
    nationality = db.Column(db.String(100), default="Unknown")
    ethnicity = db.Column(db.String(100), default="Unknown")
    gender = db.Column(db.String(30), default="Unknown")
    books = db.Column(db.String(13), db.ForeignKey('book.isbn'))

    def __repr__(self):
        return '<Author {0} ({1})>'.format(self.name, self.id)


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
            return "Started reading {0}".format(book.title)

    @classmethod
    def end_reading(cls, message):
        book = Book.find_or_create(message)
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
            return "Finished reading {0}".format(book.title)
        else:
            raise MessageException("You're not currently reading this book."
                " You need to start reading this book before you finish it.")

class MessageException(Exception):
    pass  
