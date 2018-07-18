import datetime

from shelvd import db


class Book(db.Model):

    isbn = db.Column(db.String(13), primary_key=True, index=True, unique=True)
    nickname = db.Column(db.String(100), nullable=False)
    page_count = db.Column(db.Integer, default=350)
    title = db.Column(db.String(200), default="Unknown")
    image_url = db.Column(db.String(500), nullable=True)
    last_action_date = db.Column(db.DateTime, default=datetime.datetime.now(),
        index=True)
    authors = db.relationship('Author', backref='book', lazy='dynamic')
    readings = db.relationship('Reading', backref='book', lazy='dynamic')

    def __repr__(self):
        return '<Book {0} ({1})>'.format(self.title[0:30], self.isbn)


class Author(db.Model):

    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    name = db.Column(db.String(150), nullable=False)
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

