import datetime

import factory
from amazon.api import AsinNotFound

from shelvd import models, messages


class BookFactory(factory.Factory):
    class Meta:
        model = models.Book

    isbn = factory.Sequence(lambda n: '9870000000000%d' % n)
    page_count = 350
    title = 'The King in Yellow'
    last_action_date = factory.LazyFunction(datetime.datetime.now)


class ReadingFactory(factory.Factory):
    class Meta:
        model = models.Reading

    id = factory.Sequence(lambda n: '10%d' % n)
    start_date = factory.LazyFunction(datetime.datetime.now)
    ended = False
    abandoned = False
    book_isbn = factory.SubFactory(BookFactory)


class AuthorFactory(factory.Factory):
    class Meta:
        model = models.Author

    id = factory.Sequence(lambda n: '%d' % n)
    name = "Jeff"


class FakeMessage(object):
    pass


def create_objects_for_message_testing(db):
    b1 = BookFactory(
        isbn="9780111111113",
        title="Necronomicon"
    )
    b2 = BookFactory(
            isbn="9780111111114",
            title="The King in Yellow",
            nickname="YKing"
        )
    r1 = ReadingFactory(
        book_isbn=b1.isbn,
        start_date=datetime.datetime(2017, 1, 1),
        end_date=datetime.datetime(2017, 1, 5),
        ended=True
    )
    a1 = AuthorFactory(
        id=1001,
        name="R. M. James"
    )
    db.session.add(b1)
    db.session.add(b2)
    db.session.add(r1)
    db.session.add(a1)
    db.session.commit()


def mock_amazon_lookup(*args, **kwargs):
    class MockBook(object):

        def __init__(self, title, pages, authors):
            self.title = title
            self.pages = pages
            self.authors = authors

    for key, value in kwargs.items():
        if key == "ItemId" and value == "9780241341629":
            return MockBook("Not Ghost Stories", 380,
                            ["R. M. James", "Ghost Author"])
        elif key == "ItemId" and value == "9780000000666":
            return MockBook("Especially Violent Fairytales", 620,
                            ["D. Grimmer", "T. Grimmer"])
        elif key == "ItemId" and value == "9780000000777":
            return MockBook("Mysterious Semi-known Book", 280, ["A. N. Author"])
        elif key == "ItemId" and value == "9780000000888":
            return MockBook("Mysterious Unknown Book", 260, [])
        elif key == "ItemId" and value == "0879111111111":
            raise AsinNotFound


class FakeAmazonException(Exception):
    pass


def create_objects_for_models_testing(db):
    b1 = BookFactory(
        isbn="9780111111113",
        title="Necronomicon"
    )
    b2 = BookFactory(
        isbn="9780111111114",
        title="The King in Yellow",
        nickname="YKing"
    )
    b3 = BookFactory(
            isbn="9780111111188",
            title="The Yellow Wallpaper"
    )
    r1 = ReadingFactory(
        book_isbn=b1.isbn,
        start_date=datetime.datetime(2017, 1, 1),
        end_date=datetime.datetime(2017, 1, 5),
        ended=True
    )
    r2 = ReadingFactory(
        book_isbn=b2.isbn,
        start_date=datetime.datetime(2017, 1, 1),
        ended=False
    )
    a1 = AuthorFactory(
        id=1001,
        name="R. M. James"
    )
    db.session.add(b1)
    db.session.add(b2)
    db.session.add(r1)
    db.session.add(r2)
    db.session.add(a1)
    db.session.commit()
